# NEXT work unit (s2256) — isolate shared route instability with duplicate silent arms

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent route-control pair with silent+C88=`0` in both
arms, launched one second apart. Keep the qualified spin/LLE route, startup,
`[missing-func]`, 640, 1024, and 512 controls and the same B40, route-state,
task-contract, host-boundary, and PCM-boundary trace load as s2255. This is a
route discriminator, not an output comparison: both arms deliberately use the
silent stub. Use the existing Debug binary; do not change generated code,
task/output behavior, defaults, guards, or build artifacts.

## Competing hypotheses and discriminator

- **H-SilentBaselineQualifies:** both identical silent arms pass title `1024`
  and hangar `512`, with only the known post-hangar abort. This makes the
  current failure less likely to be a silent/shared route defect and
  authorizes a fresh image/stub output-contract pair, but does not identify
  image output.
- **H-CommonSilentDefect:** both silent arms fail at the same pre-target
  boundary with matching controls and crash identity. This selects a common
  silent-route defect and requires a new route discriminator before output
  attribution.
- **H-IdenticalArmNondeterminism:** the two identical arms split, or both fail
  at distinct pre-target PCs after matching controls. This selects
  per-process/shared scheduling nondeterminism and leaves the output table
  blocked; it is distinct from a common deterministic silent defect.

The discriminator is the complete same-run route table keyed by
`(arm,phase,width,origin,b40,route_state,stable_title,hangar,crash_symbol,last_guest_pc)`.
The positive controls are startup, one `[missing-func]`, the 640 origin, and
the B40/route-state rows in each arm. A null title/hangar result is valid for
this route-control experiment only after those controls fire. Compare only
phase-keyed rows from this run; do not use a stopwatch or promote the image
default.

## Run

```sh
(
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2256_stub_a_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2256_stub_a_c88_0_driver.log 2>&1 &
  p_stub_a=$!
  sleep 1
  env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2256_stub_b_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2256_stub_b_c88_0_driver.log 2>&1 &
  p_stub_b=$!
  wait "$p_stub_a"; r_stub_a=$?
  wait "$p_stub_b"; r_stub_b=$?
  print "stub_a_rc=$r_stub_a stub_b_rc=$r_stub_b"
)
```

Record the per-arm route table, phase controls, and both crash identities if
either arm is invalid. If both qualify, the next unit returns to the
image/stub output-contract pair; keep `ROGUESQ_AUDIO_UCODE=1` opt-in until
that table is independently supported.
