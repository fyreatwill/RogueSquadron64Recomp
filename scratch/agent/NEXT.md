# NEXT work unit (s2700) — bounded generated-symbol source reconciliation

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Reconcile the next bounded generated region, `0x80092000..0x80093000`, against
companion source/m2c material. Select up to 32 names only when the companion
gives an exact semantic name for the generated function at the same address
and the destination is unique. Preserve `func_800927B0`, `func_80092A54`, and
fake fragments unless source evidence closes their identities.

## Competing hypotheses and discriminator

- `H-region-has-exact-names`: the bounded region contains exact, unique
  companion/source names and a rename batch can be landed.
- `H-region-is-address-only`: the region has no defensible human names; leave
  it unchanged and choose the next region.
- `H-ambiguous-companion`: companion names collide or already exist; preserve
  the affected entries and report the collision.

The discriminator is the bounded source/m2c-to-generated address table plus
the tool's selected mapping/count: positive count with unique destinations
selects `H-region-has-exact-names`; no defensible name selects
`H-region-is-address-only`; a collision/error selects
`H-ambiguous-companion`.

## Exact commands

1. `python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --limit 32`
2. Verify changed files and remaining placeholder/mapping counts with `git -C
   /Users/williambuckley/Documents/Tools/N64Recomp diff --stat` and bounded
   `rg` queries; no game build/run is needed for this metadata-only batch.
