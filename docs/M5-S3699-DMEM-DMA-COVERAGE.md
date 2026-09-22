# M5 s3699 — DMEM DMA coverage gap

## Independent retail ground truth

Before the port build, the retail oracle passed the whole-RDRAM positive
control at 10,000 callbacks, produced 1,058 writes to physical
`0x1797B0..0x179930`, and reached the 1024-to-512 transition. Its phase-gated
512-width histogram included 384 writes from `0x800078EC`; the earlier retail
contract remains the independent comparison because this run did not emit a
complete shutdown writer histogram.

## Port measurement

The Debug target was rebuilt once after adding a regeneration-preserved witness
for every RDRAM-to-DMEM DMA copy. The qualified real-audio, LLE-solo,
ungated, spin-yield, autopilot run reached title VI 1024 and hangar VI 512.
The generic RSP control fired, the DMEM controls fired in both target phases,
and 512 hangar source-range rows were emitted. The source-range rows split
255/512 to DMEM `0xCB0` (the `0xCB0..0xE48` output window) and 257/512 to
DMEM `0x6F0` (the separate input window).

The new census classified the previously absent `0xCC0..0xCD0` coverage as a
DMA writer for all 255 `0xCB0` hangar rows. Its recorded bytes were zero, and
the source-range payload was also zero. The complete run emitted 9,380 vector
and 256 DMA coverage records across both target phases; no guest or RDRAM
state was changed.

## Classification

This selects `H-UninstrumentedDMEMWriter`: the missing coverage was an
RDRAM-to-DMEM DMA path omitted from the scalar/vector witness, not proof that
the interval had no writer. It refutes `H-GenuineZeroGap` as an explanation of
the missing census. It does not yet distinguish `H-RetailLayoutMismatch`,
because the DMA source bytes are still zero and the retail named scalar
writers have not been joined to this port DMA's source descriptor.

ORIGIN: diagnostic DMA/DMEM provenance only; no mitigation or game-state
change.
