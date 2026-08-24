# NEXT work unit (s2252) — reverse the C88-arm launch order

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent route-stability A/B with image+C88=`0` launched
first and image+C88=`1` launched one second later. Keep the qualified startup,
`[missing-func]`, 640, title 1024, and hangar 512 controls. Keep the B40,
route-state, task-contract, image-host, and PCM-boundary traces. Leave the
high-volume thread-resume trace disabled as in the fixed s2251 retry. Do not
change generated code, task/output behavior, defaults, or guards.

## Competing hypotheses and discriminator

- **H-C88IntrinsicRoute:** C88=`1` still fails before title when launched
  second, while C88=`0` qualifies. This supports a C88-associated route
  failure, but still does not identify a task/image/PCM edge.
- **H-LaunchOrderContention:** reversing launch order changes which arm
  qualifies or moves the failure to the first/second process. This selects
  process contention or ordering rather than C88 as the measured cause.
- **H-RunNondeterminism:** both arms' outcomes vary without a stable relation
  to C88 or launch order. This keeps route qualification as the blocker and
  authorizes no output attribution.
- **H-PostRoutePairQualified:** both arms reach title and hangar. Only then
  compare the first keyed task/image/PCM divergence in this same run.

The discriminator is the complete per-arm table keyed by
`(launch_order,arm,c88,phase,width,origin,missing_func,b40_route,b40_read,
audtask_join,task_fields,task_exit,stage,stage_source_hash,stage_dest_hash,
stage_nz,host_writeback,pcm_source_hash,pcm_consumer_hash,crash_symbol,
last_guest_pc)`. A null is invalid unless that arm has startup,
`[missing-func]`, and the 640 control. If both arms qualify, use the existing
task/image/PCM rows to select the first post-route boundary; do not compare
this run with s2251's C88=`0`-only target capture.

## Run

```sh
(
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2252_order0_first 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2252_order0_first_driver.log 2>&1 &
  p_img0=$!
  sleep 1
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2252_order1_second 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2252_order1_second_driver.log 2>&1 &
  p_img1=$!
  wait "$p_img0"; r_img0=$?
  wait "$p_img1"; r_img1=$?
  print "order0_first_rc=$r_img0 order1_second_rc=$r_img1"
)
```

Compare only the same-run arms using their route controls and phase-keyed
rows. Record both crash identities if either arm is invalid.
