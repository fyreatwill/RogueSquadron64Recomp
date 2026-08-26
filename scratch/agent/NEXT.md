# NEXT work unit (s2435) — separate exact writer from caller semantic entry

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Use the built oracle's new exact-store result to capture the caller boundary in
one bounded run: watch execution at the stable return site `0x8008F2D4` and
the exact writer `0x800078EC`, with the same title/hangar phase gates and exact
store table. Keep all watches observation-only and do not change the port.

## Competing hypotheses and discriminator

- H-RetailSemanticEntry: the caller execution has a stable phase-specific
  semantic context that matches the exact range's store tuple.
- H-RetailStoreHelper: the caller execution is a repeated lower-level copy
  context, with stable return/register state but no phase-specific semantic
  distinction.
- H-RetailContextInvalid: whole-RDRAM or title/hangar controls fail, so no
  caller tuple is interpretable.

The discriminator is the same-run join of exact-store rows to phase-gated
caller execution rows, grouped by phase, writer PC, caller PC, `$ra`, store
address, and pre-store word. A stable phase-specific caller context selects
the first hypothesis; repeated caller context across the range with no
semantic phase distinction selects the second; failed controls select the
third. Zero exact callbacks or zero caller rows is an instrument failure, not
a semantic null.

## Exact validation

Require the positive control to reach 10,000 callbacks, title
`0x00790400:1024`, hangar `0x006AB400:512`, and exact-range totals before
interpreting any row. Do not modify the port or map either range.
