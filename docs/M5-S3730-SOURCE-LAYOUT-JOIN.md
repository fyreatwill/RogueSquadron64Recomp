# M5 session 3730 — port source-layout join

The first concurrent port attempt was invalid: the real arm crashed during the
first Factor 5 boot task at guest PC `0x8000B650`, while the silent arm never
reached a target phase. A real-only retry used the same diagnostic build and
the validated autopilot route.

The retry reached hangar VI 512 at 24.5 seconds. Its positive phase/RSP
controls fired. It emitted 512 bounded source-range writeback rows and 2,456
image-DMA joins. The target source DMA consistently mapped `0x1798B0` to DMEM
`0xCB0`, length `0x198`; the sampled source-DMEM, output, and post-write
payloads were all zero (`nz=0`, with source-DMEM FNV `762B22A5` and output
FNV `762B22A5`). The transition rows independently reported zero payload and
zero post-write bytes. The observed source-range producer rows were the
earlier `0x800078EC` zero-valued fill; no target-phase nonzero producer row was
observed.

The independent retail capture from s3729 reached the same target phases,
passed its whole-RDRAM control, and sampled 90/664 nonzero bytes in the
corresponding source span. Retail writer PCs included `0x80007670`,
`0x8001E2C0`, and the `0x8001F...` family, in addition to the later clear.

This selects `H-PortSourceWriterDivergence` for the observed boundary and
leaves `H-PortSourceClearOrdering` open because the port capture did not show
nonzero producer content that was subsequently cleared. The repeated source
DMA descriptor and task handoff do not support `H-SourceLayoutMismatch` at the
measured boundary. This is two-source evidence: port transition/join rows and
the independent retail oracle; the producer census itself is port-local.

ORIGIN: diagnostic-only source producer, source transition, DMEM/output hash,
route-join, and existing phase controls. No guest, RSP, task, audio-route, or
payload behavior changed.
