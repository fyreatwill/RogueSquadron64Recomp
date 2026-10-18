# Next work unit: audit the next generated-symbol candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Candidate: `fake_func_800AE3E4`.

* H1: the generated record is a callable function with an independently
  supported semantic name; synchronize its bounded references.
* H2: the companion map or syms table classifies it as a data/splat fragment,
  so no semantic rename is safe.
* H3: the generated tree and existing mapping are already synchronized or
  the address is reused; make no change.

Discriminator: compare the generated body and exact span, the companion
symbol-file classification, the following symbol boundary, `recomp_overlays.inl`,
and the checked-in syms and redefinition mappings. Only an exact callable span
plus independent semantic evidence authorizes H1. If H2 or H3 wins, write the
bounded audit and leave the generated name unchanged.

Run the bounded census first:

`rg -n -C 5 'fake_func_800AE3E4|Preamble' ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files ../rogue_squadron64/tools syms tools/rename`
