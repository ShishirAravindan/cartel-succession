"""Game loop: N seats, notes, strict parsing with one retry, call budget, shocks, logging.

A failed seat never gets a filled-in price: a second parse failure aborts the run, a call
budget that cannot cover the next round stops the run before it starts. In both cases the
env is not stepped and status.json records why.
"""

from __future__ import annotations

import hashlib
import random
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Optional

from harness.providers import FatalProviderError

from seat_swap import prompts
from seat_swap.logging import RunLogger, now
from seat_swap.metrics import A, A0, BETA, COST, MU, P_MONOPOLY, P_NASH
from seat_swap.prompts import NotesOligopoly, parse_response
from seat_swap.render import TOKENIZER_MODEL, TOKENIZER_REVISION, messages_json, render

# ints where upstream used ints: the prompt prints str(cost), so 1.0 would read "$1.0" instead of "$1"
MARKET = dict(a0=int(A0), ais=[int(A)] * 2, costs=[int(COST)] * 2, mu=MU, beta=BETA, alpha=1.0)
WINDOW = 100
PRIOR_STEPS = 1
ROUND_CONVENTION = (
    "round t >= 1 is the t-th LLM decision; synthetic warm-up near Nash is Round 0; the prompt for "
    "round t shows rounds up to t-1"
)
INHERITANCE = f"history = last {WINDOW} rounds of the price/profit table (prompt window); notes = PLANS + INSIGHTS"
FISH_CITATION = "Fish, Gonczarowski & Shorrer, arXiv:2404.00806v2, Appendix E"
TRANSPORT_RETRIES = 3


class StopRun(Exception):
    def __init__(self, status: str, detail: str):
        super().__init__(f"{status}: {detail}")
        self.status, self.detail = status, detail


@dataclass
class Seat:
    provider: object
    thinking: bool


def make_env(seed: int, notes_on: bool = True, window: int = WINDOW) -> NotesOligopoly:
    random.seed(seed)  # upstream warm-up jitter uses the global RNG
    env = NotesOligopoly(**MARKET, prefix="P0", window_size=window, notes_on=notes_on, prior_steps=PRIOR_STEPS)
    env.generate_history(PRIOR_STEPS)
    for got, want in ((env.lower_prices, P_NASH), (env.upper_prices, P_MONOPOLY)):
        assert all(abs(p - want) < 5e-4 for p in got), (got, want)
    return env


def restore_env(snapshot: dict, seed: int, notes_on: bool) -> NotesOligopoly:
    """Rebuild the env exactly as it was at a snapshot: every round, every seat's notes."""
    env = make_env(seed, notes_on=notes_on, window=snapshot["window"])
    assert env.prior_steps == snapshot["prior_steps"]
    env.history = {row["round"] + env.prior_steps: (list(row["prices"]), list(row["quantities"]), list(row["profits"]))
                   for row in snapshot["history"]}
    env.round = snapshot["env_round"]
    assert max(env.history) == env.round and env.display_round(env.round) == snapshot["round"]
    env.prior_actions = snapshot["prior_actions"]
    env.notes = [dict(n) for n in snapshot["notes"]]
    env.visible_from = list(snapshot.get("visible_from", [1] * env.nagents))
    return env


def template_hash() -> str:
    parts = [prompts.NOTES_FILES_INTRO, prompts.OUTPUT_INSTRUCTIONS_NOTES, prompts.OUTPUT_INSTRUCTIONS_PLAIN,
             prompts.P0_FILES_CLAUSE, prompts.SYSTEM_FORMAT_PLAIN, prompts.FILE_FENCE]
    return hashlib.sha256("\x00".join(parts).encode()).hexdigest()[:16]


def git_state() -> dict:
    def git(*a):
        return subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()

    # dirty = any tracked edit, or an uncommitted file inside this package (stray untracked files
    # elsewhere, e.g. scratch notes, don't make the recorded sha wrong)
    pkg = str(Path(__file__).resolve().parent)
    dirty = git("status", "--porcelain", "--untracked-files=no") or git("status", "--porcelain", "--", pkg)
    return {"sha": git("rev-parse", "HEAD"), "dirty": bool(dirty)}


def call_seed(seed: int, arm: str, rnd: int, seat: int, attempt: int) -> int:
    key = f"{seed}|{arm}|{rnd}|{seat}|{attempt}".encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:4], "big") >> 1


