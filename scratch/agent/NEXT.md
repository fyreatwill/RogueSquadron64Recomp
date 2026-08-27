# NEXT work unit (s2555) — generated-symbol renaming sweep, next bounded region

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Resume the bounded sweep at the next unresolved mission-overlay placeholder,
`0x800E406C`. Enumerate its complete generated span, inspect companion
symbol/m2c/source and caller evidence, and rename only an unambiguous match
through the regeneration-safe symbol path. Leave it unchanged if evidence is
absent. Do not repeat the M4 alias audit or the s2539 retail boundary capture.

## Competing hypotheses and discriminator

- `H-named-match`: the complete region has an exact companion name and can be
  renamed without changing generated behavior.
- `H-no-match`: the complete region has no defensible mapping, so the
  placeholder remains.
- `H-data-boundary`: the region is an embedded-data or conversion boundary,
  not an independently callable game function.
- `H-regeneration-risk`: an apparent name is found but the active symbol or
  fixup path cannot safely carry it.

The discriminator is one region table listing every placeholder, complete
span, candidate, evidence source, confidence, and resulting diff. An exact
human function match plus clean symbol/fixup validation selects H-named-match;
a data/boundary classification selects H-data-boundary; zero exact matches
selects H-no-match; failed regeneration-safe validation selects
H-regeneration-risk. The competing outcomes are mutually actionable: rename,
leave as a boundary, leave as an unresolved callable, or stop before editing
because the rename path is unsafe.

## Exact preflight commands

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
  rg -n 'fake_func_800E406C|800E406C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
  rg -n -C 12 'fake_func_800E406C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -i 'D4EC4|candidate semantic terms' /Users/williambuckley/Documents/Tools/rogue_squadron64/src /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Do not build or rename until the complete region and companion evidence are
defined. Use the synchronized rename pipeline for an exact or clearly local
semantic match; otherwise leave the placeholder unchanged and record why.
