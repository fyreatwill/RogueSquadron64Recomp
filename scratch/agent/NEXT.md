# NEXT work unit — M3: high-tri syncs=0 / FULL_SYNC starvation (D3)

s78: wild-FB refuse gate live; G1 refuted. `fs` freezes ~3297 with trailing
tasks `syncs=0` from #4252 (s77: #4326). Gate stays as safety. Detail:
`scratch/s73_post_a_scene/FBGATE_ANALYSIS.md`.

## Competing hypotheses

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| S1 | Trailing hangar-flight tasks emit 0 SYNC_FULL in the post-translation hist → VI_FULLSYNC is the only frame boundary and it stops matching | `ROGUESQ_LOG_RUNNER_ALL=1`: tasks after leave have tris>0 and syncs=0; VI_FULLSYNC / present early lines stop or stall when fs plateaus |
| S2 | Tasks still emit SYNC_FULL but fullSync is skipped/failing (pair/path gate over-filter) | runner hist shows syncs≥1 on trailing high-tri tasks, yet fs still plateaus; gate-skip counters rise in same window |
| S3 | RSP UnhandledJump (0x0231, s78) aborts tasks before SYNC_FULL | UnhandledJump count correlates 1:1 with syncs=0 onset task#; fixing/skipping that jump restores syncs≥1 |
| S4 | Present follows a dead last-drawn while geometry still lands in a live FB | last-drawn stays wild/NO-FB while a sane FB (0x6AB000/0x656000) still receives draws; force-present of that addr shows content during "freeze" |

## Discriminating measurement (one build if new counters, one soak)

Phase-gate: start_only HOLD_S=20, `ROGUESQ_LOG_RUNNER_ALL=1` (already in
`run_mission_keys.sh`), keep tilecopy optional off to reduce noise.

```bash
env PROBE_MODE=start_only HOLD_S=20 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh syncs0 0 12
# offline (never cat whole log):
#   first task with tris>100 and syncs=0 after the last syncs≥1 high-tri
#   UnhandledJump count before/after that task#
#   fs max + how many consecutive update_screen share that fs
#   last-drawn / vi-follow NO-FB in the freeze window
#   pixel stats craft_stable vs hold_02 vs hold_10
```

If S2 needs a gate-skip counter, add one build of
`[fb-pair] SKIP wild/oob` at the workload/fullSync early-outs (batch with any
other counters).

### Outcomes

- **S1:** next unit = why hangar-flight DLs lose FULL_SYNC (ucode/DL walk), or
  strengthen VI_FULLSYNC during that phase.
- **S2:** relax/fix pair skip so legitimate post-leave pairs still fullSync.
- **S3:** map jump 0x0231 (overlay/ucode) — separate unit.
- **S4:** present-follow fix for hangar-flight FB, not runner.

## Do not

- Re-open wild-FB registration (s78 closed G1).
- Convert createTileCopy assert→skip without found=0.
- Cross-run A/B on animating hangar-flight without phase gate.
- Sampled `ROGUESQ_LOG_RUNNER` (1-in-32) for single-task questions — use `_ALL`.
