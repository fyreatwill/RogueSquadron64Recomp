# NEXT work unit (s2564) — generated-symbol bounded census

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved generated/decomp symbol span after the completed
`0x80102A98` census. Derive the address from the next placeholder in the
project symbol order, then inspect its complete span and immediate named
neighbors. This is static work only: no build, runtime probe, or generated-code
edit.

## Competing hypotheses and discriminator

- `H-human-candidate`: companion symbols, m2c/source, or clear local semantics
  identify a defensible human name for the complete span.
- `H-data-or-boundary`: the span is an instruction fragment or conversion/data
  boundary, so no callable human name is justified.
- `H-already-mapped`: a repository source or companion symbol gives an exact
  existing name that should replace the placeholder.
- `H-uncertain`: evidence conflicts or the span cannot be bounded from the
  available generated/project tables.

The discriminator is a single table containing the exact project/generated
span, instructions, preceding/following symbols, companion symbol result,
exact-address/source/m2c/caller searches, and semantic candidate. A complete
human candidate permits one regeneration-safe symbol rename; a boundary/no-
match result leaves the placeholder unchanged and advances to the next
unresolved address. Conflicting evidence selects `H-uncertain` and makes no
edit.

## Exact preflight

```sh
wc -c < docs/CURRENT-TRUTH.md
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'fake_func_' syms/rogue_squadron.syms.toml | tail -20
rg -n 'fake_func_8010357C|0x8010357C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/syms
```
