# s2431 retail hangar execution-watch capture

The prescribed independent retail-oracle command ran for 120 seconds with the
whole-RDRAM positive control first, exact image-range watches, phase-gated
writer histograms, and execution watches for the complete s2430 candidate set.

- Whole-RDRAM: 12,253 writes; positive threshold reached.
- Title: 1024-wide VI at `0x00790400`.
- Hangar: 512-wide VI at `0x006AB400`; 1,252 rows in the phase histogram.
- Exact range writes: 1,536 at `0x167650..0x167C50`; 717 at
  `0x1798B0..0x179A48`.

Hangar-phase execution hits were 408 at `0x800078EC`, 184 at `0x80007670`,
12 at `0x8001E2C0`, 12 at `0x8001FACC`, 12 at `0x8001FADC`, 11 at
`0x8001FAE4`, 11 at `0x8001FAEC`, 12 at `0x8001FAF0`, 11 at `0x8001FAF8`,
11 at `0x8001FB10`, 11 at `0x8001FB14`, 11 at `0x8001FBE4`, and 11 at
`0x8001FD2C`.

The first exact range is exclusively attributed to `0x800078EC`. The second
is attributed to `0x80007670`, `0x800078EC`, and the listed helper set. Every
selected PC executes in the valid hangar phase, selecting
`H-RetailHangarExecutionClass` and ruling out `H-RetailHangarExecutionGap`
and invalid controls. This does not distinguish semantic entry from store
helpers or authorize a port mapping.
