# Next work unit (s4378): bounded post-publication writer attribution

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4377 qualified the live chain `0x80019D28/38/68 -> 0x80019DD8/E8/EC
-> 0x80033FCC`, with phase-specific source/object rows and task data pointers
`0x80173B20` versus `0x80171CE0`. Do not repeat the caller census, direct
publication join, or closed first-eight payload comparison.

Competing hypotheses:

- H-upstream-selector: the phase-specific source/object is the selector input
  for the published family.
- H-payload-overwrite: direct publication is correct, but a later writer
  changes the payload before consumption.
- H-post-publish-watch-gap: payload writes exist, but the selected
  post-publication PC set misses their writer.

Discriminating measurement: one batched oracle run must use the phase-specific
payload ranges `0x178C80:0x179A48` and `0x1E2FC0:0x1E3300`, add writer-PC
histograms for both ranges, and retain the already-qualified task join and all
three phase buckets. A phase-matched writer after `0x80033FCC` selects
H-payload-overwrite; no writer in the audited post-publication PCs with live
payload writes selects H-post-publish-watch-gap; a matching source/object and
payload writer sequence selects H-upstream-selector plus its writer. A null
without the whole-RDRAM positive control, all three VI buckets, and at least
1,000 valid type-2 rows is invalid.

Use the existing generated-function audit as the PC source, then run exactly
one batched capture from the repo root. Candidate post-publication writers are
the phase-specific ranges' existing callsites from the prior writer census;
start with `0x80090DE4`, `0x80090B68`, `0x80091078`, `0x80091198`,
`0x80090948`, `0x80090958`, `0x80092164`, and `0x8009216C`. Include the whole
RDRAM control, `0x80033FCC` typed task dump/join, `--pc-hist-watch` for both
payload watches, all three `--pc-phase-log-width` buckets, Rice, and the
established Start schedule. Use a 75-second run and do not build the port.
