# Provenance: which code each result ran on

From the `git.sha` recorded in every run's `config.json` (all clean trees). A "freeze tag" is the
`prereg-*` tag committed before that family's live runs; the result tag marks the commit the arms ran on.

| family | base (+ enforcement test) ran on | arms ran on | freeze tag | result tag | runs |
|---|---|---|---|---|---|
| P1 (seeds 200–214) | `650e722` | `47138da` (status-only commit after the gate) | `prereg-p1` = `650e722` | `p1` = `47138da` | base 15, enforce 15, arms 75, probes 75; manifest `runs/p1_20261024-192633.json` |
| P1b (seeds 215–229) | `9e44323` | `24f922b` (status-only commit after the gate) | `prereg-p1b` = `9e44323` | `p1b` = `24f922b` | base 15, enforce 15, arms 60; manifest `runs/p1b_20261024-234550.json` |
| P2 sibling, Qwen3-8B (seeds 200–214) | P1's base, `650e722` (no new base) | `126cf3f` | `prereg-p23` = `ff2bb5d`, amended `prereg-p23b` = `126cf3f` | `p23` = `126cf3f` | 30 arms; manifest `runs/p23_sib_20261025-002242.json` (in the `cartel-succession-p23` worktree) |
| P3 other family, gpt-oss-20b (seeds 200–214) | P1's base, `650e722` (no new base) | `126cf3f` | `prereg-p23` = `ff2bb5d`, amended `prereg-p23b` = `126cf3f` | `p23` = `126cf3f` | 30 arms; manifest `runs/p23_oth_20261025-002243.json` (same worktree) |

- P2/P3's stopped first attempt ran on `ff2bb5d` (`p23_sib_20261025-000230`, `p23_oth_20261025-000724`) and is
  excluded from results (plan §12.1).
- P1 and P1b arms ran on a later commit than their base because the gate result was committed before launching the
  arms; those commits change only `docs/`.
