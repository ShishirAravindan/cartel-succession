"""Fill the vLLM server's weights Volume on a CPU container (a separate app, so no GPU is needed).

    uv run --project seat_swap modal run seat_swap/modal_weights.py
"""

import modal

from seat_swap.model_config import MODEL_NAME, MODEL_REVISION

image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install("huggingface_hub[hf_xet]")
    .env({"HF_XET_HIGH_PERFORMANCE": "1", "HF_HOME": "/root/.cache/huggingface"})
    .add_local_python_source("seat_swap")
)
hf_cache = modal.Volume.from_name("seat-swap-hf-cache", create_if_missing=True)
app = modal.App("seat-swap-weights")


@app.function(image=image, volumes={"/root/.cache/huggingface": hf_cache}, cpu=4, timeout=3600)
def download():
    from huggingface_hub import snapshot_download

    path = snapshot_download(MODEL_NAME, revision=MODEL_REVISION, ignore_patterns=["*.pt", "*.bin"])
    hf_cache.commit()
    print(f"{MODEL_NAME}@{MODEL_REVISION} -> {path}")
