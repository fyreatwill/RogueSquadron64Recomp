# NEXT work unit — generated-symbol renaming sweep, next bounded placeholder batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

M5 remains blocked pending a route change. The selected M3 class
`musyxMixActiveVoices` was proven range-safe in Session 3167. Session 3185's
mandatory external-boundary revisit found a retail producer-wait route but no
port target phase; do not repeat that oracle recipe until a route change.
Session 3187 synchronized the stale `funcs.h` and `recomp_overlays.inl`
references for the already-classified `data_gap_800027B8`. Resume the
regeneration-safe sweep at the next unclassified generated record.

Competing hypotheses and the discriminating measurement:

- `H-SemanticMatch`: a placeholder has an exact companion-qualified semantic
  function name and can be propagated without ambiguity.
- `H-DataGap`: a placeholder is independently classified as a non-callable
  fragment and can be renamed mechanically to `data_gap_<address>`.
- `H-Ambiguous`: the companion record is fake/duplicate/overlay-colliding or
  lacks enough evidence; it must remain unchanged.

The discriminator is one bounded sweep table: every candidate in the selected
interval is classified against companion symbols and generated definitions,
then the helper must report at least one changed reference. An exact match
selects SemanticMatch or DataGap; ambiguous entries remain untouched.

Selected batch: `static_3_8009D8BC` is an invalid two-instruction generated
split (`lwc1` plus invalid `scd`) with no callable prologue or companion
semantic symbol. It is a mechanical data-gap rename, not a runtime change.

Exact commands:

```sh
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --start-address 0x8009D8BC --end-address 0x8009D8C0 --limit 16 --require-rename
rg -n 'static_3_8009D8BC|data_gap_8009D8BC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
```

Expected outcome: the helper changes the generated body and declaration, with
zero stale `static_3_8009D8BC` references remaining. If it reports no rename,
the selected record is not present in the generated snapshot and the next
unclassified static record must be selected.
