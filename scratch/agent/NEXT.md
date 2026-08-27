# NEXT work unit (s2611) — re-baseline the Factor-5 audio task contract

HYPOTHESIS-ID: m5-audio-contract-rebaseline

## Single work unit

Run the plan's Step 1 same-build concurrent A/B: current Factor-5 image
(`ROGUESQ_AUDIO_UCODE=1`, default) versus silent control
(`ROGUESQ_AUDIO_UCODE=0`). Do not change C88, ED48, `0x80094648`, or any
audio behavior. Batch the existing dispatch/task/DMEM-DMA/SP/service/
slot-voice/MORT/PCM controls in one Debug build and phase-gate title and
hangar observations.

## Competing hypotheses and discriminator

- `H-ImageContractHealthy`: image dispatch, task fields, DMEM/DMA, exit, SP
  completion, service/slot/voice, and PCM joins all close in both target phases.
- `H-ImageContractGap`: the image runs and completes, but one downstream
  contract edge is absent while the silent arm remains a valid negative control.
- `H-SilentPathNotIndependent`: the silent arm unexpectedly shows image-only
  downstream work, indicating a route/configuration mismatch.

The discriminator is the complete phase-keyed matrix: image-only task/DMEM/DMA
and downstream rows must be present in the image arm and absent in the silent
arm. Select `H-ImageContractHealthy` only if all joins close; select
`H-ImageContractGap` when image controls stop at a named downstream edge;
select `H-SilentPathNotIndependent` if the silent arm reproduces image-only
work. A phase transition and whole-RDRAM oracle control are mandatory; a PCM
null without those controls is unevaluable.

## Exact checks

1. Before building, arm the oracle whole-RDRAM positive control and record its
   firing; do not add a runtime instrument before that control exists.
2. Run `python3 tools/check_jr_t9_host_return.py` and
   `python3 tools/check_c88_default_store.py`.
3. Build Debug `RogueSquadron64Recomp` only, with no N64Recomp regeneration.
4. Run image and silent arms concurrently from `build/` for 90 seconds,
   SIGKILL both, with the validated AUTOPILOT route, `LLE_FORCE`,
   `SPIN_YIELD`, `LLE_UNGATED`, `LLE_SOLO`, and the phase-scoped complete
   logging set. Capture under `scratch/agent/s2611_*.log`.
5. Report each matrix column per arm and phase: dispatch, task fields/source,
   DMEM/DMA, image exit, SP completion, service, slot/voice/reap, MORT,
   PCM source/consumer, route phase, and crash/abort/missing-function.
