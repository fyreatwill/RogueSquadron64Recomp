# NEXT work unit — audit the remaining unresolved generated fragment

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit `fake_func_800AE3E4` across the companion map, generated body, callers,
header/registration, project TOML, and local duplicates. If it is a callable
fragment with an exact companion identity, synchronize that name through the
rename fixups and generated snapshot; if it is an ambiguous instruction
fragment, classify it as `data_gap_800AE3E4` only when its boundaries prove
non-callability; otherwise preserve the placeholder. Do not revisit the
completed `0x800B2628`, `0x800B42BC`, or `0x800B89F4` records.

## Competing hypotheses

- H-Callable: a complete prologue/return and exact companion identity support
  a semantic rename.
- H-DataGap: the bytes are an isolated fragment or invalid-data trap between
  complete routines, supporting a mechanical `data_gap_*` rename.
- H-Ambiguous: overlap, callers, or duplicate overlay matches prevent a safe
  rename, so the placeholder must remain.
- H-StaleSurface: the generated snapshot is already renamed but one checked-in
  symbol/fixup surface is stale and needs synchronization only.

## Discriminating measurement

The six-surface audit must show whether `0x800AE3E4` has a callable boundary,
an exact companion identity, and a unique generated definition. A complete
callable body plus exact companion name selects H-Callable; an isolated or
trap-filled record with no callers selects H-DataGap; overlap or duplicate
identity selects H-Ambiguous; a mismatch limited to project surfaces selects
H-StaleSurface. The required code result is a synchronized rename only for
the selected callable/data-gap case.

## Constraint

No runtime instrument or build is required for this naming-only unit.
