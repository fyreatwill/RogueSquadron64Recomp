# NEXT work unit (s2917) — generated-symbol sweep at 0x80059B4C

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Inspect the next bounded placeholder interval `0x80059B4C..0x80059B50`.
Reconcile only source-backed semantic names or mechanically proven
non-callable `data_gap_*` records in the companion/project maps, generated
snapshot, and regeneration-safe rename table. Leave callable-ambiguous and
data-ambiguous records unchanged.

## Competing hypotheses and discriminator

- H-CallableSemantic: companion m2c/source evidence supports a human symbol name.
- H-DataGap: exact boundaries, a short fragment/trap body, and no callers/lookups prove a non-callable record.
- H-Ambiguous: evidence cannot separate a callable trampoline from a split/data artifact; leave it unchanged.

The discriminator is the complete interval table: generated body size and
instructions, target location if any, companion symbol boundaries, source/m2c
name, generated callers and lookups, and the selected action.

## Exact commands

Run `python3 tools/rename_generated_symbols.py --help`, inspect the bounded
interval and companion sources, then use the reconciliation workflow. Build
the Debug target if generated files change. Record the complete table at
`scratch/agent/s2917_generated_symbol_rename/source-table.md`. Verify exact
old-name searches and preserve the rename-table entry for regeneration.
