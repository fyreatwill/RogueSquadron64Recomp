# M5 s3698 — coverage-aware DMEM producer census

The fresh retail oracle run passed its whole-RDRAM positive control (10,000
callbacks removed) and reached the 1024-to-512 transition at origin
`0x006AB400`. Its normal shutdown summary was not emitted, so the prior
independent retail writer contract remains the attribution source: retail
writes the source span through `0x800078EC`, `0x80007670`, `0x8001E2C0`, and
the `0x8001F...` family.

The Debug port build completed once with the new per-byte DMEM coverage table.
The qualified real-audio/LLE-solo/spin-yield/autopilot run reached VI 1024 at
14.5 seconds and VI 512 at 23.7 seconds. The RSP-source positive control fired
once; the DMEM-store control fired in both target phases; and 512 hangar
source-range rows were observed. Every source payload and post-write span was
zero.

The coverage table emitted 9,683 bounded subrange records for all 512 rows.
Covered subranges were zero-valued vector stores. However, 255 rows had no
observed writer for exactly `0xCC0..0xCD0` (the other sampled bytes had a
covering zero vector store). This is a different result from the previous
latest-global-predecessor join: a per-byte table exposes a stable hole rather
than merely a writer outside the DMA window.

## Classification

This selects `H-DMEMProducerAbsent` for the observed host DMEM-writer census:
the source DMA reads zero bytes from a repeated 16-byte region for which no
instrumented DMEM writer exists. It refutes `H-ZeroDMEMProducer` as a complete
coverage explanation. `H-RetailSourceDifferent` remains open because the
independent retail contract has writer families not represented by the port's
current host-side store table. This is diagnostic provenance only; no guest or
RDRAM state was modified.

The next boundary is the `0xCC0..0xCD0` gap: determine whether it is an
uninstrumented DMEM write path, a legitimate preserved/initialized zero gap,
or a port-vs-retail layout mismatch. The next instrument must retain the same
RSP, DMEM, and source-DMA positive controls.
