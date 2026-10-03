# Next work unit: M5 Step 1 audio-contract qualification

HYPOTHESIS-ID: m5-step1-contract-qualification

The native task-data value thread is parked after three consecutive paired
captures without a real-arm target fault. Do not add another page-watch field.

Competing hypotheses:

- `H-M5-ContractComplete`: the current image arm reaches the full task-to-PCM
  contract at title/hangar; the remaining defects are downstream rendering.
- `H-M5-ContractGap`: image DMEM/DMA and completion occur, but one named guest
  service, slot/status, voice/reap, MORT, or PCM edge is absent.
- `H-M5-RouteInstability`: the real image arm fails before the target phase, so
  downstream nulls remain unevaluable.

Discriminator: one same-build concurrent real/silent run with phase-gated
title/hangar rows containing dispatch, task fields/source, DMEM/DMA, image
exit, SP completion, service, slot/status, voice/reap, MORT, PCM source and
consumer joins, plus whole-RDRAM and route positive controls. A complete row
selects `H-M5-ContractComplete`; a complete target row with exactly one missing
edge selects `H-M5-ContractGap`; no real target row selects
`H-M5-RouteInstability` and keeps downstream nulls unevaluable.

Build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the existing validated real/silent phase-gated recipe from `build/` with
`ROGUESQ_AUDIO_UCODE=1/0`, LLE-solo, spin-yield, autopilot,
`PROBE_PHASE_WIDTH=1024`, and `PROBE_KEYS_FROM_PHASE=1`. Retain the existing
M5 dispatch/task/DMA/service/slot/voice/MORT/PCM logs and SIGKILL cleanup.
