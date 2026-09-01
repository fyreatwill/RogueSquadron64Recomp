# NEXT work unit — qualify the complete M5 audio task contract

HYPOTHESIS-ID: m5-audio-step1-image-silent-qualification

Run one same-build, phase-gated qualification of the current default
`factor5_ucode_b` image arm against the explicit silent `musyx_stub` control.
Do not change behavior, gates, slot values, PCM, or output. Identify one
missing contract edge before any de-stub.

Competing hypotheses and discriminator:

- H-AudioContractComplete: image and silent arms both reach title/hangar with
  expected task/SP/service/slot/PCM rows; no contract edge is selected.
- H-ImageTaskContractGap: image DMEM/DMA and `Broke`/SP completion are live,
  but a task-field, service, slot, voice, or PCM join is absent at target VI.
- H-AudioRouteOnly: one arm fails before title while controls show the route is
  not phase-valid; target-phase audio nulls are unevaluable.

The single discriminator is one phase-keyed A/B row containing dispatch, task
fields/source, DMEM/DMA, image exit, SP completion, service return,
status/slot, voice/reap, MORT class, PCM source/consumer, and route phase.
Both arms must be built together and each must visibly fire the positive
controls: port route controls, title 1024, and hangar 512.

Required source/config checks before building:

    rg -n "ROGUESQ_AUDIO_UCODE|musyx_stub|factor5_ucode_b|audtask-dispatch|sp-complete|pcm-boundary|MORT" src lib docs tools
    sed -n '180,260p' docs/M5-AUDIO-PLAN.md

Build and run both arms from `build/`, using `ROGUESQ_AUDIO_UCODE=0` only for
the silent control. Preserve passive breadcrumb env vars, phase-gate on VI
transitions, capture under `scratch/agent/soak_results/`, and terminate each
game/process group with SIGKILL. Do not interpret a pre-title null as evidence
for H-ImageTaskContractGap.
