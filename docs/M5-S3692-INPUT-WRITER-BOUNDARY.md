# M5 s3692 — input writer boundary

The independent retail capture was valid: the whole-RDRAM positive control
fired 11,058 writes, the watched source span fired 1,058 writes, and the
hangar origin `0x006AB400` produced 370 VI samples. Its hangar source-span
writer histogram included `0x800078EC` (768 rows), `0x80007670` (172 rows),
and several `0x8001F...` PCs.

The qualified port capture used the validated real-audio/LLE recipe. It
produced 3,178 hangar input-DMA rows and 512 hangar source-reader rows. The
new scalar-store witness passed its all-store control and captured 384 title
rows, all from `0x800078EC`, all zero. Every hangar input-DMA row carried the
same preceding-writer snapshot: sequence 384, PC `0x800078EC`, physical
address `0x17992C`, length 1, value zero. No hangar-phase scalar writer row
was observed. The descriptor/source ranges themselves were the expected
`0x1797B0..0x179930` span.

This refutes `H-InputDescriptorWrong` for the measured rows and refutes
`H-PreDmaHostClear` as an immediate pre-DMA action. It does not select
`H-InputWriterZero` for hangar: the port's only observed writer is a stale
title zero-fill, while retail writes the span again during hangar. The live
question is now a port-versus-retail hangar writer gap, including non-scalar
`rs_memset` or DMA paths not covered by the scalar witness.

ORIGIN: diagnostic scalar-store witness; it records guest store provenance
and carries the latest row into input-DMA logging without changing state.

Evidence: `scratch/agent/s3692_m5_input_payload_writer/real_validated_recipe.log`,
`scratch/agent/s3692_m5_input_payload_writer/silent.log`, and
`/tmp/rs64_oracle_s3692_groundtruth.log`.
