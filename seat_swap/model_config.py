"""The seller model: one place for its name and pinned revision.

Used by the local chat-template renderer (render.py) and by the Modal vLLM server
(modal_vllm.py), so the string we render and the weights that run it always agree.
To switch model, change these two lines (and redeploy the Modal app).
"""

MODEL_NAME = "Qwen/Qwen3-14B"
MODEL_REVISION = "40c069824f4251a91eefaf281ebe4c544efd3e18"
