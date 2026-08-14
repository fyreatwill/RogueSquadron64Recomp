# NEXT work unit (s1171)

HYPOTHESIS-ID: musyx-downstream-operation-census

Perform one bounded static census of the complete downstream operation idiom
in `musyxSynthFrame` after the s1170 callback census selected H2. Do not build,
run, or add a mitigation in this unit.

Competing hypotheses and discriminator:

- H1: a bounded voice-array, sample-pointer, or resampling operation produces
  the wild value behind the known `0x8000B650` fault family.
- H2: command-list construction or host/RSP submission produces it after the
  voice/sample operations have completed.
- H3: the static census cannot tie the fault to an operation family because a
  source or destination path remains unresolved.

The discriminating measurement is one complete operation table for every
operation family after the `musyxSynthFrame` callback entry: caller/guest PC,
source operands, array/index bounds, pointer formation, destination writes,
and the first operation capable of producing the known fault value. H1 or H2
requires a specific writer plus a legitimate/illegitimate assessment; H3 is
the outcome if any in-scope path remains unresolved.

Exact commands:

    rg -n "musyxSynthFrame|0x800912|LOOKUP_FUNC|musyxMixActiveVoices|musyxRenderVoiceSamples|musyxBuildVoiceCommandList|submit|MEM_[WHD]" ../N64Recomp/RecompiledFuncs/funcs_24.c
    sed -n '4266,5560p' ../N64Recomp/RecompiledFuncs/funcs_24.c
    sed -n '3570,4265p' ../N64Recomp/RecompiledFuncs/funcs_24.c
    rg -n "^(musyxSynthFrame|musyxMixActiveVoices|musyxRenderVoiceSamples|musyxBuildVoiceCommandList)\s*=" ../rogue_squadron64/symbol_files/*.txt

Record operation-family row counts, unresolved rows, first possible writer,
and legitimate/illegitimate classification in the next ledger entry. If the
table cannot identify a writer, do not add a guard; choose the next
ground-truth or source-census discriminator.
