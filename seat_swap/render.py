"""Local chat-template rendering with the pinned tokenizer of the seller model (Qwen3-14B).

Qwen3-8B (the original design) was retired on OpenRouter on 2026-10-09; Qwen3-14B has the same
chat template and vocabulary (checked against Qwen3-8B @ b968826d), so renderings are identical.

On OpenRouter the server applies the template, so this string is our reconstruction
(logged as rendered_prompt_local). On a raw /v1/completions endpoint (Modal vLLM) this
exact string is what we send, so it is what the model saw.
"""

from __future__ import annotations

import json
from functools import lru_cache

TOKENIZER_MODEL = "Qwen/Qwen3-14B"
TOKENIZER_REVISION = "40c069824f4251a91eefaf281ebe4c544efd3e18"


@lru_cache(maxsize=4)
def _tokenizer(model: str, revision: str):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(model, revision=revision)


def render(messages: list[dict], enable_thinking: bool, model: str = TOKENIZER_MODEL,
           revision: str = TOKENIZER_REVISION) -> str:
    return _tokenizer(model, revision).apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=enable_thinking
    )


def messages_json(messages: list[dict]) -> str:
    return json.dumps(messages, ensure_ascii=False)
