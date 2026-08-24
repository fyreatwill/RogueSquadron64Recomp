# NEXT work unit (s2253) — qualify C88=0 image against the silent control

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent two-arm comparison with image+C88=`0` and the
silent stub+C88=`0`. Keep the qualified spin/LLE route, startup,
`[missing-func]`, 640, title 1024, and hangar 512 controls. Keep the B40,
route-state, task-contract, image-host, and PCM-boundary traces. Leave the
high-volume thread-resume trace disabled. Do not change generated code, task
or output behavior, defaults, or guards.

## Competing hypotheses and discriminator

- **H-ImageOutputContractGap:** both arms qualify; the image arm shows real
  ABI/DMA/stage activity but no stage/source or stage/consumer join, while the
  silent control has no image-stage rows. This keeps the contract gap open.
- **H-ImagePayloadJoin:** both arms qualify and the image arm supplies a
  nonzero stage payload with exact source/consumer joins or a retail-span
  overlap. This moves the open boundary downstream of image generation.
- **H-ImageArmRouteInstability:** the silent control qualifies but the C88=`0`
  image arm dies before title. This keeps an image-arm-specific route blocker
  ahead of output attribution.
- **H-SharedRouteInstability:** both arms fail before title, with startup,
  `[missing-func]`, and 640 controls present. This leaves route stability as
  the blocker and selects no output hypothesis.

The discriminator is the complete same-run per-arm table keyed by
`(arm,phase,width,origin,missing_func,b40_route,b40_read,audtask_join,
task_fields,task_exit,stage,stage_source_hash,stage_dest_hash,stage_nz,
host_writeback,pcm_source_hash,pcm_consumer_hash,crash_symbol,last_guest_pc)`.
A null is invalid unless that arm has startup, `[missing-func]`, and the 640
positive control. If both arms reach the target phases, compare only their
phase-keyed task/image/PCM rows from this run; do not use a stopwatch or
promote a guard/default from the result.

## Run

```sh
(
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2253_image_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2253_image_c88_0_driver.log 2>&1 &
  p_image=$!
  sleep 1
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2253_stub_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2253_stub_c88_0_driver.log 2>&1 &
  p_stub=$!
  wait "$p_image"; r_image=$?
  wait "$p_stub"; r_stub=$?
  print "image_rc=$r_image stub_rc=$r_stub"
)
```

Compare only the same-run arms using their route controls and phase-keyed
rows. Record both crash identities if either arm is invalid.
