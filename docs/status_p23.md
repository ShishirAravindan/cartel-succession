# Status P2/P3, 2026-10-25 00:30 IST, after kickoff 08 (stopped, decisions needed)

## One-line summary
Both newcomer models passed every check, but in the live arms they often break the strict output format,
so most games would abort before the T+30 shock. I stopped P2 and P3 after ~10 rounds to ask how to proceed.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| `seat_swap/runs/smoke/*` | 2-round live smoke per newcomer | all parsed; prompt verification 2/2 per model (tokens, echo, ids) |
| `p23_sib_20261025-000230` | P2, stopped ≈ round T+10 | 8/30 games aborted_parse; 40 failed calls, all `<fill in here>` template echoes, all in `sib_full` |
| `p23_oth_20261025-000724` | P3, stopped ≈ round T+5 | 6/30 games aborted_parse; 33 failed calls, all a markdown-wrapped price in the final channel |

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| – | nothing in P2/P3 (Kickoff 07 runs separately) | – |

## Key results
Parse failures per newcomer call (first attempt) and P(the retry also fails | the first failed):

| arm | rounds | first-attempt failure | retry fails | form |
|---|---|---|---|---|
| sib_history | 241 | 0.00 | – | – |
| sib_full | 181 | 0.18 | 0.24 | template echoed with `<fill in here>`, no price |
| oth_history | 79 | 0.16 | 0.31 | `**My chosen price:**`, `` `1.92` ``, code fences |
| oth_full | 116 | 0.12 | 0.14 | same |

- The 8B fails **only when it inherits the 14B's notes**. That is a finding in itself: the sibling can't
  hold the output format when it reads the incumbent's memory.
- gpt-oss plays sensibly (prices and notes are coherent). Every failure is formatting around an
  unambiguous price. Stripping `**` and code fences recovers 24/33; the rest are single backticks or bold without a colon.

## Surprises or worries
- None of this showed up in the 2-round smokes. The rates only showed at 30 games.

## Decisions needed
1. **P3 parser.** Options: (a) normalise markdown (bold, backticks, fences, `---`) in gpt-oss's final channel
   before the strict match, count it as `parse_markdown` (like `parse_bracketed`), and rerun 30 fresh games;
   (b) switch the other-family model. My recommendation: (a). The model works, the price is unambiguous,
   and this is the same kind of tolerance as `parse_bracketed`. ≈ $6–9.
2. **P2 sibling.** Options: (a) keep Qwen3-8B and allow 3 retries per seat-round (per-round abort ≈ 0.18 ×
   0.24³ ≈ 0.25%, so ≈ 86% of games survive 60 rounds); (b) report "the 8B can't hold the format with inherited
   notes" as the P2 result and run only `sib_history`; (c) a larger sibling (Qwen3-32B; fits one H100 in bf16 only
   with a small KV cache, or as the official FP8 checkpoint, which changes precision). My recommendation: (a), and
   report the failure rate as a result. (c) changes the question from "smaller sibling" to "stronger sibling".
3. Any rerun is a fresh set of games under new run IDs, not a resume.

## Spend
P2/P3 so far ≈ $1–2 (weights download on CPU, two apps up ≈ 20–30 min each). Not yet read from Modal billing.
Caps P2 $8, P3 $10. Sprint total before tonight ≈ $27.6.

## Modal state
`seat-swap-vllm-8b`, `seat-swap-vllm-oth`: redeployed at 2 min, then stopped. `seat-swap-vllm` (14B): not touched; it serves Kickoff 07.
