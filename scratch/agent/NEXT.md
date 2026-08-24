# NEXT work unit (s2266) — paired image/silent output contract

HYPOTHESIS-ID: m5-image-output-contract

## Work unit

Run both arms from the same unchanged build, concurrently: image+C88=`0` and
silent+C88=`0`. Keep the qualified `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1` route, plus only the
existing audio-return, PCM-boundary, B40/route-state, and phase loggers. Do
not add task-contract, ABI, DMA, host-boundary, or thread-resume tracing. Do
not promote the image arm or add a writeback, consumer, slot, gate, or guard
change.

## Competing hypotheses and discriminating measurement

- **H-CompleteImageOutputContract:** both arms qualify through title and
  hangar; image stage rows, exact source/consumer tuples, and completion order
  agree at the target boundary, with the image arm's nonzero rows separated
  from the silent arm's all-zero PCM control.
- **H-ImageStageWithoutPcmContract:** both arms qualify, but image stage rows
  are nonzero while PCM source/consumer rows remain all-zero or fail to join;
  this selects a stage-only boundary and does not authorize a consumer fix.
- **H-ImageTupleOrOrderingMismatch:** both arms qualify, but image
  destination/length/FNV/nonzero tuples or completion order disagree between
  stage, source, and consumer rows; this selects a contract mismatch rather
  than a route failure.
- **H-PairRouteInvalid:** either arm misses startup, `[missing-func]`, its B40
  or route-state controls, title `1024 @ 0x00790400`, or hangar
  `512 @ 0x006AB400`; no output null or mismatch is interpretable for that
  pair and the route remains the next discriminator.

The complete discriminating table is per arm:
`(startup, missing_func, 640_origins, title, hangar, phase, width, origin,
stage_rows, nonzero_stage_rows, source_rows, consumer_rows, exact_matches,
destination, length, FNV, completion_order, driver_outcome, crash_or_timeout,
crash_pc, last_guest_pc)`. Positive controls are startup, one
`[missing-func]`, B40 rows, route-state rows, and the phase logger in both
arms. Interpret image/PCM rows only after both arms qualify.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
env ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2266_image_c88_0_pair_image_first 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2266_image_c88_0_pair_image_first_driver.log 2>&1 &
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2266_silent_c88_0_pair_silent_second 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2266_silent_c88_0_pair_silent_second_driver.log 2>&1 &
wait
```

Record each arm's driver outcome, controls, phase transitions, exact target
rows, and crash/last-guest-PC fields. A pair with both target-qualified arms
selects one of the three output-contract hypotheses; a pre-target failure in
either arm selects H-PairRouteInvalid. The s2265 isolated qualification is
single-source route evidence, so do not treat this pair as a runtime default
change without the required independent comparison.
