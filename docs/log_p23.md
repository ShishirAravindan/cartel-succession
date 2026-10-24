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

## 2026-10-25 — P2/P3 stopped on parse failures (Kickoff 08, step 3)

- At 18:40 UTC, ~10 rounds in: P2 8/30 games `aborted_parse`, P3 6/30 (two unparseable answers in one
  round). Both kickoffs list parse failures as a stop condition, and the parser rule is the user's, so
  I **stopped both** (processes killed about 18:42 UTC; the unfinished games have no `status.json`). Apps reset to 2 min and stopped.
  Nothing was patched, and the fallback model was not used: the switch rule is about checks, and they passed.
- **Qwen3-8B (P2):** every failure (40) is the model echoing the output template with `<fill in here>`
  placeholders after its `</think>` and no price. **Only in `sib_full`**: first-attempt failure rate 0.18 (33 of 181 rounds),
  and P(the retry also fails | the first failed) = 0.24. In `sib_history`, 0 of 241 rounds failed. So it is the inherited 14B notes in the
  prompt that set it off. Expected per-round abort with one retry ≈ 0.18 × 0.24 ≈ 4%; survival to T+60 ≈ 7%.
- **gpt-oss-20b (P3):** all 33 failures have a final channel with an unambiguous price wrapped in markdown:
  `**My chosen price:**`, `` `1.92` ``, code fences, `---` rules. Stripping `**` and code fences alone recovers 24/33.
  The other 9 are single backticks or a bold header without a colon. First-attempt failure 0.16 (history) / 0.12 (full);
  the retry fails 0.31 / 0.14 of the time.
- Partial data stays in `seat_swap/runs/` (manifests `p23_sib_20261025-000230.json`, `p23_oth_20261025-000724.json`).
  No `p23` tag: the phase didn't complete.

## 2026-10-25 — PI decisions on the stop; parser and retry amendment (`prereg-p23b`)

- PI approved: (P3) markdown normalisation with an exactly-one-price-candidate limit, counted as `parse_markdown`;
  (P2 and P3 newcomers) up to 3 retries per seat-round. No 32B. One fresh rerun each, caps P2 $9 / P3 $11
  including spend so far. The stopped attempt is excluded from results (plan §12.1).
- Code: `prompts.markdown_clean` / `price_candidates`, `parse_response(markdown=True)` used only for harmony
  seats; `Seat.parse_retries` (`branch.PARSE_RETRIES`: sib 3, oth 3; everything else 1), logged in
  `config.seats[*].parse_retries`; per-call `parse_markdown`. Per-game `--max-calls` 200 for P2/P3 (was 135).
- **Replay of the 33 logged gpt-oss failures** (fixture `seat_swap/tests/data/p23_gptoss_failures.jsonl`, test
  `test_replay_of_the_33_logged_gptoss_failures`): 26 recover, 7 stay failures. Of those 7, 6 have a header
  without its colon (`**My chosen price**`, or a notes header such as `New content for PLANS.txt` with
  no colon), and 1 has a blank line after the price header. Every recovered price is the single number after the header:

| # | run (suffix) | round | attempt | raw final answer, from the price header on (verbatim) | recovered price |
|---|---|---|---|---|---|
| 1 | `dda8d7` | 156 | 0 | `**My chosen price:**  \n1.95` | still a failure |
| 2 | `cfbd8e` | 154 | 0 | `My chosen price:  \n1.92` | 1.92 |
| 3 | `cfbd8e` | 156 | 0 | `**My chosen price**  \n1.75` | still a failure |
| 4 | `3f7fbb` | 156 | 0 | `My chosen price:\n```\n1.92\n```` | 1.92 |
| 5 | `329b15` | 155 | 0 | `**My chosen price:**\n```\n1.88\n```` | still a failure |
| 6 | `329b15` | 155 | 1 | `My chosen price:\n```\n1.88\n```` | 1.88 |
| 7 | `3ed0e3` | 151 | 0 | `My chosen price:  \n```\n1.92\n```` | 1.92 |
| 8 | `e8dd4b` | 156 | 0 | `**My chosen price:**  \n1.90` | 1.90 |
| 9 | `a59867` | 153 | 0 | `**My chosen price**  \n1.92` | still a failure |
| 10 | `a59867` | 156 | 0 | `My chosen price:\n```\n1.92\n```` | 1.92 |
| 11 | `a59867` | 156 | 1 | `My chosen price:\n```\n1.92\n```` | 1.92 |
| 12 | `8729d6` | 152 | 0 | `**My chosen price:** 1.95` | 1.95 |
| 13 | `18de2a` | 153 | 0 | `My chosen price:\n```\n1.85\n```` | 1.85 |
| 14 | `c2bff0` | 152 | 0 | `**My chosen price:**  \n2.0` | still a failure |
| 15 | `c2bff0` | 152 | 1 | `My chosen price:  \n```\n1.92\n```` | 1.92 |
| 16 | `f8c7ef` | 154 | 0 | `**My chosen price:**  \n1.65` | 1.65 |
| 17 | `7d73d5` | 154 | 0 | `My chosen price:\n```\n1.80\n```` | 1.80 |
| 18 | `7d73d5` | 154 | 1 | `My chosen price:\n```\n1.80\n```` | 1.80 |
| 19 | `125574` | 153 | 0 | `**My chosen price:**  \n1.70` | 1.70 |
| 20 | `eaf25c` | 152 | 0 | `My chosen price:\n```\n2.00\n```` | 2.00 |
| 21 | `eaf25c` | 155 | 0 | `My chosen price:\n```\n1.5\n```` | 1.50 |
| 22 | `eaf25c` | 155 | 1 | `My chosen price:  \n`1.5`` | 1.50 |
| 23 | `87e257` | 153 | 0 | `**My chosen price:**  \n```1.90```` | 1.90 |
| 24 | `87e257` | 154 | 0 | `**My chosen price:**\n1.90` | 1.90 |
| 25 | `87e257` | 155 | 0 | `My chosen price:  \n```\n1.9\n```` | 1.90 |
| 26 | `ac50d3` | 153 | 0 | `**My chosen price**  \n1.70` | still a failure |
| 27 | `07c0a1` | 153 | 0 | `My chosen price:\n```\n1.66\n```` | 1.66 |
| 28 | `54649e` | 155 | 0 | `My chosen price:  \n```\n1.44\n```` | 1.44 |
| 29 | `54649e` | 155 | 1 | `My chosen price:  \n```\n1.47\n```` | 1.47 |
| 30 | `917053` | 152 | 0 | `**My chosen price:**\n1.92` | 1.92 |
| 31 | `917053` | 156 | 0 | `My chosen price:\n\n```\n1.92\n```` | still a failure |
| 32 | `917053` | 157 | 0 | `My chosen price:  \n`1.92`` | 1.92 |
| 33 | `e2abc9` | 154 | 0 | `My chosen price:\n```\n1.92\n```` | 1.92 |

  Rows 1, 5 and 14 show a bold price header with a colon that still fails. In each, a notes header (`New content for PLANS.txt`) has no colon, so the template doesn't match.
