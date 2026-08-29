# NEXT work unit — generated-symbol-renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved generated placeholder `fake_func_8006B704` against
the companion map, generated body, callers, header, overlay registration, and
project TOML. Rename it only if all surfaces establish a semantic identity;
otherwise preserve the placeholder or use a mechanical gap name, then advance
the ranked sweep.

## Competing hypotheses

- H-ExactIdentity: all independent surfaces agree on one callable semantic name and exact extent.
- H-Fragment: the record is an inline fragment or preamble without a distinct callable identity; preserve the placeholder or use a mechanical gap name.
- H-Conflict: overlay/address or companion surfaces disagree; do not rename.
- H-Unresolved: the available surfaces cannot establish a defensible name.

## Discriminating measurement

The six-surface table selects H-ExactIdentity only when body boundaries,
callers, and independent mappings agree; an inline-only body selects
H-Fragment; disagreement selects H-Conflict; insufficient evidence selects
H-Unresolved. No runtime build is required for this static unit.

## Exact commands

1. Inspect the six surfaces with bounded `rg`/`sed` windows.
2. If H-ExactIdentity is selected, update the regeneration-safe rename map,
   companion symbol/TOML entry, and generated references as one batch.
3. Verify no stale placeholder references remain and record the audit in
   `scratch/agent/s<session>_generated_symbol_rename/AUDIT.md`.
