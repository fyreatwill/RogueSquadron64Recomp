# NEXT work unit (s2436) — watch the actual retail memset callsite

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Use one bounded retail-oracle run with the same positive control, title/hangar
phase gates, and exact image-store watches. Replace the uninformative return
site `0x8008F2D4` with the actual `jal 0x8008F2CC` callsite identified in the
MIPS body; add a phase-gated `--pc-field-dump` for that callsite and retain
the exact writer store table. Keep all watches observation-only and do not
modify the port.

## Competing hypotheses and discriminator

- H-RetailSemanticCaller: the callsite has a phase-specific field context
  matching the exact store range and distinguishes title/hangar semantics.
- H-RetailStoreHelper: the callsite context is stable copy-loop setup with no
  phase-specific semantic distinction, corroborating the helper interpretation.
- H-RetailContextInvalid: the positive control or title/hangar controls fail,
  so caller rows are uninterpretable.

The discriminator is the same-run table joining phase-gated callsite rows
(`pc=0x8008F2CC`, `$s0/$s1`, pointed source fields, `$a0/$a1/$a2`) to exact
writer rows by phase and return address. A stable phase-specific callsite
context selects H-RetailSemanticCaller; repeated context with the same
`ra=0x8008F2D4` selects H-RetailStoreHelper; failed controls select
H-RetailContextInvalid. Zero callsite rows with valid controls is an
instrument failure, not a semantic null.

## Exact validation

Require the whole-RDRAM positive control to reach 10,000 callbacks, title
`0x00790400:1024`, hangar `0x006AB400:512`, and exact-range totals before
interpreting any row. Use `--watch-pc 0x8008F2CC,0x800078EC`,
`--pc-field-dump 0x8008F2CC`, and
`--store-field-dump 2:0x800078EC` with the existing eleven-Start schedule.
