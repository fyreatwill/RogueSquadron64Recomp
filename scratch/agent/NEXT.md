# NEXT work unit — M3: intermittent black after leave (V2 follow-through)

s80: synthetic VI_FULLSYNC is healthy after post-leave SYNC_FULL loss
(V1/V3/V4 refuted). RDP-`fs` plateau ≠ synthetic stall. Detail:
`scratch/s73_post_a_scene/VIFS1_ANALYSIS.md`.

## Competing hypotheses (why snaps go black while FIRE + empty=0)

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| B1 | Game intentionally clears / presents empty colour FB mid hangar-flight | RDRAM at VI origin near-zero on black snaps; present-1024 drawn still "empty=0" only means RT non-null |
| B2 | Present shows a stale pair / wrong buffer while new pairs advance | drawn addr stable across black window while last-drawn / FIRE keep alternating; or pq.wc stuck |
| B3 | Black snaps are real in-game fade/loading frames (not a port bug) | black windows short, content returns without port change; stick still moves craft in content frames |
| B4 | Geometry draws to refused/wild CIMG; sane FB not updated | lastCimg wild on FIRE during black windows; last-drawn still sane but content frozen on pad |

## Discriminating measurement (ONE build if new log needed, else offline-first)

Prefer **offline-first** on existing `vifs1` if enough: correlate black snap
wall times with `[present-1024]` / `[last-drawn]` / `[vi-fs-decision]` FIRE
lastCimg in the same window. If ambiguous, one build:

```
[present-luma] drawn=0x.. mean=N black%=N (rate-limited, phase-scoped 512)
```

on the present path that already has empty=0 — positive control: non-black
hold_09-class frames must show high mean.

```bash
# if no new build needed — re-analyze vifs1 + optional second soak:
env PROBE_MODE=start_only HOLD_S=30 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh black1 0 12
# offline: snap meanL timeline + FIRE lastCimg in black vs rich windows
```

### Outcomes

- **B1:** next = why game clears / which state machine step.
- **B2:** next = present-queue / matcher after synthetic fullSync.
- **B3:** next = HOLD_S=60 craft stick response (M3 DoD).
- **B4:** next = CIMG target / refuse interaction during hangar-flight.

## Do not

- Re-open V1 (pair=0 blocks synthetic) — s80 refuted.
- Treat RDP-`fs` plateau as synthetic stall.
- Chase UnhandledJump 0x0231 as primary (0 on vifs1).
- Sampled `ROGUESQ_LOG_RUNNER` for single-task questions.
