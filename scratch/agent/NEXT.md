# NEXT work unit (s2265) — isolate the image route after paired failure

HYPOTHESIS-ID: m5-image-route-stability

## Work unit

Run one isolated image+C88=`0` reduced-trace recipe. Keep
`ROGUESQ_LOG_AUDIO_RETURN=1`, `ROGUESQ_LOG_PCM_BOUNDARY=1`, B40/route-state
tracing, the phase gate, and the qualified spin/LLE route. Use no
task-contract, ABI, DMA, host-boundary, or thread-resume tracing. This is a
route-stability discriminator after s2264's image-second arm died before
1024; do not change the image default or add a guard.

## Competing hypotheses and discriminator

- **H-ImageIsolatedQualifies:** the isolated image arm passes startup, one
  `[missing-func]`, both 640 transitions, title `1024 @ 0x00790400`, and
  hangar `512 @ 0x006AB400`; the paired failure is a route-load/concurrency
  observation and the output pair can be retried.
- **H-ImageIntrinsicPreTargetFailure:** the isolated image arm exits before
  1024 with no target PCM rows; the image route itself remains unqualified,
  so no output null is interpretable.
- **H-ImageIntermittentRoute:** the isolated arm reaches startup controls but
  dies before the target boundary without a stable intrinsic signature; this
  keeps route stability open and requires a new discriminator rather than a
  mitigation.

The discriminating table is
`(startup, missing_func, 640_origins, title, hangar, phase, width, origin,
image_stage_rows, pcm_source_rows, pcm_consumer_rows, nonzero_rows,
driver_outcome, crash_or_timeout, crash_pc, last_guest_pc)`. Reaching both
target phases selects H-ImageIsolatedQualifies; an exit before 1024 with the
startup controls selects H-ImageIntrinsicPreTargetFailure only if the same
pre-target signature is present, otherwise H-ImageIntermittentRoute. Positive
controls are startup, one `[missing-func]`, B40 rows, route-state rows, and
the phase logger itself; target image/PCM rows are interpreted only after
qualification.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
env ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2265_image_c88_0_isolated_route 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2265_image_c88_0_isolated_route_driver.log 2>&1
```

Record the driver outcome, all phase transitions, B40 and route-state controls,
the crash PC/last guest PC if pre-target, and phase-8/10/12 image plus PCM rows
only if the route qualifies. A qualified isolated arm selects a repeat paired
output comparison; a pre-target exit selects route stability only. Do not
promote `ROGUESQ_AUDIO_UCODE=1` or add a writeback/consumer guard based on this
run.
