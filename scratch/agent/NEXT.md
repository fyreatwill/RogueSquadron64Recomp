# NEXT work unit (s2262) — qualify the silent PCM control

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one single reduced-trace silent+C88=`0` control with the qualified
spin/LLE route and `ROGUESQ_LOG_PCM_BOUNDARY=1`. Keep
`ROGUESQ_LOG_AUDIO_RETURN=1`, B40/route-state tracing, and the phase gate;
omit image audio, task-contract/ABI/DMA, host-boundary, and thread-resume
tracing. This is a route/control qualification run, not an image default or
behavior change.

## Competing hypotheses and discriminator

- **H-SilentControlQualified:** the arm passes startup, one `[missing-func]`,
  the 640 origins, title `1024 @ 0x00790400`, and hangar
  `512 @ 0x006AB400`, then reaches the known post-target termination window.
  Target PCM source/consumer rows, including their zero/nonzero payload
  summaries, are valid controls because the same logger already fired in the
  qualified image arm. This qualifies the silent route for a new pair but
  does not select image behavior.
- **H-SilentRouteInvalid:** the arm fails before title or hangar after the
  startup, `[missing-func]`, and 640 controls. Target PCM nulls are then
  unevaluable and the pair-load/route-instability boundary remains open.
- **H-SilentPcmAbsent:** the arm reaches both target phases but emits no PCM
  source or consumer rows. The route is valid, while the silent stub is
  confirmed not to produce this boundary's target callbacks; future image
  attribution must compare against route controls rather than treating a
  silent PCM null as an image failure.

The discriminating row is
`(startup,missing_func,640_origins,title,hangar,phase,width,origin,pcm_source_rows,pcm_consumer_rows,nonzero_source_rows,nonzero_consumer_rows,first/last PCM tuple,driver_outcome,crash_or_timeout)`.
Any missing target phase selects H-SilentRouteInvalid regardless of PCM
counts. Positive controls are startup, exactly one `[missing-func]`, both 640
route entries, target B40/route-state rows, and the image-arm logger behavior
already established in s2261.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
env ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2262_silent_c88_0_pcm_single 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2262_silent_c88_0_pcm_single_driver.log 2>&1
```

Record the driver result, all phase transitions, B40/route-state controls,
and phase-8/10/12 PCM source/consumer rows. Do not rerun the image arm or
promote `ROGUESQ_AUDIO_UCODE=1` based on this control alone.
