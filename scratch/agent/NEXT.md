# NEXT work unit — audit the remaining unresolved generated fragment

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit `fake_func_800AE3E4` across the companion map, generated body, callers,
header/registration, project TOML, and local duplicates. Synchronize a name
only if the evidence proves a callable fragment with an exact companion
identity; use `data_gap_800AE3E4` only if the boundaries prove
non-callability; otherwise preserve the placeholder. Do not repeat the
completed `0x800B2628`, `0x800B42BC`, or `0x800B89F4` records.

## Competing hypotheses

- H-Callable: complete prologue/return plus exact companion identity support a
  semantic rename.
- H-DataGap: isolated fragment or trap-filled invalid-data record between
  complete routines supports a mechanical `data_gap_*` name.
- H-Ambiguous: overlap, callers, or duplicate overlay identity prevents a
  safe rename, so the placeholder remains.
- H-StaleSurface: generated code is already correct and only a project
  symbol/fixup surface is stale.

## Discriminating measurement

The six-surface audit must report callable boundaries, exact companion
identity, callers, and uniqueness. A complete callable body plus exact name
selects H-Callable; an isolated/trap-filled record with no callers selects
H-DataGap; overlap or duplicate identity selects H-Ambiguous; a project-only
mismatch selects H-StaleSurface. The selected outcome determines whether a
regeneration-safe rename is made.

## Constraint

Naming-only. No runtime instrument or build is required.
