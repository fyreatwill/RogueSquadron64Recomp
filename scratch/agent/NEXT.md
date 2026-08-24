# NEXT work unit (s2255) — compare the qualified image/stub output contract

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent Step-1 output-contract pair with silent+C88=`0`
launched first and image+C88=`0` launched one second later. Keep the qualified
spin/LLE route, startup, `[missing-func]`, 640, 1024, and 512 controls. Keep
the B40, route-state, task-contract, image-stage/host, and PCM-boundary
traces, with high-volume thread-resume logging disabled. Use the existing
Debug binary; do not change generated code, task/output behavior, defaults,
guards, or build artifacts.

## Competing hypotheses and discriminator

- **H-ImageInputStillZero:** both arms qualify, and the image arm's target
  image-stage rows remain zero at field348, stage-0/1 DMEM, and stage-2/3
  generated-DMA/destination payloads, with all image joins `stage-only`.
  This keeps the missing producer/input boundary ahead of output writeback.
- **H-ImageStageProducesNonzero:** the image arm has target rows with nonzero
  field348 or generated payloads and at least one stage/source or
  stage/consumer join. This selects a live image-output edge for the next
  discriminator.
- **H-ImageConsumerOrderingGap:** image-stage payloads are nonzero, but target
  joins remain source-only or lack the expected consumer/order fields. This
  selects a consumer/order contract gap rather than a missing producer.
- **H-RouteInvalidAgain:** either arm lacks startup, `[missing-func]`, 640,
  stable title, or hangar controls. The output table is invalid and selects no
  contract hypothesis.

The discriminator is the complete same-run table keyed by
`(arm,phase,width,origin,task,task_dmem_changed,task_dma_count,stage,field348_fnv,field348_nz,stage_fnv,stage_nz,dma_fnv,dma_nz,dest_fnv,dest_nz,classification,source_match,consumer_match,ordering,host_writeback,pcm_source,pcm_consumer,stable_title,hangar,crash_symbol,last_guest_pc)`.
A null is invalid unless that arm has startup, one `[missing-func]`, the 640
positive control, stable title, and hangar. Compare only phase-keyed rows from
this run; do not use a stopwatch or promote the image default.

## Run

```sh
(
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2255_stub_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2255_stub_c88_0_driver.log 2>&1 &
  p_stub=$!
  sleep 1
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2255_image_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2255_image_c88_0_driver.log 2>&1 &
  p_image=$!
  wait "$p_stub"; r_stub=$?
  wait "$p_image"; r_image=$?
  print "stub_rc=$r_stub image_rc=$r_image"
)
```

Record the per-arm target table and both crash identities if either arm is
invalid. If both qualify, the image target join classification selects the
next M5 output-contract step; keep `ROGUESQ_AUDIO_UCODE=1` opt-in until that
selection is independently supported.
