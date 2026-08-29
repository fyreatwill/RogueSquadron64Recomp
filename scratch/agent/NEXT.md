# NEXT work unit — bounded generated-symbol rename audit

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved project placeholder after `0x800B42BC`, currently
`fake_func_800B75C4`, using the
six-surface sweep: companion map, generated body, callers, header, overlay
registration, project TOML, and local duplicate references. Rename only if an
exact companion identity is supported; otherwise synchronize a mechanical
`data_gap_*` name or preserve the placeholder for callable-ambiguous
fragments. This is one bounded rename/classification change. The candidate
has an existing historical audit, so do not repeat it without a new
discriminator; use that evidence to decide whether a regeneration-safe
classification can now be landed.

## Competing hypotheses

- H-ExactIdentity: companion/source/callers support one semantic name.
- H-Fragment: the record is non-callable or a data gap; only a mechanical name
  is safe.
- H-Ambiguous: evidence is insufficient; preserve the placeholder.

For `0x800B75C4`, a named companion plus callable body/callers selects
H-ExactIdentity; an isolated fragment between named bodies with no callers
selects H-Fragment and `data_gap_800B75C4`; conflicting extent or callable
evidence selects H-Ambiguous and keeps `fake_func_800B75C4`.

## Discriminating measurement

The six-surface evidence table must show whether the record has a callable
identity, exact companion name, or only fragment/gap evidence. The positive
control is the adjacent named callable body after the candidate; it must
remain present in the generated body/header/registration after any rename.
Exact identity selects H-ExactIdentity; no prologue/return/caller selects
H-Fragment; mixed or conflicting evidence selects H-Ambiguous and leaves the
placeholder.

## Exact commands

1. Confirm the candidate with `rg -n 'fake_func_800B75C4' syms/rogue_squadron.syms.toml`.
2. Inspect the six surfaces and existing rename tooling; do not regenerate the
   full tree.
3. Apply one regeneration-safe mapping/generated-tree rename or mechanical gap
   classification, then run relevant syntax/uniqueness checks.
