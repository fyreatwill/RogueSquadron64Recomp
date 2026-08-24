# NEXT work unit (s2259) — single-arm reduced-route baseline

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one reduced-trace silent+C88=`0` baseline with the qualified spin/LLE
route. This is a route-stability control, not an image/output comparison:
keep startup, `[missing-func]`, 640, 1024, and 512 phase controls plus
B40/route-state rows; omit task-contract, host-boundary, PCM-boundary,
B40-read, and thread-resume trace load. Keep `ROGUESQ_AUDIO_UCODE=0` and make
no runtime or default change.

## Competing hypotheses and discriminator

- **H-ConcurrentLoad:** the single silent arm reaches title `1024` and hangar
  `512` after the same positive controls. This makes two-process concurrent
  load a live explanation for s2258's paired pre-title failure and restores a
  route-qualified recipe for a later image comparison.
- **H-IntrinsicReducedRoute:** the single arm fails before 1024/512 after the
  controls, at the same `cutsceneDispatchSlotsByFlag` site or another stable
  pre-target identity. This says the reduced recipe itself is not a valid
  output-attribution baseline.
- **H-SingleRouteNondeterminism:** the single arm reaches a different
  pre-target crash or times out after the controls. This distinguishes
  intrinsic route nondeterminism from the paired identical failure but does
  not qualify image output; record the phase and terminal identity for the
  next probe.

The discriminator is the single-run table keyed by
`(audio_mode,trace_level,phase,width,origin,b40,route_state,stable_title,hangar,driver_outcome,crash_or_timeout)`.
Positive controls are startup, one `[missing-func]`, the 640 origins, and the
B40/route-state rows. A missing title/hangar result is valid only after those
controls fire. Do not infer output behavior from this baseline.

## Run

```sh
env ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2259_silent_c88_0_single 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2259_silent_c88_0_single_driver.log 2>&1
```

Record the driver outcome, every 640/1024/512 phase row, B40/route-state
controls, and the terminal crash or timeout. Do not promote the image arm or
add a writeback/consumer guard based on this baseline.
