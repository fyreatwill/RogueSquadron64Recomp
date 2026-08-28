# NEXT work unit (s2893) — generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Inspect the next bounded unresolved placeholder interval beginning at
`0x8000337C`, ending at the next established symbol boundary. Reconcile only
source-backed callable names or mechanically proven non-callable data gaps;
leave ambiguous records unchanged. Record a complete source table.

## Competing hypotheses and discriminator

- H-Callable: companion code and call/reference structure identify a unique semantic function name.
- H-DataGap: the exact generated body is a non-callable fragment, invalid decode, or trap/data gap and can be named mechanically.
- H-Ambiguous: evidence is insufficient or conflicting; retain the placeholder.

The single discriminator is a complete interval table joining every generated
placeholder to its companion boundary, body shape, and call/reference
evidence. A callable selection requires a unique semantic companion name plus
callable evidence; a data-gap selection requires exact bounded non-callable
evidence; all other rows remain unchanged.

## Exact commands

1. Inspect `0x8000337C` through the next established boundary in the generated
   snapshot and companion maps; write the complete source table before editing.
2. Add only table-selected mappings to `tools/rename_generated_symbols.py` and
   reconcile with `--start-address 0x8000337C --end-address <next-boundary>`.
3. Update `syms/rogue_squadron.syms.toml` and the companion symbol map, then
   run exact old-name/reference checks and record selected and unchanged counts.

## Expected outcomes

Every candidate is classified as H-Callable, H-DataGap, or H-Ambiguous. Any
semantic callable or proven data-gap rows are renamed; ambiguous rows remain
placeholders and are explicitly recorded. No runtime build or soak is needed
unless the source table identifies a callable rename that changes generated
dispatch references.
