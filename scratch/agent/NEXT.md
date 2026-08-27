# NEXT work unit (s2590) — continue the generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Select the next complete bounded placeholder span after the s2589 census and
rename only fragments with a defensible companion name or clear local
semantics. Keep unresolved boundary/data fragments unchanged. This is a
static rename unit; do not run the game or add runtime probes.

## Competing hypotheses and discriminator

- `H-CompanionMapping`: the next span has an exact companion-defined semantic
  name and can be renamed regeneration-safely.
- `H-BoundaryOnly`: the next span is an incomplete/boundary fragment with no
  defensible name and must remain a placeholder.
- `H-ToolMismatch`: the rename input and generated tables disagree, so the
  mapping cannot be landed until the source-of-truth path is corrected.

The discriminator is a complete static table for the selected span: exact
address and instruction span in generated C, companion symbol/comment, source
or m2c match, and generated-name coverage. A direct companion match selects
`H-CompanionMapping`; a complete no-match audit selects `H-BoundaryOnly`; any
input/generated disagreement selects `H-ToolMismatch`. Verify the generator
emits every selected mapping and no unrelated mapping changes.

## Exact preparation and checks

1. Inspect the next placeholder, beginning at `0x800B2628`, in `../N64Recomp/RecompiledFuncs/` and the
   matching `../rogue_squadron64/symbol_files/` entry.
2. Add only justified mappings to `tools/rename/build_redefs.py` with
   `apply_patch`.
3. Run `python3 tools/rename/build_redefs.py` and verify the expected lines in
   `../rogue_squadron64/build/redefs.txt`.
4. Do not regenerate or build unless the mapping requires generated output;
   if it does, use make_elf.py → N64Recomp → fixup_game_funcs.py → CMake.
