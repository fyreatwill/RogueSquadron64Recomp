# NEXT work unit (s2267) — isolated silent-route qualification

HYPOTHESIS-ID: m5-silent-route-qualification

## Work unit

Run the silent+C88=`0` arm alone from the unchanged Debug build, using the
qualified `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, and
`ROGUESQ_LLE_SOLO=1` route plus only the existing audio-return,
PCM-boundary, B40/route-state, and phase loggers. This tests whether the
s2266 silent-arm `MetalFramebuffer` failure is intrinsic to the isolated
silent route or sensitive to the paired run. Do not add instrumentation,
change a default, or interpret silent output nulls as an audio-contract
result.

## Competing hypotheses and discriminating measurement

- **H-SilentIntrinsicPreTargetCrash:** the isolated silent arm repeats a
  pre-1024 crash in `MetalFramebuffer`, especially at
  `last-guest-pc=0x8000b650`. This makes the s2266 pair failure intrinsic to
  the silent route at the tested scope.
- **H-SilentRouteLoadSensitive:** the isolated silent arm passes the startup
  controls and reaches title and hangar, while the s2266 paired silent arm
  failed before 1024. This selects route-load/pair sensitivity and permits a
  fresh same-build image/silent output comparison; it does not identify an
  audio writer or authorize a mitigation.
- **H-SilentPreTargetStall:** the isolated arm remains alive but never reaches
  title `1024 @ 0x00790400` within the driver watchdog, with no crash marker.
  This selects a silent-route stall rather than the observed renderer crash.
- **H-SilentPartialTarget:** the isolated arm reaches 1024 but not hangar
  `512 @ 0x006AB400`, or lacks a required control. This keeps the pair
  comparison invalid and selects a narrower route boundary for the next
  discriminator.

The discriminating table is
`(startup, missing_func, 640_origins, title, hangar, phase, width, origin,
pcm_source_rows, pcm_consumer_rows, pcm_fnv, pcm_nz, driver_outcome,
crash_or_timeout, crash_pc, last_guest_pc)`. Positive controls are startup,
one `[missing-func]`, B40 rows, route-state rows, and phase transitions. Only
the outcome that reaches both title and hangar can permit the next paired
output run; all pre-target outcomes prohibit interpreting PCM or image nulls.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
env ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2267_silent_c88_0_isolated_route 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2267_silent_c88_0_isolated_route_driver.log 2>&1
```

Record the driver outcome, controls, phase transitions, title/hangar
qualification, crash or timeout fields, and target PCM rows. A qualified
isolated arm permits a new paired output contract run; a pre-target failure
selects route work only.
