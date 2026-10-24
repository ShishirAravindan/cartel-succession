"""Model providers with one interface for the game loop.

prompt_mode tells the logger what the model actually received:
  "messages" - chat endpoint (OpenRouter); the server applies the chat template, so the exact
               string is unknown and rendered_prompt is null (rendered_prompt_local is ours).
  "string"   - the rendered string itself is sent (vLLM /v1/completions, scripted sellers), so
               rendered_prompt is exactly what the model saw.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Optional

from harness.providers import ChatProvider, FatalProviderError
from poseidon_compute import endpoint_kind

from seat_swap.scripted import completion_text

QWEN3_STOP = ["<|im_end|>"]


@dataclass
class Completion:
    text: str  # content verbatim (no reasoning folded in)
    reasoning: Optional[str] = None
    finish_reason: Optional[str] = None
    usage: Optional[dict] = None
    served_provider: Optional[str] = None
    latency_s: float = 0.0


class OpenRouterChat(ChatProvider):
    """Upstream ChatProvider (client + model resolution), but returns the raw pieces separately."""

    name = "openrouter"
    prompt_mode = "messages"
    model_revision = None  # OpenRouter does not expose weights revisions

    def __init__(self, model: str, temperature: float, max_tokens: int, thinking: bool):
        if endpoint_kind() != "openrouter":
            raise FatalProviderError(f"expected the OpenRouter endpoint, compute.env selects {endpoint_kind()!r}")
        super().__init__(model, temperature, max_tokens, reasoning=thinking)
        if self.model != model:
            raise FatalProviderError(f"requested {model!r} but resolved to {self.model!r} (LLM_MODEL set?)")
        self.thinking = thinking
        # SDK-internal retries would bypass --max-calls and the call log; the game loop retries instead
        self._client = self._client.with_options(max_retries=0)

    def complete(self, messages, rendered, sampling, ctx) -> Completion:
        from openai import AuthenticationError, BadRequestError, NotFoundError, PermissionDeniedError

        start = time.time()
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=sampling["temperature"],
                max_tokens=sampling["max_tokens"],
                seed=sampling["seed"],
                extra_body={"reasoning": {"enabled": sampling["thinking"]}, "usage": {"include": True}},
            )
        except (NotFoundError, AuthenticationError, PermissionDeniedError, BadRequestError) as e:
            raise FatalProviderError(f"{self.spec}: {e}") from e
        raw = resp.model_dump()
        if not raw.get("choices"):
            raise RuntimeError(f"{self.spec}: empty response ({raw.get('error')})")
        choice = raw["choices"][0]
        msg = choice.get("message") or {}
        return Completion(
            text=msg.get("content") or "",
            reasoning=msg.get("reasoning"),
            finish_reason=choice.get("finish_reason"),
            usage=raw.get("usage"),
            served_provider=raw.get("provider"),
            latency_s=round(time.time() - start, 3),
        )


class RawCompletions:
    """OpenAI-compatible /v1/completions (Modal vLLM): sends the locally rendered string."""

    name = "vllm"
    prompt_mode = "string"

    def __init__(self, model: str, base_url: str, api_key: str, model_revision: str):
        from openai import OpenAI

        self.model = model
        self.model_revision = model_revision
        self._client = OpenAI(base_url=base_url, api_key=api_key or "EMPTY", max_retries=0)

    def complete(self, messages, rendered, sampling, ctx) -> Completion:
        start = time.time()
        resp = self._client.completions.create(
            model=self.model,
            prompt=rendered,
            temperature=sampling["temperature"],
            max_tokens=sampling["max_tokens"],
            seed=sampling["seed"],
            stop=QWEN3_STOP,
        )
        raw = resp.model_dump()
        choice = raw["choices"][0]
        return Completion(
            text=choice.get("text") or "",
            finish_reason=choice.get("finish_reason"),
            usage=raw.get("usage"),
            served_provider="vllm",
            latency_s=round(time.time() - start, 3),
        )


class ScriptedProvider:
    """Zero-API seller. `respond(ctx) -> str` produces the completion text."""

    name = "scripted"
    prompt_mode = "string"
    model_revision = None

    def __init__(self, label: str, respond: Callable[[dict], str]):
        self.model = f"scripted:{label}"
        self.respond = respond

    @classmethod
    def from_price_policy(cls, label: str, policy, notes_on: bool = True) -> "ScriptedProvider":
        return cls(label, lambda ctx: completion_text(
            policy(ctx["seat"], ctx["round"], ctx["history"]), ctx["seat"], ctx["round"], notes_on
        ))

    def complete(self, messages, rendered, sampling, ctx) -> Completion:
        return Completion(text=self.respond(ctx), finish_reason="stop", served_provider="scripted")
