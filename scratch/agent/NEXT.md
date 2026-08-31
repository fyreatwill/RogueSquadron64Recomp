# NEXT work unit — trace the earlier port frequency-input boundary

HYPOTHESIS-ID: m5-frequency-writer-contract

Session 3437 compared the normalized field family at the actual common
`osRecvMesg` entry `0x800331D0`. Retail had 7,815 phase-qualified rows across
both title origins; the fresh-build port image arm had 107 distinct rows and
zero exact intersection. This selects an earlier port input/dispatch gap at
the observed boundary.

Competing hypotheses and the single discriminating measurement:

- `H-EarlierPortInputGap`: the retail-observed tuple family is absent at the
  port-side producer/caller before `osRecvMesg_recomp`.
- `H-PortWrapperContractGap`: a retail-observed tuple is present before the
  wrapper but is changed or lost at wrapper entry.
- `H-EarlierBoundaryUnevaluable`: the producer/caller census has no usable
  phase-qualified rows despite live phase and route controls.

First add one phase-scoped caller/producer census at the generated callsites
that feed `osRecvMesg_recomp`, recording the same six normalized fields and a
monotonic join ordinal. Keep the existing wrapper-entry census enabled. Build
once with `cmake --build build --config Debug --target RogueSquadron64Recomp`,
then run from `build/` using the Session 3436 recipe, adding the new caller
instrument env var and capturing to
`scratch/agent/s3438_m5_frequency_input/run.log`; stop after the 512 phase and
SIGKILL the game. Compare the caller set against the retail entry set and
against the wrapper-entry set in the same run. Caller absence selects
`H-EarlierPortInputGap`; caller presence followed by wrapper divergence selects
`H-PortWrapperContractGap`; no usable caller rows with controls live selects
`H-EarlierBoundaryUnevaluable`. Do not change waits, slots, dispatch, clear
behavior, or PCM writeback.
