# NEXT work unit (s2887) — generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

M5 remains open but its current route/contract discriminator stalled for three
iterations. Do not repeat it without a genuinely new route repair. The next
eligible bounded engineering unit is the placeholder sweep.

## Work unit

Inspect the next contiguous placeholder interval above `0x800C0000` in the
generated-function snapshot and companion decomp symbol map. Rename only
source-backed callable names or mechanically proven non-callable data gaps;
leave ambiguous records unchanged. Record the bounded source table and update
all generated references through `tools/rename_generated_symbols.py`.

## Competing hypotheses and discriminator

- H-Callable: companion code and call/reference structure identify a semantic
  function name.
- H-DataGap: the record is a non-callable fragment and can be named as a
  `data_gap_*` without changing execution.
- H-Ambiguous: evidence is insufficient; the placeholder must remain.

The single discriminator is a complete interval table containing each
placeholder, companion boundaries, generated body shape, call/reference
evidence, and selected action. Every candidate in the interval must land in
exactly one of the three classes in one pass.

## Exact next commands

1. Inspect `tools/rename_generated_symbols.py`, the companion map, and the
   next interval above `0x800C0000`; do not read the full ledger.
2. Produce one source table for the whole interval before editing names.
3. Apply only the table-selected renames and reconcile generated references.
4. Run the project’s symbol/reference checks and record counts and unchanged
   ambiguous candidates.

## Expected outcomes

- Source-backed callable entries are renamed with semantic names.
- Proven data gaps are renamed mechanically.
- Ambiguous entries remain placeholders and are explicitly recorded.
