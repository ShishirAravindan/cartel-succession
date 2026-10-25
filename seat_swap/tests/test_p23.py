"""Kickoff 08: different-model newcomers. Seat routing, sampling, rendering and parsing, no API calls."""

import json
from pathlib import Path

import pytest

from seat_swap import run
from seat_swap.branch import SELLER_MODELS, run_branch
from seat_swap.model_config import MODEL_NAME, MODELS
from seat_swap.prompts import INSTRUCTED_COLLUDE_FORGIVE as RULE
from seat_swap.prompts import markdown_clean, parse_response, price_candidates
from seat_swap.providers import Completion, RawCompletions, harmony_split
from seat_swap.render import _tokenizer, render
from seat_swap.scripted import completion_text
from seat_swap.tests.test_logging import read

T = 12
URLS = {spec.env: f"http://{spec.key}.fake.invalid" for spec in MODELS.values()}


@pytest.fixture
def endpoints(monkeypatch):
    """Fake endpoints per model; every call records (model, base_url, rendered, sampling)."""
    for env, url in URLS.items():
        monkeypatch.setenv(f"{env}_URL", url)
        monkeypatch.setenv(f"{env}_KEY", "k")
    seen = []

    def complete(self, messages, rendered, sampling, ctx):
        seen.append({"model": self.model, "url": self.base_url, "rendered": rendered, "sampling": sampling,
                     "seat": ctx["seat"]})
        body = completion_text(1.92, ctx["seat"], ctx["round"])
        if self.fmt == "harmony":  # a decoy template with another price in the reasoning
            text = (f"<|channel|>analysis<|message|>Draft:\n{completion_text(1.11, 9, 9)}<|end|>"
                    f"<|start|>assistant<|channel|>final<|message|>{body}")
            answer, reasoning = harmony_split(text)
            return Completion(text=text, reasoning=reasoning, answer=answer, finish_reason="stop")
        return Completion(text=f"<think>\n{completion_text(1.11, 9, 9)}\n</think>\n\n{body}", finish_reason="stop")

    monkeypatch.setattr(RawCompletions, "complete", complete)
    return seen


def planted_parent(tmp_path):
    """A dry 14B-vllm parent: live branches then build vllm providers from its config."""
    run.main(["--dry-run", "--rounds", str(T), "--instruction", "forgive", "--warmup", "cartel", "--thinking", "on",
              "--runs-root", str(tmp_path), "--run-id", "parent"])
    d = tmp_path / "parent"
    cfg = json.loads((d / "config.json").read_text())
    for s in cfg["seats"]:
        s.update(provider="vllm", model=MODEL_NAME)
    (d / "config.json").write_text(json.dumps(cfg))
    return d


@pytest.mark.parametrize("arm", ["sib_history", "sib_full", "oth_history", "oth_full"])
def test_each_seat_goes_to_its_model_and_endpoint(tmp_path, endpoints, arm):
    p = planted_parent(tmp_path)
    d, s = run_branch(p, T, arm, dry_run=False, max_calls=20, runs_root=tmp_path, allow_dirty=True,
                      rounds=4, shock_offset=3)
    assert s["status"] == "completed", s
    newcomer = MODELS[SELLER_MODELS[arm.split("_")[0]]]
    for c in endpoints:
        spec = MODELS[MODEL_NAME] if c["seat"] == 0 else newcomer
        assert c["model"] == spec.name and c["url"] == URLS[spec.env] + "/v1"
        assert (RULE in c["rendered"]) == (c["seat"] == 0)  # only the incumbent is instructed
        for k in ("temperature", "top_p", "top_k", "max_tokens"):
            assert c["sampling"][k] == spec.sampling[k], (c["seat"], k)
    assert {c["seat"] for c in endpoints} == {0, 1}
    if newcomer.fmt == "harmony":
        assert all(c["rendered"].startswith("<|start|>system") and "Reasoning: medium" in c["rendered"]
                   for c in endpoints if c["seat"] == 1)
    cfg = json.loads((d / "config.json").read_text())
    assert cfg["instructions"][1] is None and cfg["instructions"][0] == RULE
    assert [x["model"] for x in cfg["seats"]] == [MODEL_NAME, newcomer.name]
    assert cfg["seats"][1]["model_revision"] == newcomer.revision
    calls = read(d / "calls.jsonl")
    assert all(c["parsed_price"] == 1.92 for c in calls)  # the answer's price, never the reasoning's 1.11
    assert all(c["tokenizer_revision"] == MODELS[c["model"]].revision for c in calls)


