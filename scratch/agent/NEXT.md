# NEXT: fold queued G1 coverage, levels 10–18

HYPOTHESIS-ID: g1-mission-coverage

Work unit: consume the next two queued recipes from
`scratch/agent/soak_queue/` and fold their verdicts. The static census in s5931
found 19 playable levels (0..18); levels 1–9 already have route+hold coverage,
so levels 10–18 are queued in paired runs. Do not resume the closed aim thread.

Competing hypotheses:

- H1: the remaining levels all reach flight and hold 300 s cleanly.
- H2: one or more remaining levels has a distinct crash, stall, or missing
  flight handoff; that level becomes the next root-cause datum.
- H3: the forced route cannot select a level at or above its bound; this is
  distinguished from a mission defect by the level-select control being absent
  or having the wrong mask.

Discriminator: in each same-run log, `[lvsel]` must show `a1 == 1<<level`, then
the mission origin must reach flight and remain alive for `HOLD=300`; record
`crashlines` and `vi_stalls30s`. No control line means unevaluable. Expected
commands are the queue runner's normal execution of the next two scripts; for
manual validation, run `zsh scratch/agent/soak_queue/g1_lvl10a.sh` and
`zsh scratch/agent/soak_queue/g1_lvl10b.sh` from the repository root.
