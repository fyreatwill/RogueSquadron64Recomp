# NEXT work unit (s2567) — generated-symbol bounded census

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved generated/decomp symbol span at
`0x801044D8–0x801044DF`. Inspect its complete project/generated span and
immediate named neighbors. This is static work only: no build, runtime probe,
or generated-code edit.

## Competing hypotheses and discriminator

- `H-human-candidate`: companion symbols, m2c/source, or clear local semantics
  identify a defensible human name for the complete span.
- `H-data-or-boundary`: the span is an instruction fragment or data boundary,
  so no callable human name is justified.
- `H-already-mapped`: an exact existing repository name should replace the
  placeholder.
- `H-uncertain`: evidence conflicts or the span cannot be bounded.

The discriminator is one table covering the exact span and instructions,
preceding/following symbols, companion result, exact-address/source/m2c/caller
searches, and semantic candidate. Only a complete supported candidate permits
a regeneration-safe rename; otherwise leave the placeholder unchanged and
advance.

## Exact preflight

```sh
wc -c < docs/CURRENT-TRUTH.md
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'fake_func_801044D8|0x801044D8' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/syms
```