def test_sibling_render_is_the_tokenizers_own_template():
    spec = MODELS["Qwen/Qwen3-8B"]
    msgs = [{"role": "system", "content": "SYS\nline"}, {"role": "user", "content": "USER $1.92"}]
    ours = RawCompletions(spec.name, "http://x.invalid/v1", "k", spec.revision).render(msgs, thinking=True)
    theirs = _tokenizer(spec.name, spec.revision).apply_chat_template(
        msgs, tokenize=False, add_generation_prompt=True, enable_thinking=True)
    assert ours == theirs == render(msgs, enable_thinking=True)  # and exactly like the 14B


def test_harmony_render_is_openai_harmonys_own_format():
    """gpt-oss: our string tokenizes (HF tokenizer, as vLLM does) to exactly openai-harmony's token ids,
    and differs from the HF chat template only by its stray blank line after the developer instructions."""
    import openai_harmony as oh
    spec = MODELS["openai/gpt-oss-20b"]
    msgs = [{"role": "system", "content": "SYS\nline"}, {"role": "user", "content": "USER $1.92"}]
    ours = RawCompletions(spec.name, "http://x.invalid/v1", "k", spec.revision).render(msgs, thinking=True)
    enc = oh.load_harmony_encoding(oh.HarmonyEncodingName.HARMONY_GPT_OSS)
    conv = oh.Conversation.from_messages([
        oh.Message.from_role_and_content(oh.Role.SYSTEM, oh.SystemContent.new()
                                         .with_reasoning_effort(oh.ReasoningEffort.MEDIUM)
                                         .with_conversation_start_date("2026-10-24")),
        oh.Message.from_role_and_content(oh.Role.DEVELOPER, oh.DeveloperContent.new().with_instructions(msgs[0]["content"])),
        oh.Message.from_role_and_content(oh.Role.USER, msgs[1]["content"]),
    ])
    ids = list(enc.render_conversation_for_completion(conv, oh.Role.ASSISTANT))
    tok = _tokenizer(spec.name, spec.revision)
    assert tok.encode(ours, add_special_tokens=False) == ids and tok.decode(ids) == ours
    assert "Reasoning: medium" in ours and "Current date: 2026-10-24" in ours and ours.endswith("<|start|>assistant")
    hf = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, reasoning_effort="medium")
    hf = hf.replace(hf.split("Current date: ")[1][:10], "2026-10-24")
    assert hf.replace("SYS\nline\n\n<|end|>", "SYS\nline<|end|>") == ours


def test_harmony_answer_is_the_final_channel_only():
    body = completion_text(1.85, 1, 5)
    text = (f"<|channel|>analysis<|message|>{completion_text(1.20, 1, 5)}<|end|>"
            f"<|start|>assistant<|channel|>final<|message|>{body}<|return|>")
    answer, reasoning = harmony_split(text)
    assert answer == body and "1.20" in reasoning
    assert parse_response(answer).price == 1.85
    # no final channel (cut off mid-reasoning): an empty answer, which fails to parse
    answer, reasoning = harmony_split(f"<|channel|>analysis<|message|>{completion_text(1.20, 1, 5)}")
    assert answer == "" and not parse_response(answer).ok


def test_qwen_answer_skips_the_think_block():
    text = f"<think>\n{completion_text(1.20, 1, 5)}\n</think>\n\n{completion_text(1.85, 1, 5)}"
    assert parse_response(text).price == 1.85


# ---- PI decisions on status_p23 (Kickoff 08): markdown normalisation for gpt-oss, 3 retries for P2/P3 newcomers

FAILURES = Path(__file__).parent / "data" / "p23_gptoss_failures.jsonl"
# (run id suffix, round, attempt) -> price recovered after markdown_clean; the other 7 of the 33 stay failures:
# a header without its colon ("**My chosen price**", "New content for PLANS.txt") or a blank line after the price header
RECOVERED = {
    ("cfbd8e", 154, 0): 1.92, ("3f7fbb", 156, 0): 1.92, ("329b15", 155, 1): 1.88, ("3ed0e3", 151, 0): 1.92,
    ("e8dd4b", 156, 0): 1.90, ("a59867", 156, 0): 1.92, ("a59867", 156, 1): 1.92, ("8729d6", 152, 0): 1.95,
    ("18de2a", 153, 0): 1.85, ("c2bff0", 152, 1): 1.92, ("f8c7ef", 154, 0): 1.65, ("7d73d5", 154, 0): 1.80,
    ("7d73d5", 154, 1): 1.80, ("125574", 153, 0): 1.70, ("eaf25c", 152, 0): 2.00, ("eaf25c", 155, 0): 1.50,
    ("eaf25c", 155, 1): 1.50, ("87e257", 153, 0): 1.90, ("87e257", 154, 0): 1.90, ("87e257", 155, 0): 1.90,
    ("07c0a1", 153, 0): 1.66, ("54649e", 155, 0): 1.44, ("54649e", 155, 1): 1.47, ("917053", 152, 0): 1.92,
    ("917053", 157, 0): 1.92, ("e2abc9", 154, 0): 1.92,
}


