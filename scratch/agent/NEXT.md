# NEXT work unit (s2530) — generated-symbol renaming sweep, next bounded region

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Continue the sweep with the next unresolved main-overlay placeholder,
`0x80082268`, in one complete bounded-region census. Enumerate its exact
generated span, inspect companion symbol/m2c/source and caller evidence, and
rename only an unambiguous match through the regeneration-safe path. Leave it
unchanged if evidence is absent. Do not build unless a rename or tooling
repair is actually made.

## Competing hypotheses and discriminator

- `H-named-match`: the complete region has an exact companion name and can be
  renamed without changing generated behavior.
- `H-no-match`: the complete region has no defensible mapping, so the
  placeholder remains.
- `H-regeneration-risk`: an apparent name is found but the active symbol or
  fixup path cannot safely carry it.

The discriminator is the complete region table listing every placeholder,
span, candidate, evidence source, confidence, and resulting diff. An exact
match plus clean symbol/fixup validation selects `H-named-match`; zero exact
matches selects `H-no-match`; failed regeneration-safe validation selects
`H-regeneration-risk`.

## Exact preflight commands

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'fake_func_80082268|80082268' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
rg -n -C 8 'fake_func_80082268' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -i '82268|candidate semantic terms' /Users/williambuckley/Documents/Tools/rogue_squadron64/src /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Do not build or rename until the region and companion evidence are defined.
