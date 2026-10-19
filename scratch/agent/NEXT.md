Single next work unit: perform one bounded generated-symbol audit for the next
remaining live placeholder, `fake_func_800AE3E4`. Use the companion decomp map,
generated function span/callers, and `syms/rogue_squadron.syms.toml`; rename only
when all three agree on a semantic function and exact span. If the record is a
data gap, invalid fragment, or lacks a semantic companion, leave it unchanged
and record that classification.

Competing hypotheses and discriminator:

1. H1: the candidate has a companion-backed semantic name and exact generated
   span; a regeneration-safe rename is justified.
2. H2: the candidate is a gap/fragment or the independent span disagrees; no
   rename is justified.
3. H3: the candidate is already synchronized or cannot be resolved from the
   three sources; the sweep lead is exhausted and must pivot.

The discriminator is the three-source exact-span table for that one candidate;
do not build or run the game. Inspect candidates with the existing sweep tools
and write a bounded audit under `docs/RENAME-S5573.md`.

Expected commands:

    rg -n --glob 'funcs_*.c' '^RECOMP_FUNC void (func_|fake_func_)' ../N64Recomp/RecompiledFuncs | head -1
    rg -n '800AE3E4|fake_func_800AE3E4|func_800AE3E4' ../rogue_squadron64 syms tools ../N64Recomp/RecompiledFuncs
    sed -n '<bounded-window>p' ../N64Recomp/RecompiledFuncs/funcs_<N>.c

HYPOTHESIS-ID: generated-symbol-renaming-sweep