def test_replay_of_the_33_logged_gptoss_failures():
    rows = [json.loads(line) for line in FAILURES.read_text().splitlines()]
    assert len(rows) == 33
    got = {}
    for r in rows:
        assert not parse_response(r["answer"]).ok  # strict alone still rejects every one
        p = parse_response(r["answer"], markdown=True)
        if p.ok:
            got[(r["run_id"][-6:], r["round"], r["attempt"])] = p.price
            assert p.markdown and price_candidates(markdown_clean(r["answer"])) and \
                len(price_candidates(markdown_clean(r["answer"]))) == 1
            assert float(price_candidates(markdown_clean(r["answer"]))[0]) == pytest.approx(p.price)
    assert got == pytest.approx(RECOVERED)


def test_markdown_clean_limits():
    body = completion_text(1.85, 1, 5)
    fenced = body.replace("My chosen price:\n1.85", "**My chosen price:**\n```\n1.85\n```")
    assert parse_response(fenced, markdown=True).price == 1.85
    assert not parse_response(fenced).ok  # off unless asked (Qwen seats)
    two = body.replace("My chosen price:\n1.85", "**My chosen price:**\n`1.85` or `1.90`")
    p = parse_response(two, markdown=True)
    assert not p.ok and "2 price candidates" in p.error  # exactly one candidate, or a failure
    no_colon = body.replace("My chosen price:\n1.85", "**My chosen price**\n1.85")
    assert not parse_response(no_colon, markdown=True).ok  # formatting only: a missing colon is not fixed


class Flaky:
    """Scripted seller: the first `bad` answers of each round are unparseable."""
    name, prompt_mode, model_revision, model = "scripted", "string", None, "scripted:flaky"

    def __init__(self, bad):
        self.bad, self.seen = bad, {}

    def complete(self, messages, rendered, sampling, ctx):
        n = self.seen[ctx["round"]] = self.seen.get(ctx["round"], 0) + 1
        text = "<fill in here>" if n <= self.bad else completion_text(1.92, ctx["seat"], ctx["round"])
        return Completion(text=text, finish_reason="stop")


@pytest.mark.parametrize("retries,bad,status", [(3, 3, "completed"), (3, 4, "aborted_parse"), (1, 2, "aborted_parse"),
                                                (1, 1, "completed")])
def test_parse_retries_per_seat(tmp_path, retries, bad, status):
    from seat_swap.game import Game, Seat, make_env
    from seat_swap.logging import RunLogger
    env = make_env(seed=0, notes_on=True)
    logger = RunLogger(tmp_path, "r")
    game = Game(env, [Seat(Flaky(0), False), Seat(Flaky(bad), False, retries)], logger, phase="t", arm="t", seed=0,
                temperature=1.0, max_tokens=10, max_calls=None)
    st = game.run(2)
    assert st["status"] == status
    calls = [c for c in read(tmp_path / "r" / "calls.jsonl") if c["seat"] == 1 and c["round"] == 1]
    assert len(calls) == (bad + 1 if status == "completed" else retries + 1)  # every attempt is logged
    assert len({c["rendered_prompt"] for c in calls}) == 1 and len({c["sampling_params"]["seed"] for c in calls}) == len(calls)


@pytest.mark.parametrize("arm,retries", [("sib_history", 3), ("sib_full", 3), ("oth_history", 3), ("oth_full", 3),
                                         ("same_full", 1), ("control", 1)])
def test_only_p23_newcomers_get_three_retries(tmp_path, arm, retries):
    p = planted_parent(tmp_path)
    d, _ = run_branch(p, T, arm, dry_run=True, max_calls=None, runs_root=tmp_path, rounds=2, shock_offset=1)
    seats = json.loads((d / "config.json").read_text())["seats"]
    assert [s["parse_retries"] for s in seats] == [1, retries]
