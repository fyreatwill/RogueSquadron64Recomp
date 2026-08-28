# NEXT work unit (s2890) — generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

M5 remains open but its current route/contract discriminator is parked after
three route-invalid iterations. The next eligible bounded engineering unit
is the next placeholder interval after `0x800FA248`.

## Work unit

Inspect the complete next placeholder interval beginning after `0x800FA248`
in the generated snapshot and companion decomp symbol maps. Rename only
source-backed callable names or mechanically proven non-callable data gaps;
leave ambiguous records unchanged. Record a complete source table and update
all generated references through `tools/rename_generated_symbols.py`.

## Competing hypotheses and discriminator

- H-Callable: companion code and call/reference structure identify a unique semantic function name.
- H-DataGap: the exact generated body is a non-callable fragment, invalid decode, or trap/data gap and can be named mechanically.
- H-Ambiguous: evidence is insufficient or conflicting; retain the placeholder.

The single discriminator is a complete interval table joining every generated
placeholder to its companion boundary, body shape, and call/reference
evidence. A callable selection requires a unique semantic companion name plus
callable evidence; a data-gap selection requires exact bounded non-callable
evidence; all other rows remain unchanged.

## Exact next commands

1. Inspect the generated snapshot and companion maps for the next interval and
   produce the complete source table before editing names.
2. Add only table-selected mappings to `tools/rename_generated_symbols.py` and
   reconcile the generated snapshot with `--start-address 0x80100000
   --end-address <next-boundary> --require-rename`.
3. Update the companion/project symbol maps, run symbol/reference checks, and
   record selected and unchanged counts.

## Expected outcomes

Every candidate is classified as H-Callable, H-DataGap, or H-Ambiguous. Any
semantic callable or proven data-gap rows are renamed; ambiguous rows remain
placeholders and are explicitly recorded.
