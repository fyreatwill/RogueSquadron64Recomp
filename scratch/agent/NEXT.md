# NEXT work unit (s2250) — locate the C88-dependent route edge

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent three-arm route-state audit: image+C88=`1`,
image+C88=`0`, and silent stub+C88=`1`. Keep the common route controls,
phase gates, task contract, and PCM controls. Use only the existing
`m5-b40-route`, `m5-route-state`, and `m5-b40-read` traces; do not change
generated code, task/output behavior, defaults, or guards.

## Competing hypotheses and discriminator

- **H-C88RouteEdge:** the two image arms first diverge in a B40/route-state
  event, sampled state byte, or B40 read at a shared phase; the stub follows
  the C88=`0` route. The first divergent keyed row identifies the edge scope.
- **H-C88PostRoute:** image+C88=`1` and image+C88=`0` have the same route-state
  and B40 rows through the 640 control, but only C88=`1` dies before title.
  The interaction is after the logged route boundary and needs a later task
  edge, not another route-state field.
- **H-C88EarlyBoundary:** image+C88=`1` passes startup, 640, and the
  missing-function control but dies before the first route-state/B40 row,
  while the other arms produce the positive control. This places the effect
  before the current route witness; do not add another counter in this unit.
- **H-ImageNondeterminism:** the two image arms produce inconsistent route
  rows or crash identities across the same-build comparison, so C88 remains a
  route-correlated factor but not a selected causal edge.

The discriminating table is keyed by
`(arm,c88,phase,width,origin,missing_func,route_edge,route_state_bytes,
b40_read_pc,b40_value,task_dispatch,task_exit,crash_symbol,last_guest_pc)`.
Positive controls are startup, one `[missing-func]`, and the 640 origin
`0x00696100`; title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` remain
required route controls for the arms that survive. A null is invalid unless
the same arm has its startup, missing-function, and 640 controls.

## Run

```sh
(
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2250_image_c88_1 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2250_image_c88_1_driver.log 2>&1 &
  p_img1=$!
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2250_image_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2250_image_c88_0_driver.log 2>&1 &
  p_img0=$!
  env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2250_stub_c88_1 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2250_stub_c88_1_driver.log 2>&1 &
  p_stub=$!
  wait "$p_img1"; r_img1=$?
  wait "$p_img0"; r_img0=$?
  wait "$p_stub"; r_stub=$?
  print "image_c88_1_rc=$r_img1 image_c88_0_rc=$r_img0 stub_c88_1_rc=$r_stub"
)
```

Compare the three driver tails and bounded marker counts. Report the first
phase-keyed route/B40 divergence and the crash identities. If C88=`1` image
again has no route witness after its valid 640 control, classify the boundary
as H-C88EarlyBoundary and move to the next task edge without adding logging.
