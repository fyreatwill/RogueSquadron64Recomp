# Next work unit: audit and preserve the next newly mapped menu-overlay symbol
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Competing hypotheses:

1. `func_800B2630` has a safe companion mapping to
   `buildFormatMessageGlyphBuffer`, and the mapping should be preserved in the
   regeneration helper.
2. The companion name is stale or belongs to a different address, so changing
   the helper would mislabel generated code.
3. The address is mapped correctly but the generated record is a split/data
   fragment or has no live caller, so it fails the rename gates.

Discriminating measurement: independently compare the companion address,
generated overlay span, generated body start, and generated caller set. Exact
agreement on `0x800B2630`, `0x468`, and a caller selects H1; any disagreement
selects H2/H3 and forbids the mapping change.

Exact commands:

    rg -n -C 3 'buildFormatMessageGlyphBuffer' ../rogue_squadron64/symbol_files/menu_overlay.txt ../N64Recomp/RecompiledFuncs
    git -C ../rogue_squadron64 diff -- symbol_files/menu_overlay.txt

The normal MIPS patch qualification remains parked until a GCC toolchain is
supplied; do not rerun it in this unit.
