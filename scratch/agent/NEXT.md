# NEXT work unit (s2260) — same-build reduced image/output pair

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent image+C88=`0` / silent+C88=`0` pair with the
qualified spin/LLE route. Launch the image arm first and the silent arm one
second later. Use the reduced trace set: startup, `[missing-func]`, 640, 1024,
and 512 phase controls plus B40/route-state rows; omit task-contract,
host-boundary, PCM-boundary, B40-read, and thread-resume trace load. Keep the
image arm opt-in and make no runtime or default change.

## Competing hypotheses and discriminator

- **H-ImageOutputSplit:** both arms qualify title/hangar, and the image arm
  emits target image-stage rows while the silent arm emits none. This restores
  the output table and moves the boundary to stage/source/consumer payload
  attribution.
- **H-PairLoadInstability:** one or both arms fail before 1024/512 after the
  controls, despite the single-arm silent qualification. This says the pair
  recipe remains route-invalid; record each phase and terminal identity and
  do not interpret output nulls.
- **H-CommonOutputNull:** both arms qualify the target phases, but the image
  arm still has no target image-stage rows or only stage-only zero-payload
  rows. This selects a common output/contract boundary and requires a new
  phase-keyed payload discriminator.

The discriminator is the complete same-run table keyed by
`(arm,audio_mode,trace_level,phase,width,origin,b40,route_state,image_stage_rows,stable_title,hangar,driver_outcome,crash_or_timeout)`.
Positive controls are startup, one `[missing-func]`, the 640 origins, and
B40/route-state rows in each arm. A missing title/hangar result is valid only
after those controls fire. Compare only phase-keyed rows from this run.

## Run

```sh
(
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2260_image_c88_0_reduced 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2260_image_c88_0_reduced_driver.log 2>&1 &
  p_image=$!
  sleep 1
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2260_silent_c88_0_reduced 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2260_silent_c88_0_reduced_driver.log 2>&1 &
  p_silent=$!
  wait "$p_image"; r_image=$?
  wait "$p_silent"; r_silent=$?
  print "image_rc=$r_image silent_rc=$r_silent"
)
```

Record both driver outcomes, every 640/1024/512 phase row, B40/route-state
controls, and image-stage rows. Do not promote the image arm or add a
writeback/consumer guard based on a null result.
