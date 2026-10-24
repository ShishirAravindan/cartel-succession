"""vLLM on Modal serving the seller model (seat_swap/model_config.py) behind an API key.

    uv run --project seat_swap modal run seat_swap/modal_vllm.py::download   # fill the weights Volume (CPU)
    uv run --project seat_swap modal deploy seat_swap/modal_vllm.py          # deploy the server
    uv run --project seat_swap modal app stop seat-swap-vllm                 # stop it

The client (providers.RawCompletions) sends the locally rendered chat-template string to
/v1/completions, so the server never applies a template. The URL and key come from
compute.env (SEAT_SWAP_VLLM_URL, SEAT_SWAP_VLLM_KEY); the key reaches the server through the
Modal Secret `seat-swap-vllm` (VLLM_API_KEY).

`--generation-config vllm` stops vLLM from applying the model's generation_config.json defaults
(Qwen3: top_p 0.95, top_k 20) to every request: only the sampling params we send and log apply.
"""

import modal

from seat_swap.model_config import MODEL_NAME, MODEL_REVISION

APP_NAME = "seat-swap-vllm"
GPU = "L40S"  # 48 GB: Qwen3-14B bf16 (~30 GB) plus KV cache for two concurrent sellers
VLLM_PORT = 8000
MAX_MODEL_LEN = 16384
MINUTES = 60

vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.21.0", "huggingface_hub[hf_xet]")
    .env({"HF_XET_HIGH_PERFORMANCE": "1", "HF_HOME": "/root/.cache/huggingface"})
    .add_local_python_source("seat_swap")
)
hf_cache = modal.Volume.from_name("seat-swap-hf-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("seat-swap-vllm-cache", create_if_missing=True)
VOLUMES = {"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache}

app = modal.App(APP_NAME)


@app.function(image=vllm_image, volumes=VOLUMES, cpu=4, timeout=60 * MINUTES)
def download():
    """Fetch the pinned weights into the Volume on a CPU container (no GPU time spent)."""
    from huggingface_hub import snapshot_download

    path = snapshot_download(MODEL_NAME, revision=MODEL_REVISION, ignore_patterns=["*.pt", "*.bin"])
    hf_cache.commit()
    print(f"{MODEL_NAME}@{MODEL_REVISION} -> {path}")


@app.server(
    image=vllm_image,
    gpu=GPU,
    volumes=VOLUMES,
    secrets=[modal.Secret.from_name("seat-swap-vllm")],
    port=VLLM_PORT,
    scaledown_window=2 * MINUTES,
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
