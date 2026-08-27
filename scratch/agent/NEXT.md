# NEXT work unit (s2521) — generated-symbol renaming sweep, next bounded region

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

The previous region `0x80005570–0x8000595C` was completely censused and had
one isolated placeholder with no companion mapping. Continue the same sweep
with exactly one new bounded region around the next unresolved placeholder:
main-overlay `0x80006BFC–0x80006BFC`. Before starting, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

If all 15 titles are sweep-scoped, revisit CURRENT-TRUTH Next step #2 or the
M4 accumulator boundary with a genuinely new angle. Otherwise enumerate the
complete selected interval, find matching named functions or m2c output in the
companion `rogue_squadron64` tree, and rename only unambiguous matches through
the regeneration-safe symbol/fixup path. Do not invent names or edit unrelated
generated functions. The prior results are in
`scratch/agent/s2518_symbol_census/audit.md` and
`scratch/agent/s2519_symbol_census/audit.md`.

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
rg -n '^void func_|^static .*func_|func_0x[0-9A-Fa-f]+' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -200
rg --files /Users/williambuckley/Documents/Tools/rogue_squadron64 | head -100
```

Do not build or rename until the region and its companion evidence are
defined. If names are changed, build the affected target and confirm no
generated placeholder references are left dangling.
