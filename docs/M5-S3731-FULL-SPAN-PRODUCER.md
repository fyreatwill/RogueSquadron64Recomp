# M5 session 3731 — full-span port producer census

Extended the regeneration-safe port source census from
`0x1797B0..0x179930` to the full retail-measured span
`0x1797B0..0x179A48`, then ran the prescribed real-audio and silent arms in
one build and one capture.

The real arm reached both target phases, fired the RSP positive control, and
produced 512 source-reader rows, 512 source-range writeback rows, 3,392
source-transition rows, and 13,824 DMEM-coverage rows. The target source DMA
was consistently `0x1798B0 -> DMEM 0xCB0`, length `0x198`; source, DMEM,
writeback, and post-write payloads were all zero. The silent arm reached both
target phases and fired the RSP control but produced no image-source rows, as
expected for the intentional stub.

The extended span added 478 producer-store rows overall. There were 78
nonzero stores in the extension, from the pre-target route; the target phases
had 280 extension rows and all were zero. The target zero writer remained the
known `0x800078EC` clear path. No target-phase nonzero producer appeared in
the full span.

This selects `H-PortSourceClearOrdering`: nonzero pre-target source content
exists, then the legitimate target setup clear leaves the later source DMA
zero. It refutes `H-UninstrumentedPortProducer` for the measured full span and
narrows `H-PortSourceWriterDivergence` to the already-observed ordering
difference. The independent retail witness from s3729 still reports 90/664
nonzero target-phase source bytes and the corresponding writer families, so
the result has two evidence lines: the port's full-span producer/payload join
and the retail oracle. No behavior changed.

ORIGIN: diagnostic-only full-span producer/transition hooks, source-DMA and
image-DMA payload hashes, route joins, and existing phase controls.
