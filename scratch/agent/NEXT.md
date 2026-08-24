# NEXT work unit (s2258) — reduced-trace image/output comparison

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent image+C88=`0` / silent+C88=`0` pair with the
qualified spin/LLE route. Launch the image arm first and the silent arm one
second later. Use reduced tracing in both arms: keep startup,
`[missing-func]`, 640, 1024, and 512 phase controls plus B40/route-state rows;
omit task-contract, host-boundary, PCM-boundary, B40-read, and thread-resume
trace load. This isolates the output comparison from the s2257 trace-load
split. Keep `ROGUESQ_AUDIO_UCODE=1` opt-in and make no runtime or default
change.

## Competing hypotheses and discriminator

- **H-ImageOutputSplit:** both arms qualify through title/hangar, and the
  image arm has target image-stage rows while the silent arm has none. This
  restores a valid reduced-load output table and moves the open boundary to
  stage/source/consumer payload attribution.
- **H-ReducedRouteInstability:** either arm fails before 1024 or 512 after the
  positive controls. This says route instability remains at reduced load and
  blocks output attribution; record the failing phase and crash identity.
- **H-CommonReducedRoute:** both arms reach the same target phases with matched
  route controls, but the image arm still has no target image rows or both
  arms fail identically. This selects a common reduced-load route/output
  boundary and requires a new phase-keyed discriminator.

The discriminator is the complete same-run table keyed by
`(arm,audio_mode,trace_level,phase,width,origin,b40,route_state,image_stage_rows,stable_title,hangar,driver_outcome,crash_or_timeout)`.
Positive controls are startup, one `[missing-func]`, the 640 origin, and
B40/route-state rows in each arm. A missing title/hangar result is valid only
after those controls fire. Compare only phase-keyed rows from this run.

## Run

```sh
(
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2258_image_c88_0_reduced 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2258_image_c88_0_reduced_driver.log 2>&1 &
  p_image=$!
  sleep 1
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2258_silent_c88_0_reduced 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2258_silent_c88_0_reduced_driver.log 2>&1 &
  p_silent=$!
  wait "$p_image"; r_image=$?
  wait "$p_silent"; r_silent=$?
  print "image_rc=$r_image silent_rc=$r_silent"
)
```

Record both driver outcomes, the 640/1024/512 phase rows, B40/route-state
controls, and image-stage rows. Do not promote the image arm or add a
writeback/consumer guard based on a null result.
