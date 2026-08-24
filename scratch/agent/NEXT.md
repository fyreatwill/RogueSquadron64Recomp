# NEXT work unit (s2257) — separate trace load from silent-route instability

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent silent+C88=`0` / silent+C88=`0` pair with the
qualified spin/LLE route. Launch the fully traced arm first and the route-only
arm one second later. Keep startup, `[missing-func]`, 640, 1024, and 512
phase controls in both arms, plus B40/route-state rows. This is a route-load
discriminator, not an image/output comparison; do not change generated code,
task/output behavior, defaults, guards, or build artifacts.

## Competing hypotheses and discriminator

- **H-TraceLoad:** the fully traced arm fails or stalls before 1024 while the
  route-only arm reaches title and hangar. This selects instrumentation load
  as a contributor to the route split and requires a reduced-load output pair.
- **H-SharedRouteNondeterminism:** the two silent arms split, both fail before
  1024, or both qualify despite different trace loads. This rejects a clean
  trace-only explanation and leaves the route blocker unresolved for the
  output table.
- **H-CommonSilentDefect:** both arms reach the same 640 boundary and fail
  there with matching controls. This selects a common silent-route defect and
  requires a new route discriminator before image attribution.

The discriminator is the complete same-run table keyed by
`(arm,trace_level,phase,width,origin,b40,route_state,stable_title,hangar,driver_outcome,crash_or_timeout)`.
Positive controls are startup, one `[missing-func]`, the 640 origin, and
B40/route-state rows in each arm. A missing title/hangar result is valid only
after those controls fire. Compare only phase-keyed rows from this run.

## Run

```sh
(
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2257_full_silent_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2257_full_silent_c88_0_driver.log 2>&1 &
  p_full=$!
  sleep 1
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2257_route_silent_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2257_route_silent_c88_0_driver.log 2>&1 &
  p_route=$!
  wait "$p_full"; r_full=$?
  wait "$p_route"; r_route=$?
  print "full_rc=$r_full route_rc=$r_route"
)
```

Record both driver outcomes, the 640/1024/512 phase rows, and the B40/
route-state controls. If the route-only arm qualifies while the full arm does
not, the next unit reduces trace load before returning to the image/stub
output-contract pair. Keep `ROGUESQ_AUDIO_UCODE=1` opt-in.
