# NEXT work unit (s2596) — continue the generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Select the next complete bounded placeholder span after the s2595 census,
starting at `0x800CC3D4`, and rename only fragments with a defensible
companion name or clear local semantics. Keep unresolved boundary/data
fragments unchanged. This is a static rename unit; do not run the game or add
runtime probes.

## Competing hypotheses and discriminator

- `H-CompanionMapping`: the span has an exact companion-defined semantic name
  and can be renamed regeneration-safely.
- `H-BoundaryOnly`: the span is incomplete or boundary-only and must remain a
  placeholder.
- `H-ToolMismatch`: rename inputs and generated tables disagree, so the
  source-of-truth path must be repaired before mapping.

The discriminator is a complete static table for `0x800CC3D4`: generated
instruction span and neighboring bodies, companion symbol/comment,
exact-address source/m2c/caller matches, and generated-name coverage. A direct
companion or independent semantic match selects `H-CompanionMapping`; a
complete no-match boundary audit selects `H-BoundaryOnly`; an input/generated
disagreement selects `H-ToolMismatch`.

## Exact checks

1. Inspect `fake_func_800CC038` in `../N64Recomp/RecompiledFuncs/` and the
   matching `../rogue_squadron64/symbol_files/` entry.
2. Add only justified mappings to `tools/rename/build_redefs.py` with
   `apply_patch`.
3. Run `python3 tools/rename/build_redefs.py` and verify expected lines in
   `../rogue_squadron64/build/redefs.txt`.
4. Do not regenerate or build unless a mapping requires generated output.
