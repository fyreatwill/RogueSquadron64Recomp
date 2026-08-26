# NEXT work unit (s2432) — field-context table for retail hangar image writers

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Run one independent retail-oracle capture with `--pc-field-dump` for every
selected hangar image writer/entry PC, phase-gated to `0x006AB400:512`. Keep
the port unchanged. Reuse the s2431 whole-RDRAM positive control, exact image
range watches, Start schedule, and target-phase controls.

## Competing hypotheses and discriminator

- H-RetailSemanticEntryContext: the range writer entry has a stable context
  tuple distinct from helper rows, identifying the semantic image-consumer
  boundary.
- H-RetailStoreHelperContext: entry and helper rows share the same phase-local
  context, so the selected PCs are one lower-level store pipeline.
- H-RetailContextInvalid: a whole-RDRAM or title/hangar control fails, making
  the field table uninterpretable.

The discriminator is one bounded phase-gated table over
`0x800078EC`, `0x80007670`, `0x8001E2C0`, `0x8001FACC`, `0x8001FADC`,
`0x8001FAE4`, `0x8001FAEC`, `0x8001FAF0`, `0x8001FAF8`, `0x8001FB10`,
`0x8001FB14`, `0x8001FBE4`, and `0x8001FD2C`, using each PC's `$s0`, `$s1`,
`MEM_W($s0+0x60)`, `MEM_BU($s0+0x22)`, `$v0`, and `MEM_HU($s1+0x22)`. Distinct
stable tuples between entry and helper rows select
`H-RetailSemanticEntryContext`; shared tuples select
`H-RetailStoreHelperContext`; failed controls select `H-RetailContextInvalid`.

## Exact command shape

Reuse the s2431 command, retaining both exact range watches, both
`--pc-hist-watch` options, `--pc-hist-phase 0x006AB400:512`, all thirteen
`--watch-pc` options, `--pc-phase-log-width 0x006AB400:512`, and VI tracing.
Add one `--pc-field-dump` argument containing the same thirteen PCs
(comma-separated), then retain the validated eight-Start schedule. Arm the
whole-RDRAM watch first and require its positive threshold before interpreting
any target null.
