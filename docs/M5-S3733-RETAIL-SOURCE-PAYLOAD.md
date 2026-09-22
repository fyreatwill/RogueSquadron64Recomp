# M5 session 3733 — retail source payload requalification

The fixed independent retail-oracle capture ran 120.2 seconds / 7,184 VI.
The whole-RDRAM positive control reached 10,000 callbacks and was removed;
the run reached 1024-wide `0x00790400` and hangar 512-wide `0x006AB400`.

Target-phase samples in `0x1797B0..0x1798B0` were 189/256 nonzero, and the
adjacent `0x1798B0..0x179A48` range was 106/256 nonzero. The task-data watch
`0x173CB0..0x173DB0` produced a target-phase snapshot. The candidate output
watch `0x166450..0x169450` had no target samples, so this run does not support
an output-only classification.

The independent writer census included `0x80007670`, `0x8001E2C0`, and the
`0x8001F...` family; the hangar-phase source histogram attributed observed
source-range writes to the later `0x800078EC` clear. The type-2 task dump at
`0x80033FCC` returned zero rows, so descriptor parity is unevaluable rather
than null.

This selects `H-RetailSourceNonzero` and refutes `H-RetailSourceZero` at the
measured boundary. `H-RetailOutputOnly` is insufficient as the primary
explanation because the retail source itself is nonzero. The next boundary is
an explicit byte/layout join between retail source samples and the port's
corresponding zero source-DMA payload.

The first attempt was invalid because unrestricted high-rate writer output
grew to about 1 GB before shutdown summaries. The fixed rerun removed
per-instruction writer watches and kept bounded phase-gated histograms and
payload summaries.

ORIGIN: independent retail oracle watches and phase histograms. No port or
guest behavior changed.
