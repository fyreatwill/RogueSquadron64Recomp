# NEXT work unit (s2254) — reverse the C88=0 image/stub launch order

HYPOTHESIS-ID: m5-audio-step1-route-qualification

## Work unit

Run one same-build concurrent Step-1 audio validation pair with the silent
C88=`0` arm launched first and the image+C88=`0` arm launched one second
later. Keep the qualified spin/LLE route, startup, `[missing-func]`, 640,
1024, and 512 controls. Keep the B40, route-state, task-contract,
image-stage/host, and PCM-boundary traces. Leave high-volume thread-resume
logging disabled. Do not change generated code, task/output behavior,
defaults, guards, or build artifacts.

## Competing hypotheses and discriminator

- **H-ImageArmIntrinsic:** the silent arm reaches stable title/hangar while
  image+C88=`0` again fails before stable title, despite the reversed launch
  order. This keeps the image arm's route blocker ahead of contract
  attribution.
- **H-LaunchOrderShared:** reversing the order changes which arm qualifies or
  changes the crash identity, showing that the s2253 split is launch-order or
  shared route instability rather than image-arm-specific.
- **H-BothQualify:** both arms reach title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`; only then compare the phase-keyed task, image, PCM, and
  host rows to advance Step 1.
- **H-SharedRouteInstability:** both arms fail before stable title with
  startup, `[missing-func]`, and 640 controls present; no output hypothesis
  is selected.

The discriminator is the complete same-run per-arm table keyed by
`(arm,launch_order,phase,width,origin,missing_func,b40_route,b40_read,
audtask_dispatch,task_fields,task_exit,stage,stage_source_hash,
stage_dest_hash,stage_nz,host_writeback,pcm_source_hash,
pcm_consumer_hash,stable_title,hangar,crash_symbol,last_guest_pc)`.
A null is invalid unless that arm has startup, `[missing-func]`, and the 640
positive control. If both arms qualify, compare only this run's phase-keyed
rows; do not use a stopwatch or promote the image default.

## Run

```sh
(
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2254_stub_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2254_stub_c88_0_driver.log 2>&1 &
  p_stub=$!
  sleep 1
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2254_image_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2254_image_c88_0_driver.log 2>&1 &
  p_image=$!
  wait "$p_stub"; r_stub=$?
  wait "$p_image"; r_image=$?
  print "stub_rc=$r_stub image_rc=$r_image"
)
```

Record both crash identities if either arm is invalid. If both qualify, the
next unit can return to the full image-output contract comparison; otherwise
keep the image arm opt-in and design the next route discriminator from this
table.
