# NEXT work unit (s2433) — repair retail field-context join

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Add one oracle-only observation path that dumps the selected PC register/field
tuple only from the exact memory-write callback for watch 1 or watch 2, keyed
by the current writer PC. Keep the existing generic `--pc-field-dump` path
unchanged. Build the oracle once, then run one 120-second retail capture with
the whole-RDRAM control first, exact image-range watches, phase-gated writer
histograms, the 13 selected PCs, and the validated eleven-Start schedule.

## Competing hypotheses and discriminator

- H-RetailSemanticEntryContext: the exact store callback at the entry PC has a
  stable tuple distinct from the helper-store tuples.
- H-RetailStoreHelperContext: exact store callbacks at entry and helpers share
  the same phase-local tuple family.
- H-RetailContextInvalid: whole-RDRAM or title/hangar controls fail, so the
  table cannot be interpreted.

The discriminator is the bounded table of exact-store rows for watch 1 and
watch 2, grouped by writer PC and tuple. Distinct stable entry/helper tuples
select the first hypothesis; shared tuples select the second; failed controls
select the third. A table with no exact-store rows is an instrument failure and
does not select a semantic hypothesis.

## Exact validation

Use the s2432 oracle command and add the new exact-store field option for all
13 PCs. Require `12,000+` whole-RDRAM hits, title origin
`0x00790400:1024`, hangar origin `0x006AB400:512`, and exact-range totals
before interpreting any tuple. Do not modify the port or map either range.
