# NEXT work unit (s2591) — continue the generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Select the next complete bounded placeholder span after the s2590 census and
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

The discriminator for this iteration is a complete static table for
`0x800C5898`: exact generated instruction span and neighbouring bodies,
companion symbol/comment, exact-address source/m2c/caller matches, and
generated-name coverage. A direct companion or independent semantic match
selects `H-CompanionMapping`; a complete no-match boundary audit selects
`H-BoundaryOnly`; an input/generated disagreement selects `H-ToolMismatch`.

Expected outcomes for the selected span:

- `H-CompanionMapping`: add only a defensible regeneration-safe mapping and
  verify its emitted line.
- `H-BoundaryOnly`: leave the placeholder unchanged and record the complete
  no-match table.
- `H-ToolMismatch`: stop the rename and repair only the source-of-truth path.

The prior span's table is retained below as the s2590 record:

| Item | Observation | Outcome |
|---|---|---|
| Generated span | `funcs_30.c`: `0x800B2628` `lwc1` and `0x800B262C` `swc1`; 8 bytes total | bounded fragment, not a complete body |
| Neighbours | complete `playExitSoundAndToggleScreenMeshes` ends at `0x800B2624`; complete `buildFormatMessageGlyphBuffer` starts at `0x800B2630` | boundary fragment |
| Companion input | `fake_func_800B2628 = 0x800B2628`; no comment or semantic alias | no direct mapping |
| Independent search | no exact-address source, m2c, caller, or symbol alias beyond the placeholder | no defensible inferred name |
| Generator coverage | `build_redefs.py` emits no mapping for this placeholder; existing mappings remain unchanged | rejects tool mismatch |

A direct companion or independent semantic match would select
`H-CompanionMapping`; the complete no-match table selects `H-BoundaryOnly`; an
input/generated disagreement would select `H-ToolMismatch`. No mapping is
justified for this span.

## Exact preparation and checks

1. Inspect `fake_func_800C5898` in `../N64Recomp/RecompiledFuncs/` and the
   matching `../rogue_squadron64/symbol_files/` entry.
2. Add only justified mappings to `tools/rename/build_redefs.py` with
   `apply_patch`.
3. Run `python3 tools/rename/build_redefs.py` and verify the expected lines in
   `../rogue_squadron64/build/redefs.txt`.
4. Do not regenerate or build unless the mapping requires generated output;
   if it does, use make_elf.py → N64Recomp → fixup_game_funcs.py → CMake.
