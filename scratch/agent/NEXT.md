# NEXT work unit (s2285) — M5 Step 1 full audio-contract pair

HYPOTHESIS-ID: m5-step1-audio-contract

## Work unit

Run one same-build, phase-gated silent/image validation pair for the complete
M5 Step 1 row. Keep the runtime default unchanged: the silent arm uses
`ROGUESQ_AUDIO_UCODE=0`, and the Factor 5 image arm uses
`ROGUESQ_AUDIO_UCODE=1`. Use the qualified route settings
`ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, `ROGUESQ_M5_C88_VALUE=0`, and the eleven-Start schedule.
Start the silent arm first and launch the image arm only after the silent arm
reaches `512 @ 0x006AB400`; this is the route-qualified stagger, not a live
overlap test. Keep one independently gated retail oracle for the entire pair.

The row must contain, per arm and phase: `M_AUDTASK` dispatch and exit, task
fields/source hash, DMEM change and DMA/readback ranges, image completion and
SP completion, service entry/return, status `01/02/00` and status-`03` reaping,
voice-array/reap activity, MORT descriptor class, PCM source/consumer joins,
and route phase. Do not flip a default or change a guard from this run.

## Competing hypotheses and discriminating measurement

- H-AudioDegeneracy: both arms qualify the route, and the real image task
  produces a new downstream service, slot, voice/reap, or PCM edge that the
  silent stub lacks. This selects an audio-disabled degenerate-path effect.
- H-ContractGap: the image arm shows real DMEM/DMA work, completion, and SP
  delivery, but a task/output/service/slot/PCM join remains absent or mismatched.
  This selects the missing contract edge and keeps the image opt-in.
- H-MixedPipelines: RSP image rows close while MORT descriptor/voice/PCM rows
  remain an independent CPU-side pipeline, so no global audio-default change
  follows from the RSP result.
- H-RouteInvalid: the oracle, port controls, or either target phase is absent;
  all audio nulls from that arm are unevaluable and the pair must be rerun with
  a route fix rather than interpreted.

The single discriminating table is keyed by `(arm, phase, task_seq)` plus task
field tuple/hash, DMEM hash/nonzero count, DMA ranges, image exit, SP-complete
edge, service return, slot/status transition, voice/reap event, MORT class, and
PCM source/consumer tuple. A result selects among the hypotheses only when the
retail whole-RDRAM control is at least `10,000` writes, the oracle reaches both
title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and both port arms pass
their route controls and reach the target phase. A `Broke` return or a branch
counter by itself is not a positive control.

## Exact commands

1. Create `scratch/agent/run_s2285_m5_step1_contract_pair.sh` with
   `apply_patch`. Base its process/watchdog and silent-first/image-after-hangar
   gate on the corrected s2272 driver. Gate the oracle before launching the
   port arm, as in s2284. Arm the existing task, DMA, image-stage, service,
   slot/voice, MORT, PCM-boundary, B40, route-state, and phase diagnostics in
   one build; do not add a one-off generated-file probe.
2. Check syntax:
   `zsh -n scratch/agent/run_s2285_m5_step1_contract_pair.sh`
3. Run from the repository root:
   `zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2285_m5_step1_contract_pair`
4. Summarize with bounded `grep`/`tail` only: oracle positive controls, both
   port route controls, title/hangar gates, task/DMA/SP/service/slot/voice/MORT/
   PCM rows by phase, and terminal crash/timeout. Do not interpret a missing
   downstream row from an arm that lacks its route gate.
