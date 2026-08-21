# NEXT work unit (s2120) — one-writer port arm for the mixed retail gate

HYPOTHESIS-ID: m5-guest-gate-ground-truth

## Work unit

Run one same-build, same-recipe image-task A/B with only the
`reapplyDisplayMode` gate store varied through `ROGUESQ_M5_C88_VALUE=0` versus
`1`. Keep `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_SPIN_YIELD=1`, the forced-LLE
wrapper, task fields, output routing, waits, queues, guards, and defaults
unchanged. Arm the existing phase-keyed
`ROGUESQ_LOG_M5_GATE_CONTRACT` census plus all passive audio/PCM breadcrumbs.
The retail oracle result is the first evidence line; this port pair must
provide the second.

## Competing hypotheses and single discriminator

- `H-ReapplyDisplayModeLive`: the retail nonzero writer at `0x8008EC88` is the
  live port gate writer; C88=1 will preserve gate 1 and change downstream
  audio-task, slot/status, or PCM rows relative to C88=0.
- `H-ReapplyWriterNoncausal`: the writer is observed but does not control this
  route at the tested phase; both arms will reach the same target phases and
  have the same downstream contract rows.
- `H-OtherWriter`: another named init/display or failure/shutdown writer later
  overwrites the byte; the gate census will show that writer's value edge and
  the C88 pair will not isolate a downstream split.

The single discriminator is the complete phase-keyed table in both arms:
title/hangar VI coverage, all seven gate-writer rows and final gate value,
audio-task dispatch/exit, slot or status transition, and PCM nonzero/source
rows. C88=1-only downstream activity selects `H-ReapplyDisplayModeLive`;
identical covered rows reject it and select `H-ReapplyWriterNoncausal`; a
later named overwrite selects `H-OtherWriter`. If either arm misses the
target phase or its positive controls, the result is coverage failure and no
hypothesis is selected.

## Exact commands

Build once:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Run both arms concurrently from the repository root:

    env ROGUESQ_SPIN_YIELD=1 GAME_EXTRA_ENV="ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1" zsh scratch/s73_post_a_scene/run_mission_keys.sh s2120_c88_0 30 12 > scratch/agent/s2120_c88_0.launch.log 2>&1 &
    env ROGUESQ_SPIN_YIELD=1 GAME_EXTRA_ENV="ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1" zsh scratch/s73_post_a_scene/run_mission_keys.sh s2120_c88_1 30 12 > scratch/agent/s2120_c88_1.launch.log 2>&1 &
    wait

Inspect only phase-gated rows from
`scratch/s73_post_a_scene/s2120_c88_0/run.log` and
`scratch/s73_post_a_scene/s2120_c88_1/run.log`: `[phase]`, `[m5-gate]`,
`[audtask-dispatch]`, task exit/ABI, slot/status, and PCM boundary/sanity
rows. Do not infer a null from a pre-target crash or a missing positive
control.

No store change, task-contract change, output-routing change, or mitigation
is authorized by this work unit.
