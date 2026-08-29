# NEXT work unit — bounded generated-symbol rename audit

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved project placeholder, currently
`fake_func_8006B704`, using the six-surface sweep: companion map, generated
body, callers, header, overlay registration, project TOML, and local duplicate
references. Rename only if an exact companion identity is supported;
otherwise synchronize a mechanical `data_gap_*` name or preserve the
placeholder for callable-ambiguous fragments. This is one bounded
rename/classification change.

## Competing hypotheses

- H-ExactIdentity: companion/source/callers support one semantic name.
- H-Fragment: the record is non-callable or a data gap; only a mechanical name
  is safe.
- H-Ambiguous: evidence is insufficient; preserve the placeholder.

## Discriminating measurement

The six-surface evidence table must show whether the record has a callable
identity, exact companion name, or only fragment/gap evidence. Exact identity
selects H-ExactIdentity; no prologue/return/caller selects H-Fragment; mixed
or conflicting evidence selects H-Ambiguous and leaves the placeholder.

## Exact commands

1. Identify the next placeholder with `rg -n '^\\s*\\{ name = "fake_func_' syms/rogue_squadron.syms.toml`.
2. Inspect the six surfaces and existing rename tooling; do not regenerate the
   full tree.
3. Apply one regeneration-safe mapping/generated-tree rename or mechanical gap
   classification, then run relevant syntax/uniqueness checks.
