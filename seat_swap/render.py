"""Local chat-template rendering with the pinned Qwen3-8B tokenizer.

On OpenRouter the server applies the template, so this string is our reconstruction
(logged as rendered_prompt_local). On a raw /v1/completions endpoint (Modal vLLM) this
exact string is what we send, so it is what the model saw.
"""

from __future__ import annotations

import json
from functools import lru_cache

QWEN3_8B = "Qwen/Qwen3-8B"
QWEN3_8B_REVISION = "b968826d9c46dd6066d109eabc6255188de91218"


@lru_cache(maxsize=4)
def _tokenizer(model: str, revision: str):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(model, revision=revision)


def render(messages: list[dict], enable_thinking: bool, model: str = QWEN3_8B,
           revision: str = QWEN3_8B_REVISION) -> str:
    return _tokenizer(model, revision).apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=enable_thinking
    )


def messages_json(messages: list[dict]) -> str:
    return json.dumps(messages, ensure_ascii=False)
