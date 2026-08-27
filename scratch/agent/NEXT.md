# NEXT work unit (s2821) — sweep generated symbols at 0x80161000..0x80163000

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the regeneration-safe companion selector for
`0x80161000..0x80163000`, independently scan the generated tree for
placeholders in that interval, and apply only source-backed semantic names or
mechanical `data_gap_*` classifications for proven non-callable fragments.
Preserve unresolved entries and do not run a game soak.

## Competing hypotheses and discriminator

- H-callable-semantic: a companion semantic symbol maps to a generated
  placeholder, so a semantic rename is justified.
- H-explicit-data-gap: a placeholder is proven to be a non-callable fragment,
  so a mechanical `data_gap_*` rename is justified.
- H-unresolved: candidates are ambiguous or callable semantics are not
  defensible, so their address-encoded names remain.

The discriminator is the complete selector decision table plus the
independent generated-tree scan and each selected body: matching semantic
references select H-callable-semantic; a renamed isolated fragment with no
old-name references selects H-explicit-data-gap; preserved candidates select
H-unresolved.

## Exact commands

```sh
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x80161000 --end-address 0x80163000 --limit 32
rg -n 'func_8016|fake_func_8016' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
git diff --check
```
