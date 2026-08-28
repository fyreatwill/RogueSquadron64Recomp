# NEXT work unit (s2908) — generated-symbol sweep at 0x8004661C

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Inspect the next bounded placeholder interval after the already reconciled
`0x80040304` record: `0x8004661C..0x80046620`. Reconcile only
source-backed semantic names or mechanically proven non-callable `data_gap_*`
records in the companion/project maps, generated snapshot, and
regeneration-safe rename table. Leave callable-ambiguous and data-ambiguous
records unchanged. Do not repeat the M5 route probe: s2905 positively matched
the pre-title key but did not qualify target phases.

## Competing hypotheses and discriminator

- H-CallableSemantic: companion m2c/source evidence supports a human symbol
  name for `0x8004661C`.
- H-DataGap: exact boundaries, a short fragment/trap body, and no
  callers/lookups prove a non-callable record, so `data_gap_8004661C` is the
  defensible reconciliation.
- H-Ambiguous: evidence cannot separate a callable trampoline from a split/data
  artifact; leave the placeholder unchanged.

The discriminator is the complete interval table: generated body size and
instructions, target location if any, companion symbol boundaries, source/m2c
name, generated callers and lookups, and the selected action for the sole
record.

## Exact commands

Run `python3 tools/rename_generated_symbols.py --help`, inspect the bounded
interval, and use the project reconciliation workflow. Build the Debug target
if generated files change.
Record the complete table at
`scratch/agent/s2907_generated_symbol_rename/source-table.md`. Verify exact
old-name searches and build the Debug target if generated files change.
