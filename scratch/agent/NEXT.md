# NEXT work unit (s2527) — generated-symbol renaming sweep, next bounded region

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

The region `0x80079CD8–0x80079CD8` was completely censused and had one
8-byte boundary placeholder with no companion mapping. Continue the same
sweep with exactly one new bounded region around the next unresolved
main-overlay placeholder after `0x80079CD8` (currently `0x8007A0E8`). Before
starting, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

If all 15 titles are sweep-scoped, revisit CURRENT-TRUTH Next step #2 or the
M4 accumulator boundary with a genuinely new angle. Otherwise enumerate the
complete selected interval, find matching named functions or m2c output in the
companion `rogue_squadron64` tree, and rename only unambiguous matches through
the regeneration-safe symbol/fixup path. Do not invent names or edit unrelated
generated functions. The prior results are in
`scratch/agent/s2518_symbol_census/audit.md`,
`scratch/agent/s2519_symbol_census/audit.md`,
`scratch/agent/s2521_symbol_census/audit.md`,
`scratch/agent/s2522_symbol_census/audit.md`,
`scratch/agent/s2523_symbol_census/audit.md`,
`scratch/agent/s2524_symbol_census/audit.md`, and
`scratch/agent/s2525_symbol_census/audit.md`.

## Competing hypotheses and discriminator

- `H-named-match`: the selected region has exact companion names and can be
  renamed without changing generated behavior.
- `H-no-match`: the complete region census has no defensible mappings, so
  placeholders stay.
- `H-regeneration-risk`: apparent names are not connected to the active
  generation/fixup path, requiring a tooling repair before renaming.

The discriminator is the complete region table of every placeholder address,
candidate symbol, evidence source, confidence, and resulting diff. An exact
match plus clean symbol/fixup validation selects `H-named-match`; zero exact
matches selects `H-no-match`; a failed regeneration-safe validation selects
`H-regeneration-risk`.

## Exact preflight commands

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'func_0x8007A0E8|fake_func_8007A0E8|8007A0E8' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
rg -n -C 8 'fake_func_8007A0E8' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -i '7A0E8|candidate semantic terms' /Users/williambuckley/Documents/Tools/rogue_squadron64/src /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Do not build or rename until the region and its companion evidence are
defined. If names are changed, build the affected target and confirm no
generated placeholder references are left dangling.
