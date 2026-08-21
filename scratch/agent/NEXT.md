# NEXT work unit (s2093)

HYPOTHESIS-ID: m5-audio-arm-validation

## Work unit

Build one binary, then run the default silent-stub control and the opt-in
Factor 5 image-arm treatment from the same eleven-Start driver. Run both arms
concurrently where possible. Keep every passive breadcrumb enabled, phase-gate
the comparison on title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and
do not change the gate, waits, guards, host routing, or default dispatch.

## Competing hypotheses and discriminator

- **H-ImageArmValid** — the opt-in image arm completes `M_AUDTASK` with a
  non-`Broke` exit, preserves the DMEM canary, and produces a valid slot
  transition and nonzero PCM.
- **H-ImageArmStillABIWrong** — the image arm dispatches and changes DMEM but
  still exits `Broke` or fails the canary, with no valid slot/PCM contract.
- **H-StubControlOnly** — the default arm remains silent and the treatment has
  no distinct dispatch/exit evidence, indicating stale configuration or an
  unexercised audio path.
- **H-RouteRegression** — the treatment alone loses a qualified target VI,
  crashes before it, or changes the route; this is a recipe/interaction
  failure, not an audio conclusion.

The discriminator is one same-build A/B table, phase-keyed by VI: per-arm
`audtask-dispatch`, `RspExitReason`, DMEM-canary result, slot-status sequence,
PCM nonzero count, and target-phase coverage. Non-`Broke` plus intact canary
plus valid slot/PCM selects H-ImageArmValid. Dispatch with `Broke`/canary
failure and no valid slot/PCM selects H-ImageArmStillABIWrong. Missing target
phase makes that arm unevaluable; a control-qualified, treatment-only route
failure selects H-RouteRegression. A missing treatment dispatch with no route
failure selects H-StubControlOnly only after the env and binary identity are
verified.

## Exact commands

Build once:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run the two arms concurrently from the repository root, capturing separate
driver logs. The existing driver writes each game log under its tag:

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step2-treatment 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step2-treatment-driver.log 2>&1 &
pid_t=$!
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step2-control 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step2-control-driver.log 2>&1 &
pid_c=$!
wait $pid_t; rc_t=$?
wait $pid_c; rc_c=$?
printf 'treatment_rc=%s control_rc=%s\n' "$rc_t" "$rc_c"
```

Inspect only bounded summaries from both `scratch/s73_post_a_scene/m5-audio-step2-*/run.log` files; do not treat a counter-only hit as success. If either arm is unevaluable, record the missing positive control or target phase and do not alter the port.
