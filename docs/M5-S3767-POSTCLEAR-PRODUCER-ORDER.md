# M5 s3767 — post-clear producer and retail timing

The rebuilt capture used the existing phase-gated source-span writer, clear
caller, input-DMA, and image-stage probes, plus an independent retail oracle.
The oracle positive control fired (11,830 whole-RDRAM writes), reached title
VI 1024 at `0x00790400` and hangar VI 512 at `0x006AB400`, and recorded 705
writes in `0x1797B0..0x1798B0` and 1,125 writes in
`0x1798B0..0x179A48`. The port image arm also reached both target VIs.

In the port image arm, the phase-5 clear was
`0x8008F2CC -> 0x801797B0`, fill zero, length `0x298`. The target source
span then had 244 phase-5 writer rows, all zero-valued byte stores from
`0x800078EC`; no nonzero writer appeared. The input-DMA probe produced no
row in this capture, so the downstream DMA join is unevaluable here. The
silent arm reached neither target VI and its target rows are discarded as
incomplete coverage.

Together with the prior exact retail byte snapshots (nonzero title payload
and zero hangar payload), this selects `H-M5-PostClearProducerAbsent` for the
measured port target-span producer class. It refutes a port-side
nonzero-then-clear sequence in this capture. It does not identify the retail
writer-to-port call edge and does not authorize changing the legitimate clear.

ORIGIN: the observed port writer is the legitimate zero-fill at
`0x800078EC`; no mitigation or guest state changed.
