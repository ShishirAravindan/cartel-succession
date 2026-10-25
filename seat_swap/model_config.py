"""The seller models: one place for each name, pinned revision, Modal app and sampling.

Used by the local chat-template renderer (render.py), the providers (providers.py) and the Modal
vLLM server (modal_vllm.py, modal_weights.py), so the string we render and the weights that run
it always agree. MODEL_NAME / MODEL_REVISION / SAMPLING stay the 14B incumbent's (the defaults
everywhere). Kickoff 08 adds the P2 / P3 newcomers, one Modal app, Volume and Secret each.
"""

from dataclasses import dataclass, field

MODEL_NAME = "Qwen/Qwen3-14B"
MODEL_REVISION = "40c069824f4251a91eefaf281ebe4c544efd3e18"

# Qwen's recommended sampling per thinking mode (user decision 2026-10-24); keyed by thinking on/off
SAMPLING = {
    False: {"temperature": 0.7, "top_p": 0.8, "top_k": 20, "max_tokens": 4096},
    True: {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "max_tokens": 8192},
}


@dataclass(frozen=True)
class ModelSpec:
    key: str                 # SEAT_SWAP_MODEL value for the Modal deploy
    name: str
    revision: str
    app: str                 # Modal app
    volume: str              # weights Volume
    secret: str              # Modal Secret holding VLLM_API_KEY
    env: str                 # compute.env prefix: <env>_URL, <env>_KEY
    fmt: str                 # "qwen3" (<think> block) or "harmony" (gpt-oss channels)
    sampling: dict           # thinking-on sampling sent with every call of this model
    template_kwargs: dict = field(default_factory=dict)  # extra apply_chat_template kwargs


MODELS = {m.name: m for m in [
    ModelSpec("14b", MODEL_NAME, MODEL_REVISION, "seat-swap-vllm", "seat-swap-hf-cache", "seat-swap-vllm",
              "SEAT_SWAP_VLLM", "qwen3", SAMPLING[True]),
    # P2 sibling: same chat template and vocabulary as 14B; Qwen's thinking-mode sampling
    ModelSpec("8b", "Qwen/Qwen3-8B", "b968826d9c46dd6066d109eabc6255188de91218", "seat-swap-vllm-8b",
              "seat-swap-hf-cache-8b", "seat-swap-vllm-8b", "SEAT_SWAP_VLLM_8B", "qwen3", SAMPLING[True]),
    # P3 other family: OpenAI's recommended sampling for gpt-oss (temperature 1.0, top_p 1.0, no top-k;
    # top_k 0 = off in vLLM), reasoning effort "medium" and a pinned date in the harmony system message;
    # rendered with openai-harmony (render.render_harmony), not the HF chat template
    ModelSpec("oth", "openai/gpt-oss-20b", "6cee5e81ee83917806bbde320786a8fb61efebee", "seat-swap-vllm-oth",
              "seat-swap-hf-cache-oth", "seat-swap-vllm-oth", "SEAT_SWAP_VLLM_OTH", "harmony",
              {"temperature": 1.0, "top_p": 1.0, "top_k": 0, "max_tokens": 8192},
              {"reasoning_effort": "medium", "conversation_start_date": "2026-10-24"}),
]}
BY_KEY = {m.key: m for m in MODELS.values()}
