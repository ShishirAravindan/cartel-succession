# Status P2/P3, 2026-10-25 00:10 IST, after kickoff 08

## One-line summary
Both newcomer models pass every check (local and server-side). P2 (Qwen3-8B) and P3 (gpt-oss-20b) are running: 30 games each from P1's base snapshots.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| `seat_swap/runs/smoke/*` | 2-round live smoke per newcomer | all parsed; prompt verification 2/2 per model |

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| `p23_sib_*` | P2: `sib_history`, `sib_full` × seeds 200–214 | ≈ 01:30–02:00 |
| `p23_oth_*` | P3: `oth_history`, `oth_full` × seeds 200–214 | ≈ 01:30–02:00 |

## Key results
None yet.

## Surprises or worries
- The HF chat template for gpt-oss appends a stray blank line after the developer instructions that OpenAI's
  reference renderer does not. Prompts are rendered with `openai-harmony`, with the date pinned (see the log).

## Decisions needed
None so far.

## Spend
Caps: P2 $8, P3 $10. Sprint total before tonight ≈ $27.6. With Kickoff 07's $16 cap, tonight's caps add up to
$34, which would pass the $45 checkpoint. The coordinator set these caps in the kickoffs, so I'm proceeding.

## Modal state
`seat-swap-vllm-8b`, `seat-swap-vllm-oth`: deployed, scaledown 10 min, running. `seat-swap-vllm` (14B) is not managed here.
