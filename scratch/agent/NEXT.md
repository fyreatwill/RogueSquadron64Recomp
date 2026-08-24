# NEXT work unit (s2251) — locate the first post-route C88 task/output edge

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent two-arm post-route audit: image+C88=`1` and
image+C88=`0`. Keep the common startup, `[missing-func]`, 640, title 1024,
and hangar 512 route controls. Enable the existing task-contract, image-stage,
host-boundary, and PCM-boundary traces; retain the B40 traces as route
qualification. Do not change generated code, task/output behavior, defaults,
or guards.

## Competing hypotheses and discriminator

- **H-C88TaskContract:** the first keyed difference after identical target
  route-state rows is task dispatch, task fields, image input, completion, or
  generated DMA metadata. This selects the task boundary as the next causal
  edge.
- **H-C88ImagePayload:** task rows and completion match, but image-stage or
  host-boundary payload hashes/nonzero counts diverge at a shared phase. This
  selects the image transform/writeback boundary.
- **H-C88PCMConsumer:** task/image-stage payloads match, but paired PCM
  source/consumer rows diverge. This selects the downstream PCM consumer or
  callback boundary.
- **H-C88RouteOnlyIntermittency:** both image arms produce the same complete
  task/image/PCM table through title and hangar. This leaves the prior
  pre-title split as intermittent at this measured scope; do not add another
  route counter.

The discriminating table is keyed by
`(arm,c88,phase,width,origin,missing_func,b40_route,b40_read,
task_dispatch,task_fields,task_exit,stage,stage_source_hash,stage_dest_hash,
stage_nz,host_writeback,pcm_source_hash,pcm_consumer_hash,crash_symbol,
last_guest_pc)`. The positive controls are startup, one `[missing-func]`,
the 640 origin `0x00696100`, and the two target origins. A null is invalid
unless that same arm has the startup, missing-function, and 640 controls.

## Run

```sh
(
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2251_image_c88_1 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2251_image_c88_1_driver.log 2>&1 &
  p_img1=$!
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2251_image_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2251_image_c88_0_driver.log 2>&1 &
  p_img0=$!
  wait "$p_img1"; r_img1=$?
  wait "$p_img0"; r_img0=$?
  print "image_c88_1_rc=$r_img1 image_c88_0_rc=$r_img0"
)
```

Compare the two driver tails and bounded marker counts. Report the first
post-route keyed divergence and both crash identities. If both arms qualify
through title and hangar, a complete equality of task/image/PCM rows selects
H-C88RouteOnlyIntermittency and closes this table without adding another
counter.
