# NEXT work unit (s2748) — continue the generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Extend `tools/rename_generated_symbols.py` with the exact fragment mappings
already present in `tools/rename/build_redefs.py` for the bounded region
`0x800B4000` (inclusive) through `0x800B6000` (exclusive), then apply that
batch to `../N64Recomp/RecompiledFuncs`. Do not infer names from implementation
shape, regenerate the tree, or run the game.

## Competing hypotheses and discriminator

- H-verified-fragments-remain: the region contains source-backed fragment
  mappings whose generated placeholders can be renamed.
- H-already-synchronized: companion semantic entries exist, but generated
  references already use them.
- H-ambiguous-or-fake: remaining fragments lack defensible semantic evidence.

The discriminator is the complete candidate table for this interval plus the
`--require-rename` result: a selected mapping must change generated references;
all other candidates must be explicitly classified as synchronized or
ambiguous/fake.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. Inspect the interval with `companion_renames` and the checked-in
   `build_redefs.py` mapping source, without writing.
3. Add only the selected source-backed mappings to `RENAMES`, then run:
   `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x800B4000 --end-address 0x800B6000 --limit 32 --require-rename`
4. Verify old names are absent and new names occur in expected generated
   files; save the full table under `scratch/agent/s2748_generated_symbol_sweep/`.
