"""vLLM on Modal serving the seller model (seat_swap/model_config.py) behind an API key.

    uv run --project seat_swap modal run seat_swap/modal_weights.py          # fill the weights Volume (CPU)
    SEAT_SWAP_SCALEDOWN_MIN=10 uv run --project seat_swap modal deploy seat_swap/modal_vllm.py   # during a task
    uv run --project seat_swap modal deploy seat_swap/modal_vllm.py          # back to 2 min idle scaledown
    uv run --project seat_swap modal app stop -y seat-swap-vllm              # stop it

SEAT_SWAP_MODEL picks the model (model_config.BY_KEY; default 14b): app name, weights Volume, Secret
and model all follow it, e.g. SEAT_SWAP_MODEL=8b deploys `seat-swap-vllm-8b` (Kickoff 08).

The client (providers.RawCompletions) sends the locally rendered chat-template string to
/v1/completions, so the server never applies a template. The URL and key come from
compute.env (SEAT_SWAP_VLLM_URL, SEAT_SWAP_VLLM_KEY); the key reaches the server through the
Modal Secret `seat-swap-vllm` (VLLM_API_KEY).

`--generation-config vllm` stops vLLM from applying the model's generation_config.json defaults
(Qwen3: top_p 0.95, top_k 20) to every request: only the sampling params we send and log apply.
"""

import os

import modal

from seat_swap.model_config import BY_KEY

# read at deploy time and baked into the image env, so the container imports the same choice
MODEL_KEY = os.environ.get("SEAT_SWAP_MODEL", "14b")
SPEC = BY_KEY[MODEL_KEY]
MODEL_NAME, MODEL_REVISION = SPEC.name, SPEC.revision
APP_NAME = SPEC.app
GPU = "H100"  # run policy: one H100 (bf16 weights unchanged); ~3x the L40S decode speed
# idle scaledown, read at deploy time: 10 min during an active task, 2 min otherwise (run policy)
SCALEDOWN_MIN = int(os.environ.get("SEAT_SWAP_SCALEDOWN_MIN", "2"))
# a second container only if one is loaded past this many concurrent requests (8 games = 16)
TARGET_CONCURRENCY, MAX_CONTAINERS = 32, 2
VLLM_PORT = 8000
MAX_MODEL_LEN = 16384
MINUTES = 60

VLLM_VERSION = "0.21.0"
vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install(f"vllm=={VLLM_VERSION}", "huggingface_hub[hf_xet]")
    .env({"HF_XET_HIGH_PERFORMANCE": "1", "HF_HOME": "/root/.cache/huggingface", "SEAT_SWAP_MODEL": MODEL_KEY})
    .add_local_python_source("seat_swap")
)
hf_cache = modal.Volume.from_name(SPEC.volume, create_if_missing=True)
# compile cache: the 14B keeps its Volume; other models get their own
vllm_cache = modal.Volume.from_name("seat-swap-vllm-cache" if MODEL_KEY == "14b" else f"seat-swap-vllm-cache-{MODEL_KEY}",
                                    create_if_missing=True)
VOLUMES = {"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache}

app = modal.App(APP_NAME)


@app.server(
    image=vllm_image,
    gpu=GPU,
    volumes=VOLUMES,
    secrets=[modal.Secret.from_name(SPEC.secret)],
    port=VLLM_PORT,
    scaledown_window=SCALEDOWN_MIN * MINUTES,
    target_concurrency=TARGET_CONCURRENCY,
    max_containers=MAX_CONTAINERS,
    startup_timeout=15 * MINUTES,
    unauthenticated=True,  # Modal proxy open; vLLM itself checks VLLM_API_KEY on every /v1 request
)
class Server:
    @modal.enter()
    def start(self):
        import subprocess

        cmd = [
            "vllm", "serve", MODEL_NAME,
            "--revision", MODEL_REVISION,
            "--tokenizer-revision", MODEL_REVISION,
            "--served-model-name", MODEL_NAME,
            "--host", "0.0.0.0", "--port", str(VLLM_PORT),
            "--max-model-len", str(MAX_MODEL_LEN),
            "--generation-config", "vllm",
            "--uvicorn-log-level", "info",
        ]
        print(*cmd)
        self.process = subprocess.Popen(cmd)  # VLLM_API_KEY comes from the Secret's env

    @modal.exit()
    def stop(self):
        self.process.terminate()
