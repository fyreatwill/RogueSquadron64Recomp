# NEXT work unit (s2376) — M5 A1 successor-PC boundary

HYPOTHESIS-ID: m5-a1-rs-free-successor-boundary

## Work unit

Run one bounded source-level control-flow audit of `rs_free` around
`0x80001CAC..0x80001CD8F`, comparing the companion retail disassembly/decomp
with the generated port body and the s2375 runtime rows. Do not build or
change game behavior, dispatch, VI selection, task data, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-GeneratedControlFlowDiffers: the generated body contains a real branch or
  instruction-path difference corresponding to the retail `0x80001CB4`
  successor.
- H-InputDependentPath: the generated and retail bodies are equivalent, and
  the different successor is explained by differing live register/input state.
- H-ProbeLabelArtifact: the source instruction mapping shows that `0x80001CD8F`
  is not the successor represented by the runtime marker.

The discriminator is the first instruction/branch after the shared
`0x80001CAC -> 0x80001CB0` prefix: a matching retail/port instruction with
different live inputs selects `H-InputDependentPath`; a generated branch or
instruction mismatch at that boundary selects `H-GeneratedControlFlowDiffers`;
an address/label mismatch selects `H-ProbeLabelArtifact`.

## Exact commands

    rg -n -C 24 '0x80001CAC|0x80001CB0|0x80001CB4|0x80001CD8' ../N64Recomp/RecompiledFuncs/funcs_0.c ../rogue_squadron64
    sed -n '1,120p' syms/rogue_squadron.syms.toml
    grep -a -E 'pc=0x80001(CAC|CB0|CB4|CD8F)' scratch/agent/s2375_m5_a1_rs_free_internal_join/{control,alternate}.log | head -80

The driver must SIGKILL each port arm after its abort marker and must report
counts for every internal PC plus all controls.
