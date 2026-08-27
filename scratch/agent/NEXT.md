# NEXT work unit (s2668) — continue generated-symbol-renaming-sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Use `tools/rename_generated_symbols.py` after each generated-tree refresh.
The seven-name batch from s2668 is complete; select the next batch only after
comparing the generated definitions with `syms/rogue_squadron.syms.toml` and
the companion `../rogue_squadron64/symbol_files/`. Do not invent names: leave
an address generic when the companion evidence is absent or ambiguous.

## Competing hypotheses and discriminator

- `H-symbol-map-complete`: every generated placeholder in the selected batch
  has an exact companion address/name match and can be renamed safely.
- `H-symbol-map-partial`: only some placeholders have exact matches; rename
  those and leave the remainder generic.
- `H-symbol-tree-stale`: the generated tree has no matching placeholders, so
  the batch must be deferred until regeneration rather than forcing edits.

The discriminator is one address-keyed census of generated definitions joined
to both symbol sources. Exact address/name agreement selects a rename;
missing or conflicting names select a documented hold. The post-edit check
must show zero old-name references and exactly one definition for each new
name.

## Exact commands

1. `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs`
2. `rg -n 'fake_func_800(82268|825C8|AD378|D2C98|D4EC4|DD2C4|DFB8C)' ../N64Recomp/RecompiledFuncs`
3. `rg -n 'cheatCodeConstantPreamble|rspbootTextPreamble|storeTrackedObjectAuxiliaryFields|duplicateSymbolPrefixForNpcInitWithMotionParams|duplicateSymbolPrefixForNpcInitChildLinkedToParent|duplicateSymbolPrefixForNpcInitFullModel|duplicateSymbolPrefixForApplyCraftAnimAndDetailParams' ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/funcs_*.c`

Expected outcome: the first command reports seven renamed batches with no
missing targets; the second returns no matches; the third reports one
definition and all callsites for each replacement. No runtime behavior or
audio contract is changed.
