# Next work unit: audit the remaining mission-overlay placeholder
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Candidate: `func_800E9AE0`.

* H1: the generated record has an independently supported semantic name;
  synchronize its bounded references.
* H2: the companion or syms entry is only an address-coded/overlay placeholder
  or split fragment, so no semantic rename is safe.
* H3: the generated tree and existing mapping are already synchronized; make
  no change.

Discriminator: compare the generated body and exact span, the companion
symbol-file classification, the following symbol boundary, `recomp_overlays.inl`,
and the checked-in syms and redefinition mappings. Only an exact callable span
plus independent semantic evidence authorizes H1. If H2 or H3 wins, write the
bounded audit and leave the generated name unchanged.

Run the bounded census first:

`rg -n -C 5 'func_800E9AE0|800E9AE0|data_gap_800E9AD8|playStateGatedDestroySound' ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files syms tools/rename`

`rg -n -C 5 'fake_func_800AE3E4|Preamble' ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files ../rogue_squadron64/tools syms tools/rename`
