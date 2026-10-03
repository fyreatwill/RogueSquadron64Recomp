# M5 Session 3802 — source writer census

The Debug build passed. A single phase-gated harness ran image and silent port
arms with the independent retail oracle. Both port arms reached title
`0x00790400`/1024 and hangar `0x006AB400`/512 with controls active and no
crash or abort. The oracle whole-RDRAM control fired and its `0x800078EC`
execution watch was active in title. The harness stopped when both port arms
reached hangar, before a retail hangar payload join, so retail span parity is
still unevaluable.

In the port image arm, the hangar input DMA repeatedly read
`0x1798B0..0x179A48` from DMEM `0xCB0` with `FNV=0x762B22A5` and zero
nonzero bytes. The source-range transition then wrote the same all-zero span
to RDRAM. DMEM coverage independently showed zero-valued vector writes and a
zero-valued DMA covering the input window; no phase-gated guest CPU store
overlapping `0x1797B0..0x179A48` was observed.

This selects the port-side RSP/vector/DMA chain as the immediate writer of the
zero source payload. It does not identify the upstream source of the zero data
loaded into DMEM or establish retail hangar payload parity.

ORIGIN: the immediate writer is the Factor 5 RSP route's zero-valued
DMEM/vector/DMA chain, followed by source DMA to RDRAM. The zero is legitimate
for the observed port route but is not yet explained as the intended payload;
no mitigation was added.
