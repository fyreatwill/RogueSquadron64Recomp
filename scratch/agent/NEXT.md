# Next work unit: audit and preserve the next newly mapped menu-overlay symbol
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Competing hypotheses:

1. The next newly mapped menu-overlay symbol has a safe companion mapping and
   should be preserved in the regeneration helper.
2. The companion name is stale or belongs to a different address, so changing
   the helper would mislabel generated code.
3. The address is mapped correctly but the generated record is a split/data
   fragment or has no live caller, so it fails the rename gates.

Discriminating measurement: independently compare the companion address,
generated overlay span, generated body start, and generated caller set. Exact
agreement selects H1; any disagreement selects H2/H3 and forbids the mapping
change.

Exact commands:

    rg -n -C 3 '<candidate-name>' ../rogue_squadron64/symbol_files/menu_overlay.txt ../N64Recomp/RecompiledFuncs
    git -C ../rogue_squadron64 diff -- symbol_files/menu_overlay.txt

    python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address <start> --end-address <end> --limit 1

The normal MIPS patch qualification remains parked until a GCC toolchain is
supplied; do not rerun it in this unit.
