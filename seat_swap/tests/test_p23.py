"""Kickoff 08: different-model newcomers. Seat routing, sampling, rendering and parsing, no API calls."""

import json

import pytest

from seat_swap import run
from seat_swap.branch import SELLER_MODELS, run_branch
from seat_swap.model_config import MODEL_NAME, MODELS
from seat_swap.prompts import INSTRUCTED_COLLUDE_FORGIVE as RULE
from seat_swap.prompts import parse_response
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
