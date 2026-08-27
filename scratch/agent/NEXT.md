# NEXT work unit (s2571) — generated-symbol bounded census

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved generated/decomp symbol span at `0x80106BE8`.
Inspect its complete generated span, immediate named neighbors, companion
symbol entry, and exact source/m2c/caller matches. Rename only if the companion
decomp supplies an exact human mapping. If unresolved, advance to the next
placeholder; do not invent a name for a fragment.

## Competing hypotheses and discriminator

- `H-human-candidate`: companion symbols, m2c/source, or clear local semantics identify a defensible human name.
- `H-data-or-boundary`: the span is an instruction fragment or data boundary, so no callable human name is justified.
- `H-already-mapped`: an exact existing repository name should replace the placeholder.
- `H-uncertain`: evidence conflicts or the span cannot be bounded.

The discriminator is one table covering the exact span and instructions,
preceding/following symbols, companion result, exact-address/source/m2c/caller
searches, and semantic candidate. A complete supported candidate selects a
regeneration-safe rename; an explicit companion placeholder plus no exact
candidate selects unchanged and advances to the next placeholder.

## Exact preflight

```sh
wc -c < docs/CURRENT-TRUTH.md
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'fake_func_80106BE8|0x80106BE8' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/syms
```
