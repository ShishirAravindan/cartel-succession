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

from seat_swap.model_config import MODEL_NAME, MODEL_REVISION

TOKENIZER_MODEL = MODEL_NAME
TOKENIZER_REVISION = MODEL_REVISION


@lru_cache(maxsize=4)
def _tokenizer(model: str, revision: str):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(model, revision=revision)


def render(messages: list[dict], enable_thinking: bool, model: str = TOKENIZER_MODEL,
           revision: str = TOKENIZER_REVISION, **template_kwargs) -> str:
    """template_kwargs: model-specific chat-template options (gpt-oss: reasoning_effort)."""
    return _tokenizer(model, revision).apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=enable_thinking, **template_kwargs
    )


def messages_json(messages: list[dict]) -> str:
    return json.dumps(messages, ensure_ascii=False)


@lru_cache(maxsize=1)
def _harmony():
    import openai_harmony as oh

    return oh, oh.load_harmony_encoding(oh.HarmonyEncodingName.HARMONY_GPT_OSS)


def render_harmony(messages: list[dict], reasoning_effort: str, conversation_start_date: str) -> str:
    """gpt-oss prompt in OpenAI's harmony format, rendered by openai-harmony (the reference renderer).

    Our system prompt becomes the developer message's instructions (as in the HF chat template, whose
    output differs from harmony's only by a stray blank line after the instructions). The harmony
    system message carries the reasoning effort and a pinned date, so the prompt does not change
    across midnight."""
    oh, enc = _harmony()
    roles = {"user": oh.Role.USER, "assistant": oh.Role.ASSISTANT}
    conv = [oh.Message.from_role_and_content(oh.Role.SYSTEM, oh.SystemContent.new()
                                             .with_reasoning_effort(oh.ReasoningEffort(reasoning_effort.capitalize()))
                                             .with_conversation_start_date(conversation_start_date))]
    for m in messages:
        if m["role"] == "system":
            conv.append(oh.Message.from_role_and_content(oh.Role.DEVELOPER,
                                                         oh.DeveloperContent.new().with_instructions(m["content"])))
        else:
            conv.append(oh.Message.from_role_and_content(roles[m["role"]], m["content"]))
    ids = enc.render_conversation_for_completion(oh.Conversation.from_messages(conv), oh.Role.ASSISTANT)
    return enc.decode_utf8(ids)