class Game:
    def __init__(self, env: NotesOligopoly, seats: list[Seat], logger: RunLogger, *, phase: str, arm: str,
                 seed: int, temperature: float, max_tokens: int, max_calls: Optional[int],
                 shocks: Optional[dict] = None, shock_calls_llm: Optional[bool] = None, parallel: bool = True):
        """shocks: {round: {seat: forced_price}}. Whether a forced seat's LLM is still called that
        round (and its notes updated) is part of the arm definition, so it must be stated."""
        if shocks and shock_calls_llm is None:
            raise ValueError("shocks given: set shock_calls_llm explicitly")
        self.env, self.seats, self.log = env, seats, logger
        self.phase, self.arm, self.seed = phase, arm, seed
        self.temperature, self.max_tokens = temperature, max_tokens
        self.max_calls, self.shocks, self.shock_calls_llm = max_calls, shocks or {}, shock_calls_llm
        self.parallel = parallel
        self.calls_made = self.parse_failures = self.transport_failures = 0
        self.rounds_done = 0
        self._lock = Lock()

    # ---- config / state -------------------------------------------------------------------------
    def config(self, extra: dict) -> dict:
        env = self.env
        return {
            "run_id": self.log.run_id, "phase": self.phase, "arm": self.arm, "seed": self.seed,
            "market": MARKET, "p_nash": env.lower_prices, "p_monopoly": env.upper_prices,
            "window": env.window_size, "inheritance": INHERITANCE, "round_convention": ROUND_CONVENTION,
            "prior_steps": env.prior_steps, "prior_actions": env.prior_actions, "notes_on": env.notes_on,
            "price_decimals": prompts.PRICE_DECIMALS,
            "prompt_prefix": env.prefixes, "prompt_template_sha": template_hash(), "prompt_source": FISH_CITATION,
            "seats": [{"seat": i, "provider": s.provider.name, "model": s.provider.model,
                       "model_revision": s.provider.model_revision, "prompt_mode": s.provider.prompt_mode,
                       "thinking": s.thinking} for i, s in enumerate(self.seats)],
            "temperature": self.temperature, "max_tokens": self.max_tokens, "max_calls": self.max_calls,
            "tokenizer_model": TOKENIZER_MODEL, "tokenizer_revision": TOKENIZER_REVISION,
            "git": git_state(), "created": now(), **extra,
        }

    def history_rows(self, seat: Optional[int] = None) -> list[dict]:
        """All rounds, or only those `seat` can see (a newcomer without history sees none before T).
        `forced` lists the seats whose price was forced that round (shocks in this game only)."""
        start = 1 if seat is None else self.env.visible_from[seat]
        rows = []
        for r, (p, d, pr) in sorted(self.env.history.items()):
            if r < start:
                continue
            t = self.env.display_round(r)
            rows.append({"round": t, "prices": p, "quantities": d, "profits": pr,
                         "forced": {str(k): v for k, v in self.shocks.get(t, {}).items()}})
        return rows

    def snapshot(self, t: int) -> None:
        self.log.snapshot(t, {
            "round": t, "env_round": self.env.round, "prior_steps": self.env.prior_steps,
            "prior_actions": self.env.prior_actions, "window": self.env.window_size,
            "history": self.history_rows(), "notes": [dict(n) for n in self.env.notes],
            "visible_from": list(self.env.visible_from),
        })

    # ---- one seat -------------------------------------------------------------------------------
    def _reserve_call(self) -> None:
        with self._lock:
            if self.max_calls is not None and self.calls_made >= self.max_calls:
                raise StopRun("stopped_max_calls", f"budget of {self.max_calls} calls used mid-round")
            self.calls_made += 1

    def _record(self, rnd, seat_idx, attempt, messages, rendered, sampling, comp, parsed, error) -> None:
        seat = self.seats[seat_idx]
        p = seat.provider
        self.log.call({
            "run_id": self.log.run_id, "phase": self.phase, "arm": self.arm, "seed": self.seed,
            "round": rnd, "seat": seat_idx, "attempt": attempt,
            "model": p.model, "model_revision": p.model_revision, "provider": p.name,
            "served_provider": comp.served_provider if comp else None,
            "prompt_mode": p.prompt_mode,
            "rendered_prompt": rendered if p.prompt_mode == "string" else None,
            "rendered_prompt_local": rendered, "tokenizer_revision": TOKENIZER_REVISION,
            "messages": messages_json(messages),
            "sampling_params": sampling,
            "raw_completion": comp.text if comp else None,
            "reasoning_text": comp.reasoning if comp else None,
            "finish_reason": comp.finish_reason if comp else None,
            "usage": comp.usage if comp else None,
            "latency_s": comp.latency_s if comp else None,
            "parsed_price": parsed.price if parsed and parsed.ok else None,
            "parse_ok": bool(parsed and parsed.ok),
            "parse_error": parsed.error if parsed and not parsed.ok else None,
            "parse_bracketed": bool(parsed and parsed.ok and parsed.bracketed),
            "notes_text": {"plans": parsed.plans, "insights": parsed.insights}
            if parsed and parsed.ok and self.env.notes_on else None,
            "error": error, "timestamp": now(),
        })

    def ask(self, rnd: int, seat_idx: int, messages: list[dict], rendered: str):
        seat = self.seats[seat_idx]
        ctx = {"seat": seat_idx, "round": rnd, "history": self.history_rows(seat_idx)}
        parse_tries = transport_tries = 0
        attempt = 0
        while True:
            self._reserve_call()
            sampling = {"temperature": self.temperature, "max_tokens": self.max_tokens, "thinking": seat.thinking,
                        "seed": call_seed(self.seed, self.arm, rnd, seat_idx, attempt),
                        **getattr(seat.provider, "fixed_sampling", {})}
            comp = parsed = None
            try:
                comp = seat.provider.complete(messages, rendered, sampling, ctx)
            except FatalProviderError as e:
                self._record(rnd, seat_idx, attempt, messages, rendered, sampling, None, None, repr(e))
                raise StopRun("aborted_fatal", str(e)) from e
            except Exception as e:  # noqa: BLE001  transport error: retry with backoff
                self._record(rnd, seat_idx, attempt, messages, rendered, sampling, None, None, repr(e))
                with self._lock:
                    self.transport_failures += 1
                transport_tries += 1
                if transport_tries > TRANSPORT_RETRIES:
                    raise StopRun("aborted_transport", f"round {rnd} seat {seat_idx}: {e!r}") from e
                time.sleep(min(2 ** transport_tries, 10))
                attempt += 1
                continue
            try:
                parsed = parse_response(comp.text, self.env.notes_on)
            except Exception as e:  # noqa: BLE001  never let parsing lose the raw line
                parsed = prompts.Parsed(ok=False, price=None, error=f"parser raised {e!r}")
            self._record(rnd, seat_idx, attempt, messages, rendered, sampling, comp, parsed, None)
            if parsed.ok:
                return parsed
            with self._lock:
                self.parse_failures += 1
            parse_tries += 1
            if parse_tries > 1:
                raise StopRun("aborted_parse", f"round {rnd} seat {seat_idx}: two unparseable responses")
            attempt += 1

    # ---- rounds ---------------------------------------------------------------------------------
    def play_round(self, rnd: int) -> None:
        forced = self.shocks.get(rnd, {})
        called = [i for i in range(len(self.seats)) if i not in forced or self.shock_calls_llm]
        if self.max_calls is not None and self.calls_made + len(called) > self.max_calls:
            raise StopRun("stopped_max_calls", f"{self.max_calls - self.calls_made} calls left, round {rnd} needs {len(called)}")
        msgs = {i: self.env.generate_prompt(i) for i in called}
        rendered = {i: render(msgs[i], enable_thinking=self.seats[i].thinking) for i in called}
        if self.parallel and len(called) > 1:
            with ThreadPoolExecutor(max_workers=len(called)) as ex:
                futs = {i: ex.submit(self.ask, rnd, i, msgs[i], rendered[i]) for i in called}
                results = {i: f.result() for i, f in futs.items()}
        else:
            results = {i: self.ask(rnd, i, msgs[i], rendered[i]) for i in called}

        prices = [forced[i] if i in forced else results[i].price for i in range(len(self.seats))]
        if self.env.notes_on:
            for i, parsed in results.items():
                self.env.notes[i] = {"plans": parsed.plans, "insights": parsed.insights}
        _, quantities, profits, _, _ = self.env.step(prices)
        self.log.round({
            "run_id": self.log.run_id, "phase": self.phase, "arm": self.arm, "seed": self.seed, "round": rnd,
            "prices": prices, "quantities": quantities, "profits": profits,
            "shock": bool(forced), "forced": {str(k): v for k, v in forced.items()},
        })
        self.rounds_done = rnd

    def run(self, rounds: int, snapshot_at=(), start: int = 1) -> dict:
        status = {"status": "completed", "detail": ""}
        try:
            for rnd in range(start, start + rounds):
                self.play_round(rnd)
                if rnd in snapshot_at:
                    self.snapshot(rnd)
        except StopRun as e:
            status = {"status": e.status, "detail": e.detail}
        status.update(rounds_completed=self.rounds_done, calls_made=self.calls_made,
                      parse_failures=self.parse_failures, transport_failures=self.transport_failures)
        self.log.status(status)
        return status
