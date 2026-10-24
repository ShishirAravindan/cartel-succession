# Status, 2026-10-25 00:55 IST, during kickoff 07

## One-line summary
P1b base gate passes 15/15: every new seed (215–229) holds the planted cartel and enforces it. Arms launching now.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| `20261024-234550_p1b-base_qwen3-14b_thinkon_s{215..229}` + `*_phaseA_enforce_*` | P1b base (150 rounds) + enforcement test | **gate 15/15** |

Manifest: `seat_swap/runs/p1b_20261024-234550.json`. Code `9e44323` (= `prereg-p1b`).

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| P1b arms | 15 seeds × `control`, `same_history`, `same_full`, `same_notes`, 60 rounds, no probes | ≈ 02:30 |

## Key results
**Base** (pass rule unchanged from P1):

| seed | cartel_ci 121–150 | enforcement_retaliation | pass |
|---|---|---|---|
| 215 | +0.989 | −0.664 | yes |
| 216 | +0.989 | −0.664 | yes |
| 217 | +0.989 | −0.996 | yes |
| 218 | +0.989 | −0.996 | yes |
| 219 | +0.989 | −0.996 | yes |
| 220 | +0.989 | −0.664 | yes |
| 221 | +0.989 | −0.996 | yes |
| 222 | +0.989 | −0.664 | yes |
| 223 | +0.989 | −0.664 | yes |
| 224 | +0.989 | −0.996 | yes |
| 225 | +0.989 | −0.332 | yes |
| 226 | +0.989 | −0.664 | yes |
| 227 | +0.989 | −0.996 | yes |
| 228 | +0.989 | −0.664 | yes |
| 229 | +0.989 | −0.996 | yes |

Gate: 15/15 pass (need 8). Same pattern as P1 (−0.996 in 7 seeds, −0.664 in 7, −0.332 in 1).

## Surprises or worries
- Kickoff 08 (P2/P3) runs alongside in the worktree `../cartel-succession-p23` and shares the 14B app for its
  seat-0 calls; its status is in `docs/status_p23.md` on `exp/p23`.

## Decisions needed
None.

## Spend
Base ≈ 1 h 37 min on the 14B app (shared with P2/P3 seat-0 calls since about 18:30 UTC). The split by calls comes in the final report. Cap $16.

## Modal state
`seat-swap-vllm` deployed with `scaledown_window` 10 min.
