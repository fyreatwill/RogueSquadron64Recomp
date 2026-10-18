# Next work unit: audit the next generated-symbol candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Candidate: `fake_func_800B75C4`.

* H1: the generated short record is the exact callable preamble represented
  by the companion's `playerYwingInit` boundary; rename its bounded references.
* H2: the companion map's invalid/splat classification means it is a data
  fragment before `playerYwingInit`, so no semantic rename is safe.
* H3: the generated tree and existing mapping are already synchronized or
  the address is reused; make no change.

Discriminator: compare the generated prologue and exact span, companion
`symbol_files/mission_overlay.txt` classification, the following
`playerYwingInit` boundary, `recomp_overlays.inl`, and the checked-in syms and
redefinition mappings. Only an exact preamble span plus independent semantic
evidence authorizes H1. If H2 or H3 wins, write the bounded audit and leave the
generated name unchanged.

Run the bounded census first:

`rg -n -C 5 'fake_func_800B75C4|playerYwingInit|Preamble' ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files ../rogue_squadron64/tools syms tools/rename`
