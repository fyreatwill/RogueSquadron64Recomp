# M5 Session 3707 — shared clear input/state boundary

The paired qualification reached VI 512 in both arms. Each fired the new
writer-setup positive control and 128 setup rows. At the target setup both
arms had `a0=0x801797B0`, `a2=0x298`, `s0=0x12`, `s1=0x561F`, `t0=1`, and
`t1=0`; the pre-clear object words were identical and nonzero
(`0x7613940E`, `0xBD178316`). Existing static-clear rows independently
reported zero fill. The real arm continued with zero source-DMA payloads;
the silent arm emitted no image source DMA.

This selects `H-ProducerInputZero` and refutes `H-ProducerStateClobbered` at
the measured boundary. `H-ProducerUsesOtherState` remains unsupported by the
paired setup/object join. Evidence comes from real-vs-silent setup parity and
the independent static-clear plus real source-DMA observations.

ORIGIN: diagnostic-only clear-input provenance. The writer is the legitimate
`0x800078EC` zero-fill; no mitigation or guest/RDRAM state change was added.
