# NEXT work unit (s2264) — pair qualified silent control with image arm

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build, two-arm reduced-trace pair with the silent+C88=`0` arm
launched first and the image+C88=`0` arm launched second. Keep
`ROGUESQ_LOG_AUDIO_RETURN=1`, `ROGUESQ_LOG_PCM_BOUNDARY=1`, B40/route-state
tracing, the phase gate, and the qualified spin/LLE route. Use no
task-contract, ABI, DMA, host-boundary, or thread-resume tracing. This is one
output-contract comparison; do not change the image default or add a guard.

## Competing hypotheses and discriminator

- **H-BothArmsQualified:** both arms pass startup, one `[missing-func]`, the
  two 640 transitions, title `1024 @ 0x00790400`, and hangar
  `512 @ 0x006AB400`, so their phase-keyed output rows are comparable.
- **H-PairRouteInvalid:** either arm fails before both target phases. Its
  output nulls are unevaluable and the pair selects only a route-stability
  work unit.
- **H-ImageStagePayloadJoin:** the qualified image arm has target stage rows
  with nonzero payloads that match PCM source and consumer rows by
  destination, length, FNV, nonzero count, completion, and valid order; the
  qualified silent arm retains the all-zero PCM boundary established in
  s2262.
- **H-ImageContractGap:** both arms qualify, but image stage rows remain zero,
  stage-only, or fail the exact PCM source/consumer join while the silent arm
  stays all-zero. This selects the measured contract gap only, not a writer or
  runtime fix.

The discriminating table is
`(arm, startup, missing_func, 640_origins, title, hangar, phase, width,
origin, stage_rows, nonzero_stage_rows, pcm_source_rows,
pcm_consumer_rows, nonzero_source_rows, nonzero_consumer_rows,
stage/PCM dest+len+fnv+nz, completion_before, source_before_consumer,
ordering_violation, driver_outcome, crash_or_timeout)`. Any missing target
phase selects H-PairRouteInvalid before interpreting output. Positive controls
are per-arm startup/missing-function/route/B40 rows, image-stage logging in
the image arm, and source/consumer logging with all-zero payloads in the
silent arm.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

Launch the silent arm first, then the image arm in the same shell so both
arms use the same executable:

```sh
env ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2264_silent_c88_0_pcm_pair_silent_first 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2264_silent_c88_0_pcm_pair_silent_first_driver.log 2>&1 &
env ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2264_image_c88_0_pcm_pair_image_second 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2264_image_c88_0_pcm_pair_image_second_driver.log 2>&1 &
wait
```

Record both driver outcomes, all target phase transitions, per-arm B40 and
route-state controls, and phase-8/10/12 stage plus PCM rows. A qualified pair
selects the next output-contract boundary; a route-invalid arm selects only a
new route-stability work unit. Do not promote `ROGUESQ_AUDIO_UCODE=1` or add a
writeback/consumer guard based on this pair alone.
