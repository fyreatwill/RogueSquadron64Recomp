# Next work unit: M5 de-stubbing Step 1 re-baseline

HYPOTHESIS-ID: m5-audio-step1-rebaseline

Session 4073 ran the clean dummy-silent immediate-versus-7-second-delayed A/B
after the retail whole-RDRAM positive control. Both arms reached title 1024 and
hangar 512 with no crash or abort, so the recipe does not split on launch delay.

Competing hypotheses:

- Himage-contract: the default Factor 5 image arm reaches the complete task,
  DMEM/DMA, SP completion, service/slot, and PCM chain at the target phases.
- Himage-gap: the image performs task work and exits but a named contract edge
  remains absent or divergent from the silent control.
- Hroute-control: retail whole-RDRAM or either port phase gate fails; no audio
  contract conclusion is valid.

Discriminating measurement: one same-build, retail-gated capture with the
default image arm and `ROGUESQ_AUDIO_UCODE=0` silent arm, phase-keyed at title
1024 and hangar 512. Record dispatch, task fields/source, DMEM/DMA, image exit,
SP completion, service return, status/slot, voice/reap, MORT class, PCM source,
PCM consumer, and route phase. Himage-contract requires the complete image row;
Himage-gap is selected by a target-phase missing/divergent edge with the other
controls present; any missing positive control or phase gate selects
Hroute-control.

Exact implementation: use the existing Step 1/default-image validation driver
and add no new counter until the independent retail control and current port
task/PCM joins are confirmed. Run both arms in one build/run from `build/`,
retain `PROBE_PHASE_WIDTH=1024` and `PROBE_KEYS_FROM_PHASE=1`, and SIGKILL the
process group. Keep `ROGUESQ_AUDIO_UCODE=0` as the rollback/control arm.
