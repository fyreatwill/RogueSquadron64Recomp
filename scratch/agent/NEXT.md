# NEXT work unit — define a patches-only null-consumer recovery contract

HYPOTHESIS-ID: m3-musyx-pointer-class-audit

Session 3239 selected `H-NullConsumer`: `rs_malloc` can return zero and
`allocateSongChannelArray` publishes it without checking. The next unit is a
bounded contract audit for a patches-only consumer guard. Do not change
`rs_malloc` globally and do not add a runtime instrument.

## Competing hypotheses

- `H-SkipVoice`: a null channel pointer can be detected at the command-list
  consumer and safely skip only that voice, preserving list state.
- `H-ReinitArray`: the correct recovery is to rerun or reinitialize the whole
  channel array, so a local consumer skip would leave inconsistent state.
- `H-NotPatchable`: no semantics-preserving recovery can be established from
  the available generated code; leave the class as a documented static risk.

## Discriminator

Recover the complete `musyxBuildVoiceCommandList` loop and its caller contract,
including list-head/count updates and the voice-index progression. If the
null path has a local skip that preserves all list invariants, implement one
override under `patches/` with an `ORIGIN:` naming `0x8008F228` as the writer.
If recovery requires array-wide state, document the required reinitialization
edge and do not patch this iteration. If neither can be proven, select
`H-NotPatchable` and close the class as a static unresolved risk.

## Exact commands

1. `sed -n '5140,5485p' ../N64Recomp/RecompiledFuncs/funcs_24.c` and map every
   list-head/count write and loop exit in `musyxBuildVoiceCommandList`.
2. `rg -n -B20 -A30 'musyxBuildVoiceCommandList\\(rdram|0x80091034|0x80091060|0x80091074|0x8009123C' ../N64Recomp/RecompiledFuncs/funcs_24.c` and identify
   caller arguments and post-call assumptions.
3. If a local recovery is proven, add only the corresponding `patches/`
   override, build `PatchesLib`, then full-link and validate. Otherwise write
   `scratch/agent/s3240_m3_musyx_null_contract.md` with the selected outcome.
