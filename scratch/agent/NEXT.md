# Next work unit (s4402): compare qualified port and retail payload families

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4399/s4401 port route is qualified as `0x00790400 -> 0x006AB400`; do
not seek or recount the absent `0x00790800` bucket.

Competing hypotheses:

- H-cross-source-equivalence: qualified port title/hangar task families match
  corresponding qualified retail families after phase labeling.
- H-cross-source-divergence: the direct port transition has phase-specific
  families that do not match retail in the same phase.
- H-cross-source-instrument-gap: a positive control, actual phase, or paired
  task/image join is absent, so no cross-source conclusion is valid.

Discriminating measurement: use the existing qualified retail payload capture
and one phase-gated port capture to compare normalized task data pointers,
source hashes, image-DMA hashes, and phase-family hashes for `0x00790400` and
`0x006AB400`. Matching normalized families select equivalence; a stable
phase-specific mismatch selects divergence; missing control, phase, or joins
select instrument gap. Report the title selector witness separately because
s4401 did not fire it in title.

Exact commands: inspect the existing qualified retail payload summary and
port log, then create one bounded comparison script with `apply_patch` if a
normalization is needed. Do not rebuild unless the existing logs lack a
required field. Run one phase-gated capture only if needed, for 85 seconds,
SIGKILL the game, and report controls, paired-row counts, and normalized
family matches.
