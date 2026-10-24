import json
import logging as stdlib_logging
import sysconfig
from pathlib import Path

import pytest

from seat_swap.game import Game, Seat, make_env
from seat_swap.logging import CALL_FIELDS, ROUND_FIELDS, RunLogger
from seat_swap.providers import ScriptedProvider
from seat_swap.scripted import ramp_policy


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def make_game(tmp_path, providers, max_calls=None, run_id="t", **kw):
    env = make_env(seed=0)
    logger = RunLogger(tmp_path, run_id)
    kw = {"top_p": 0.8, "top_k": 20, **kw}
    game = Game(env, [Seat(p, thinking=False) for p in providers], logger, phase="test", arm="main",
                seed=0, temperature=1.0, max_tokens=4096, max_calls=max_calls, **kw)
    logger.config(game.config({}))
    return game, logger


def ramp_providers():
    policy = ramp_policy(1.473, 1.925)
    return [ScriptedProvider.from_price_policy("ramp", policy) for _ in range(2)]


def test_stdlib_logging_not_shadowed():
    stdlib = Path(sysconfig.get_paths()["stdlib"]).resolve()
    assert Path(stdlib_logging.__file__).resolve().is_relative_to(stdlib)


def test_five_dry_rounds_log_every_field(tmp_path):
    game, logger = make_game(tmp_path, ramp_providers())
    status = game.run(5, snapshot_at={5})
    assert status["status"] == "completed" and status["calls_made"] == 10 and status["parse_failures"] == 0

    calls = read(logger.dir / "calls.jsonl")
    assert len(calls) == 10
    for c in calls:
        assert all(k in c for k in CALL_FIELDS), set(CALL_FIELDS) - set(c)
        assert isinstance(c["rendered_prompt"], str) and c["rendered_prompt"].strip()
        assert c["rendered_prompt"] == c["rendered_prompt_local"]
        assert c["rendered_prompt"].startswith("<|im_start|>system")
        assert c["parse_ok"] and c["parsed_price"] is not None and c["notes_text"]["plans"]
        assert c["raw_completion"] and c["sampling_params"]["seed"] is not None
    assert {(c["round"], c["seat"]) for c in calls} == {(r, s) for r in range(1, 6) for s in (0, 1)}

    rounds = read(logger.dir / "rounds.jsonl")
    assert [r["round"] for r in rounds] == [1, 2, 3, 4, 5]
    for r in rounds:
        assert all(k in r for k in ROUND_FIELDS) and r["shock"] is False
    # logged price is the parsed price
    by_key = {(c["round"], c["seat"]): c["parsed_price"] for c in calls}
    assert all(r["prices"][s] == by_key[(r["round"], s)] for r in rounds for s in (0, 1))

    snap = json.loads((logger.dir / "snapshot_T5.json").read_text())
    assert [h["round"] for h in snap["history"]] == [0, 1, 2, 3, 4, 5]
    assert "[dry-run seat 1 round 5]" in snap["notes"][1]["plans"]
    cfg = json.loads((logger.dir / "config.json").read_text())
    assert cfg["window"] == 100 and cfg["prior_steps"] == 1 and cfg["tokenizer_revision"]


def test_round_prompt_carries_previous_notes(tmp_path):
    game, logger = make_game(tmp_path, ramp_providers())
    game.run(3)
    calls = read(logger.dir / "calls.jsonl")
    r3_seat1 = next(c for c in calls if c["round"] == 3 and c["seat"] == 1)
    assert "[dry-run seat 1 round 2] plan" in r3_seat1["rendered_prompt"]
    assert "[dry-run seat 0 round 2]" not in r3_seat1["rendered_prompt"]


def test_max_calls_stops_cleanly(tmp_path):
    game, logger = make_game(tmp_path, ramp_providers(), max_calls=3)
    status = game.run(5)
    assert status["status"] == "stopped_max_calls" and status["rounds_completed"] == 1
    assert len(read(logger.dir / "calls.jsonl")) <= 3
    assert len(read(logger.dir / "rounds.jsonl")) == 1
    assert game.env.round == 2  # warm-up + round 1, env not stepped for the stopped round


def test_unparseable_twice_aborts_without_price(tmp_path):
    good = ramp_providers()[0]
    junk = ScriptedProvider("junk", lambda ctx: "I would go with about $1.80")
    game, logger = make_game(tmp_path, [good, junk], parallel=False)
    status = game.run(3)
    assert status["status"] == "aborted_parse" and status["rounds_completed"] == 0
    assert status["parse_failures"] == 2
    junk_calls = [c for c in read(logger.dir / "calls.jsonl") if c["seat"] == 1]
    assert len(junk_calls) == 2 and not any(c["parse_ok"] for c in junk_calls)
    assert all(c["parsed_price"] is None and c["raw_completion"] for c in junk_calls)
    assert junk_calls[0]["sampling_params"]["seed"] != junk_calls[1]["sampling_params"]["seed"]
    assert not (logger.dir / "rounds.jsonl").exists()


def test_retry_rescue_counts_failure(tmp_path):
    state = {"n": 0}
    good_text = ramp_providers()[0].respond

    def flaky(ctx):
        state["n"] += 1
        return "garbage" if state["n"] == 1 else good_text(ctx)

    game, _ = make_game(tmp_path, [ramp_providers()[0], ScriptedProvider("flaky", flaky)])
    status = game.run(2)
    assert status["status"] == "completed" and status["parse_failures"] == 1 and status["calls_made"] == 5


def test_run_dir_never_overwritten(tmp_path):
    RunLogger(tmp_path, "same")
    with pytest.raises(FileExistsError):
        RunLogger(tmp_path, "same")


def test_shock_forces_price_and_requires_policy(tmp_path):
    with pytest.raises(ValueError):
        make_game(tmp_path, ramp_providers(), run_id="a", shocks={2: {0: 1.473}})
    game, logger = make_game(tmp_path, ramp_providers(), run_id="b", shocks={2: {0: 1.473}}, shock_calls_llm=False)
    game.run(3)
    rounds = read(logger.dir / "rounds.jsonl")
    assert rounds[1]["shock"] and rounds[1]["prices"][0] == 1.473
    assert not any(c["round"] == 2 and c["seat"] == 0 for c in read(logger.dir / "calls.jsonl"))
