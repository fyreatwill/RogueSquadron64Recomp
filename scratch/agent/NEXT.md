# NEXT work unit (s2603) — locate the next generated-symbol sweep span

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Select the next unresolved generated-symbol placeholder after `0x800E406C`,
using the generated overlays and companion symbol files to identify the next
segment/address. Rename only fragments with a defensible companion name or
clear local semantics. The next expected address is `0x800E447C`. Keep
unresolved boundary/data fragments unchanged. This is a static rename unit; do
not run the game or add runtime probes.

## Competing hypotheses and discriminator

- `H-CompanionMapping`: the span has an exact companion-defined semantic name
  and can be renamed regeneration-safely.
- `H-BoundaryOnly`: the span is incomplete or boundary-only and must remain a
  placeholder.
- `H-ToolMismatch`: rename inputs and generated tables disagree, so the
  source-of-truth path must be repaired before mapping.

The competing hypotheses are recorded before inspection; the discriminator is
the static address/span table below, not the placeholder's mere execution.

The discriminator is a complete static table for the selected address:
generated instruction span and neighboring bodies, companion symbol/comment,
exact-address source/m2c/caller matches, and generated-name coverage. A direct
companion or independent semantic match selects `H-CompanionMapping`; a
complete no-match boundary audit selects `H-BoundaryOnly`; an input/generated
disagreement selects `H-ToolMismatch`.

## Exact checks

1. Enumerate unresolved `fake_func_*` entries in
   `../N64Recomp/RecompiledFuncs/` and companion symbol files, sorted by
   address, then inspect the first span after `0x800E406C` (currently expected
   at `0x800E447C`).
2. Add only justified mappings to `tools/rename/build_redefs.py` with
   `apply_patch`.
3. Run `python3 tools/rename/build_redefs.py` and verify expected lines in
   `../rogue_squadron64/build/redefs.txt`.
4. Do not regenerate or build unless a mapping requires generated output.
