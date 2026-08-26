# NEXT work unit (s2434) — capture exact-writer call/store context

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Extend the oracle-only exact-store table for watch 1 and watch 2 to include
the physical store address, pre-store word, `$ra`, `$a0`, `$a1`, `$a2`, `$t0`,
and `$t1`, keyed by exact writer PC and latched VI phase. Keep the generic
`--pc-field-dump` path unchanged. Build once, then run the validated 120-second
retail recipe from s2433 with the whole-RDRAM control first, exact ranges,
phase gates, the 13 selected PCs, and the eleven-Start schedule.

## Competing hypotheses and discriminator

- H-RetailSemanticEntry: the exact range writer carries a stable caller/return
  and store-value/address tuple identifying the semantic image entry.
- H-RetailStoreHelper: the exact writer has a repeated copy-loop/register
  tuple, with caller/return context separating it from the semantic entry.
- H-RetailContextInvalid: whole-RDRAM or title/hangar controls fail, so no
  tuple is interpretable.

The discriminator is the bounded exact-store table grouped by phase, watch,
writer PC, `$ra`, store address, and store value. A stable semantic tuple
selects the first hypothesis; repeated copy-loop tuples with distinct callers
select the second; failed controls select the third. Zero exact callbacks is
an instrument failure, not a semantic null.

## Exact validation

Require the positive control to reach 10,000 callbacks, title
`0x00790400:1024`, hangar `0x006AB400:512`, and exact-range totals before
interpreting any row. Do not modify the port or map either range.
