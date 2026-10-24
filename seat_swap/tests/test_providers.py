"""Live providers against fake clients: no key, no network, but the real extraction code runs."""

import json
from types import SimpleNamespace

from openai.types import Completion as OAICompletion
from openai.types.chat import ChatCompletion

from seat_swap.providers import OpenRouterChat, RawCompletions
from seat_swap.scripted import completion_text
from seat_swap.tests.test_logging import make_game, ramp_providers, read


class FakeCreate:
    def __init__(self, response):
        self.response, self.kwargs = response, []

    def __call__(self, **kwargs):
        self.kwargs.append(kwargs)
        return self.response(kwargs) if callable(self.response) else self.response


def openrouter_response(content):
    return ChatCompletion.model_validate({
        "id": "gen-1", "object": "chat.completion", "created": 0, "model": "qwen/qwen3-14b",
        "provider": "SomeBackend",
        "choices": [{"index": 0, "finish_reason": "stop",
                     "message": {"role": "assistant", "content": content, "reasoning": "secret thoughts"}}],
        "usage": {"prompt_tokens": 900, "completion_tokens": 120, "total_tokens": 1020, "cost": 0.0001,
                  "completion_tokens_details": {"reasoning_tokens": 80}},
    })


def fake_openrouter(thinking, create):
    p = object.__new__(OpenRouterChat)  # skip __init__: it loads compute.env and fetches the catalog
    p.provider, p.model, p.thinking = "openrouter", "qwen/qwen3-14b", thinking
    p._client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    return p


def test_openrouter_extracts_fields_separately():
    text = completion_text(1.8, 0, 1)
    create = FakeCreate(openrouter_response(text))
    p = fake_openrouter(True, create)
    sampling = {"temperature": 1.0, "max_tokens": 4096, "thinking": True, "seed": 123}
    c = p.complete([{"role": "user", "content": "hi"}], "<rendered>", sampling, {})
    assert c.text == text and "<think>" not in c.text
    assert c.reasoning == "secret thoughts" and c.finish_reason == "stop"
    assert c.served_provider == "SomeBackend"
    assert c.usage["cost"] == 0.0001 and c.usage["completion_tokens_details"]["reasoning_tokens"] == 80
    kw = create.kwargs[0]
    assert kw["extra_body"]["reasoning"] == {"enabled": True} and kw["seed"] == 123
    assert kw["messages"] == [{"role": "user", "content": "hi"}]


def test_openrouter_game_logs_messages_not_rendered(tmp_path):
    create = FakeCreate(openrouter_response(completion_text(1.8, 0, 1)))
    game, logger = make_game(tmp_path, [fake_openrouter(False, create), ramp_providers()[1]])
    assert game.run(1)["status"] == "completed"
    c = next(c for c in read(logger.dir / "calls.jsonl") if c["seat"] == 0)
    assert c["rendered_prompt"] is None and c["rendered_prompt_local"].startswith("<|im_start|>system")
    assert json.loads(c["messages"]) == create.kwargs[0]["messages"]
    assert create.kwargs[0]["extra_body"]["reasoning"] == {"enabled": False}
    assert c["reasoning_text"] == "secret thoughts" and c["served_provider"] == "SomeBackend"


def test_raw_completions_sends_exactly_the_logged_string(tmp_path):
    def respond(kwargs):
        return OAICompletion.model_validate({
            "id": "c1", "object": "text_completion", "created": 0, "model": "qwen3-14b",
            "choices": [{"index": 0, "text": completion_text(1.7, 0, 1), "finish_reason": "stop", "logprobs": None}],
            "usage": {"prompt_tokens": 900, "completion_tokens": 50, "total_tokens": 950},
        })

    create = FakeCreate(respond)
    p = RawCompletions("qwen3-14b", "http://fake.invalid/v1", "x", model_revision="abc123")
    p._client = SimpleNamespace(completions=SimpleNamespace(create=create))
    game, logger = make_game(tmp_path, [p, ramp_providers()[1]])
    assert game.run(1)["status"] == "completed"
    c = next(c for c in read(logger.dir / "calls.jsonl") if c["seat"] == 0)
    assert c["prompt_mode"] == "string" and c["model_revision"] == "abc123"
    assert create.kwargs[0]["prompt"] == c["rendered_prompt"] == c["rendered_prompt_local"]
    assert create.kwargs[0]["stop"] == ["<|im_end|>"]
    assert c["rendered_prompt"].endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n")


def test_raw_completions_pins_extra_sampling_and_logs_it(tmp_path):
    create = FakeCreate(lambda kw: OAICompletion.model_validate({
        "id": "c1", "object": "text_completion", "created": 0, "model": "m",
        "choices": [{"index": 0, "text": completion_text(1.7, 0, 1), "finish_reason": "stop", "logprobs": None}],
    }))
    p = RawCompletions("m", "http://fake.invalid/v1", "x", model_revision="abc123")
    p._client = SimpleNamespace(completions=SimpleNamespace(create=create))
    game, logger = make_game(tmp_path, [p, ramp_providers()[1]])
    assert game.run(1)["status"] == "completed"
    kw = create.kwargs[0]
    assert kw["top_p"] == 0.8 and kw["extra_body"] == {"top_k": 20, "add_special_tokens": False}
    c = next(c for c in read(logger.dir / "calls.jsonl") if c["seat"] == 0)
    sp = c["sampling_params"]
    assert (sp["top_p"], sp["top_k"], sp["add_special_tokens"]) == (0.8, 20, False)
    assert (sp["temperature"], sp["max_tokens"]) == (kw["temperature"], kw["max_tokens"])


def test_run_defaults_to_qwen_sampling_per_thinking_mode(tmp_path):
    from seat_swap import run
    from seat_swap.model_config import SAMPLING

    for mode, on in (("off", False), ("on", True)):
        run.main(["--dry-run", "--rounds", "1", "--thinking", mode, "--runs-root", str(tmp_path), "--run-id", mode])
        sp = read(tmp_path / mode / "calls.jsonl")[0]["sampling_params"]
        assert {k: sp[k] for k in ("temperature", "top_p", "top_k", "max_tokens")} == SAMPLING[on]
    assert SAMPLING[True]["max_tokens"] == 8192 and SAMPLING[False]["temperature"] == 0.7
