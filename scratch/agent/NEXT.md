# NEXT work unit (s2268) — paired image/silent output contract

HYPOTHESIS-ID: m5-image-output-contract

## Work unit

Run image+C88=`0` and silent+C88=`0` concurrently from the unchanged Debug
build, using the qualified `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1` route plus only the
existing audio-return, PCM-boundary, B40/route-state, image-stage, and phase
loggers. Both arms must pass their startup, `[missing-func]`, B40/route-state,
title `1024 @ 0x00790400`, and hangar `512 @ 0x006AB400` controls before any
output comparison is interpreted. Do not change a default or add a
writeback, consumer, slot, gate, or guard.

## Competing hypotheses and discriminating measurement

- **H-CompleteImageOutputContract:** both arms pass target qualification, and
  the image arm has nonzero stage rows with exact destination/length/FNV joins
  to both its generated source and consumer records in the same target phase;
  the silent arm remains the all-zero PCM control. This selects a complete
  image-stage contract at the measured rows, without authorizing a runtime
  change.
- **H-ImageStageWithoutPcmContract:** both arms pass target qualification, the
  image arm has real stage/source/consumer joins, but the PCM boundary remains
  identical and all zero in both arms. This selects stage-only output evidence
  and keeps the audio writer/consumer boundary open.
- **H-ImageTupleOrOrderingMismatch:** both arms pass target qualification, but
  image rows lack exact source/consumer joins or their completion order does
  not agree with the corresponding stage events. This selects a tuple/order
  contract mismatch rather than a null image arm.
- **H-PairRouteInvalid:** either arm misses a required control or target phase,
  or exits before the comparison window. This prohibits interpreting every
  image/PCM difference and selects route qualification work only.

The discriminating table is
`(arm, startup, missing_func, B40_rows, route_state_rows, title, hangar,
phase, width, origin, image_stage_rows, image_stage_nz, image_source_rows,
image_consumer_rows, exact_tuple_joins, completion_order, pcm_source_rows,
pcm_consumer_rows, pcm_fnv, pcm_nz, driver_outcome, crash_or_timeout,
crash_pc, last_guest_pc)`. Positive controls are startup, one
`[missing-func]`, B40 rows, route-state rows, and phase transitions in each
arm. The comparison is valid only when both arms reach title and hangar; a
post-target aligned-ROM abort is recorded but does not invalidate the rows.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2268_image_c88_0_pair 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2268_image_c88_0_pair_driver.log 2>&1 &
image_pid=$!
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2268_silent_c88_0_pair 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2268_silent_c88_0_pair_driver.log 2>&1 &
silent_pid=$!
wait "$image_pid"
image_rc=$?
wait "$silent_pid"
silent_rc=$?
printf 'image_rc=%s silent_rc=%s\n' "$image_rc" "$silent_rc"
```

Record both driver outcomes, controls, phase transitions, title/hangar
qualification, crash or timeout fields, image stage/source/consumer joins,
completion order, and target PCM rows. A route-invalid arm selects route work
only; two qualified arms select one of the three output-contract hypotheses.
