# M5 Session 3570 — zero source-DMA producer census

The first standalone image capture was invalid: it reached title VI 1024 but
did not reach hangar VI 512. A corrected retry with the validated autopilot
schedule reached title at `0x00790400`/1024 and hangar at
`0x006AB400`/512. It used real audio, LLE-solo, spin-yield, and
`ROGUESQ_STUB_MISSING_FUNCS=1` from `build/`, then was stopped with SIGKILL.

The same run passed phase, RSP-source, source-DMA, and source-range-writer
controls. In hangar, source DMAs repeatedly loaded `0x1797B0`/`0x1798B0`
with zero hashes and zero nonzero bytes. Every observed write into the source
span was the expected `dmem_to_rdram` operation with zero payload. A separate
phase-matched `field348-writer` witness at guest PC `0x800078EC` fired 322
times, but its stores were also zero; it did not publish content. No crash
marker appeared.

This selects `H-SourceDmaZeroInput` in the productive-producer discriminator:
neither CPU nor RSP/DMA activity supplied nonzero source bytes before the
source DMA. The result is port-only for the detailed writer attribution. The
retail oracle independently passed its whole-RDRAM positive control (10,000
callbacks) but did not reach the target phase in its 8-second preflight, so its
zero target-span watch is unevaluable for hangar behavior.

The next boundary is the writer/initializer that leaves the source span at
zero before the image task, especially the zero `field348` path at
`0x800078EC`; no output, PCM, task, or DMA behavior was changed.

ORIGIN: diagnostic-only source-DMA and writer census. Zero source bytes are
not legitimate image content for this contract, so no mitigation was added.
