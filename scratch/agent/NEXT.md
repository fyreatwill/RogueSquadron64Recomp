# NEXT work unit (s2508) — compare stub/image route reachability

HYPOTHESIS-ID: m5-audio-arm-route-reachability

## Single work unit

Run one same-build A/B route-reachability capture with the silent stub
(`ROGUESQ_AUDIO_UCODE=0`) and Factor 5 image arm
(`ROGUESQ_AUDIO_UCODE=1`) using the qualified route and identical
phase-relative key schedule. Keep the existing task dispatch/exit, table,
image-stage, PCM-boundary, and crash/phase controls enabled. Build both arms
from the same Debug tree and run them concurrently; do not change the audio
implementation.

## Competing hypotheses and discriminator

- `H-image-causes-route-stall`: the image arm fails to reach 1024/512 while
  the silent stub reaches the same route.
- `H-route-independent`: both arms reach the same phase boundary or both fail
  before it; the prior failure is not caused by image-arm behavior.
- `H-stub-degenerate`: the silent stub alone fails to reach the route, so the
  image arm is not the route blocker.

The discriminator is the same-build A/B table of first phase transition, last
phase, target-gate reached, target image-stage/DMA count, PCM-consumer count,
task completion count, and crash/timeout outcome for each arm. Each arm must
pass its early table/dispatch control; a target writer conclusion is not
allowed unless the 1024/512 route and image/PCM controls fire.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run one `ROGUESQ_AUDIO_UCODE=0` and one `ROGUESQ_AUDIO_UCODE=1` arm
concurrently, each with a distinct absolute output directory under
`scratch/agent/s2508_m5_audio_arm_route/`, using the qualified
`tools/probe.sh` route from s2506 and these controls:
`ROGUESQ_LOG_M5_AI_TABLE=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`,
`ROGUESQ_LOG_PCM_BOUNDARY=1`. Summarize both arms in `audit.md`.
