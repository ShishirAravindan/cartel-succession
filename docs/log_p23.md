# Lab notebook, P2/P3 (Kickoff 08, branch `exp/p23`)

Kept apart from `docs/log.md` while Kickoff 07 runs in the main checkout; the PI reconciles them.
Newest entry at the bottom.

## 2026-10-24 — P2/P3 setup, checks and pre-registration (Kickoff 08, steps 1–2)

- **Worktree** `../cartel-succession-p23`, branch `exp/p23` off `origin/exp/p1` (`9d77675`). Runs go to the
  worktree's `seat_swap/runs/`; P1's base runs are read by absolute path from the main checkout, never written.
- **Models** (`seat_swap/model_config.py`, one `ModelSpec` each: app, Volume, Secret, compute.env prefix):
  - P2 `Qwen/Qwen3-8B` @ `b968826d9c46dd6066d109eabc6255188de91218`, thinking on, 0.6 / 0.95 / 20, max_tokens 8192
    (the 14B's settings, as the kickoff says). Same chat template as the 14B (test: byte-identical rendering).
  - P3 `openai/gpt-oss-20b` @ `6cee5e81ee83917806bbde320786a8fb61efebee`. **Sampling:** temperature 1.0,
    top_p 1.0, no top-k (sent as `top_k 0`, vLLM's "off"), max_tokens 8192: OpenAI's recommendation for
    gpt-oss (model card / harmony guide), reasoning effort **medium** (the kickoff). gpt-oss has no
    "thinking off", so the reasoning is always on.
  - **gpt-oss prompt format.** The HF chat template (`apply_chat_template`) and OpenAI's reference renderer
    `openai-harmony` differ by one stray blank line the HF template appends after the developer
    instructions. I render with `openai-harmony` (the model's own format, also what vLLM's own chat server
    uses for gpt-oss), with our system prompt as the developer instructions. The harmony system message
    carries "Reasoning: medium" and the date; the HF template writes today's local date, so I **pin the
    date to 2026-10-24** (otherwise the prompt changes at midnight). Test: our string tokenizes to exactly
    openai-harmony's token ids, and equals the HF template's output minus that blank line.
  - **gpt-oss output.** Sent with `skip_special_tokens=False` and stop ids `<|return|>`, `<|call|>`, so the
    raw completion keeps its channel markers (logged verbatim in `raw_completion`). The parser reads only
    the last `final` channel (`Completion.answer`); the `analysis` channel goes to `reasoning_text`. No
    final channel → empty answer → a parse failure (retry), never a price read from the reasoning.
- **Code:** providers render, sample and split per model; per-seat sampling and tokenizer revision are logged
  in `sampling_params`, `config.seats[*].sampling_override` and each call's `tokenizer_revision`. The 14B
  seats are unchanged (they keep the game's sampling). `modal_vllm.py` / `modal_weights.py` take
  `SEAT_SWAP_MODEL` (14b default, 8b, oth): app, Volume, Secret, compile cache and model follow it.
- **Checks** (all pass; 93 tests): rendering as above; parser reads the answer, not a decoy template with
  another price inside the reasoning (Qwen `<think>` and harmony `analysis`); every seat goes to its own
  model and endpoint, seat 0 to the 14B with the rule, seat 1 to the newcomer with no instruction text, each
  with its own sampling (`test_p23.py`). Dry-run arms from P1's s200 base and the full `p23 sib/oth --dry-run`
  (15 seeds × 2 arms) complete.
- Secrets `seat-swap-vllm-8b`, `seat-swap-vllm-oth` created with new keys (in the worktree's gitignored
  `compute.env`, never printed). Weights Volumes `seat-swap-hf-cache-8b` / `-oth` filled on CPU.
- Pre-registered in `docs/plan.md` §12 (numbered 12 to avoid P1b's §11) and tagged `prereg-p23`.

## 2026-10-25 — P2/P3 launched (Kickoff 08, step 3)

- Apps deployed from `ff2bb5d` (= `prereg-p23`) with `scaledown_window` 10 min: `seat-swap-vllm-8b`, `seat-swap-vllm-oth`
  (1 H100 each, up to 2 containers). URLs added to the worktree's `compute.env`.
- **Live smoke, one 2-round `sib_full` / `oth_full` branch of P1 s200 each** (`seat_swap/runs/smoke/`, throwaway):
  every call parsed; `verify_prompts --seat 1` 2/2 on tokens, echo and token ids for both models, so the
  string we log is what each server ran. gpt-oss answered in harmony channels (analysis, then final);
  the price came from the final channel. 8B 6–14 s/call, gpt-oss 8–11 s/call at no load.
- **P3 runs gpt-oss-20b** (the primary): its checks all passed about 35 min after I started on it, inside the
  kickoff's 45 min, so no switch to the fallback.
- P2 `seat_swap.p23 sib` launched about 18:31 UTC, P3 `seat_swap.p23 oth` about 18:37 UTC, 30 games each, against the
  14B app that is also running Kickoff 07's base.
