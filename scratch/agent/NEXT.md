# NEXT work unit (s2835) — phase-640 route continuation discriminator

HYPOTHESIS-ID: m5-audio-route-640-continuation

## Work unit

Run one same-build image/silent pair with a new in-process input schedule that
continues Start presses after the observed VI 640 transition. Retain the
whole-RDRAM retail positive control and phase logging. Do not change audio
behavior or add a new guard.

## Competing hypotheses and discriminator

- H-input-exhausted: the prior schedules stop before the menu consumes the
  post-640 transition; continued phase-relative Start presses move both arms
  through title and hangar.
- H-route-independent-stall: the 640 boundary is independent of input; both
  arms remain at `0x0066A500` despite continued presses.
- H-audio-route-divergence: image and silent dispatch changes affect the route;
  the two arms diverge in phase or menu state under the same schedule.

The discriminator is one run containing both arms and the retail control:
title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` in both arms selects
H-input-exhausted; matching 640 terminal state selects H-route-independent-
stall; arm divergence selects H-audio-route-divergence. Only after a target
phase is reached may the M5 contract rows be interpreted.

## Exact commands

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2835_m5_route_continuation.sh
grep -a -E 'oracle_gate|title=|hangar=|\[phase\] vi_width=|\[autopilot\]|\[audtask-dispatch\]|\[CRASH\]|\[ABORT\]' scratch/agent/s2835_m5_route_continuation/driver.log
```

The new recipe must SIGKILL its process group and must treat pre-target audio
nulls as unevaluable.
