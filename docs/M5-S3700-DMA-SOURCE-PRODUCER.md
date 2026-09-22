# M5 Session 3700 — DMA source producer boundary

## Ground truth

The independent retail preflight passed its whole-RDRAM positive control at
10,000 callbacks, reached title VI `0x00790400`/1024 and hangar VI
`0x006AB400`/512, and observed target-span writers from `0x800078EC`,
`0x80007670`, `0x8001E2C0`, and the `0x8001F...` family.

## Port measurement

The qualified real-audio, LLE-ungated, LLE-solo, spin-yield, autopilot retry
reached both target VIs. The RSP source control fired, the DMEM controls fired
in both phases, and 512 hangar source-range rows were emitted. All 512 rows
joined the intended source DMA: RDRAM `0x1798B0`, length `0x198`, to DMEM
`0xCB0`, with `source_dma_overlap=1`. Every source-DMA snapshot was zero
(`source_dma_fnv=762B22A5`, `source_dma_nz=0`), and every output payload was
also zero (`payload_fnv=A7B537C5`, `payload_nz=0`).

The paired input-DMA rows covering the same source span retained the port's
latest writer as the title zero-fill at `0x800078EC` (384 stores, zero value),
with no hangar writer from the retail families. The final source-DMA retry had
no crash or abort marker.

## Classification

This selects `H-RetailSourceDifferent`: the port is using the expected
`0x1798B0..0x179A48` source descriptor, but its source bytes remain the stale
zero-filled image while retail has distinct hangar writers. It refutes
`H-InputDescriptorWrong` for the measured range and supersedes the broader
`H-UninstrumentedDMEMWriter` boundary as the active next question. The next
probe should identify the port-side writer/layout producer for the source
range, including the portion beyond `0x179930`.

ORIGIN: diagnostic source-DMA provenance only; no guest-state or rendering
mitigation was added.
