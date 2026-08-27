# NEXT work unit (s2557) — generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Resume the bounded sweep at unresolved mission-overlay placeholder
`0x800E447C`. Enumerate its complete generated span and inspect companion
symbol, m2c, source, and caller evidence. Rename only an exact or clearly
local semantic match through the regeneration-safe symbol path; otherwise
leave it unchanged and record the boundary classification. The M4 revisit is
parked until a new phase-gated runtime index capture is justified.

## Competing hypotheses and discriminator

- `H-named-match`: exact companion or unambiguous local semantics support a
  regeneration-safe rename.
- `H-no-match`: no defensible human mapping exists.
- `H-data-boundary`: the span is embedded data, a thunk, or a conversion
  boundary rather than an independent callable function.
- `H-regeneration-risk`: evidence suggests a name, but the active symbol/fixup
  path cannot safely carry it.

The discriminator is one complete region table listing every placeholder,
span, body, candidate, evidence source, confidence, and resulting diff. The
outcome selects rename, unchanged boundary, unchanged unresolved symbol, or
stop before editing if the rename path is unsafe.

## Exact preflight commands

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'fake_func_800E447C|800E447C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
rg -n -C 12 'fake_func_800E447C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -i 'candidate semantic terms' /Users/williambuckley/Documents/Tools/rogue_squadron64/src /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Do not build until the complete region and evidence table are defined. If a
rename is selected, use the existing synchronized rename pipeline and build
the affected target to validate the generated declaration/implementation and
overlay table.
