# NEXT work unit (s2535) — generated-symbol renaming sweep, next bounded region

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Continue the sweep at the next unresolved main-overlay placeholder,
`0x80099C4C`. Enumerate its complete generated span, inspect companion
symbol/m2c/source and caller evidence, and rename only an unambiguous match
through the regeneration-safe symbol path. Leave it unchanged if evidence is
absent. Do not repeat `0x80097D58`, `0x8009711C`, `0x80094348`, `0x80093E74`, or the already-closed
`0x80082268`/`0x800825C8` pair.

## Competing hypotheses and discriminator

- `H-named-match`: the complete region has an exact companion name and can be
  renamed without changing generated behavior.
- `H-no-match`: the complete region has no defensible mapping, so the
  placeholder remains.
- `H-regeneration-risk`: an apparent name is found but the active symbol or
  fixup path cannot safely carry it.

The discriminator is one region table listing every placeholder, span,
candidate, evidence source, confidence, and resulting diff. An exact match
plus clean symbol/fixup validation selects `H-named-match`; zero exact matches
selects `H-no-match`; failed regeneration-safe validation selects
`H-regeneration-risk`.

## Exact preflight commands

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'fake_func_80099C4C|80099C4C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
rg -n -C 8 'fake_func_80099C4C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -i '99C4C|candidate semantic terms' /Users/williambuckley/Documents/Tools/rogue_squadron64/src /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Do not build or rename until the complete region and companion evidence are
defined.
