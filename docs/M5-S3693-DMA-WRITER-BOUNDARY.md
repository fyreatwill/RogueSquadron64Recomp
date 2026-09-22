# M5 s3693 — DMA writer boundary

The independent retail control passed before the port run: whole-RDRAM writes
were 33,934,346, the `0x1797B0..0x179930` source span had 1,058 writes, the
title control span had 108 writes, the type-2/control span had 17 writes, the
selector span had 16 writes, and the retail oracle reached hangar origin
`0x006AB400` with a phase-gated writer histogram.

The paired port attempt had a real-audio crash before qualification, while its
silent arm reached title and hangar. A standalone rerun of the same real-audio
recipe then reached both target phases. Its positive control fired; it
captured 384 title scalar rows, 3,178 hangar input-DMA rows, and 512
source-range DMA-to-RDRAM rows. No hangar scalar writer row occurred.

For the hangar source-range DMA rows, the writer was not a guest scalar store:
the DMA-to-RDRAM transition rows had `dram=0x1797B0..0x179930`, with
`payload_nz=0` and `post_nz=0`. The independent retail writer-PC histogram and
the port's DMA transition attribution are two separate evidence lines. This
selects `H-NonScalarWriterPath` from the s3692 table and refutes
`H-WriterOutsidePhaseGate` for the measured port rows: the path is visible in
the phase gate, but its payload is already zero.

The next boundary is upstream of the DMA-to-RDRAM copy: identify the DMEM
payload producer and join it to the zero source-range DMA payload. This is a
diagnostic result only; no guest or RDRAM state was changed.

Evidence: `scratch/agent/s3693_m5_writer_gap/oracle.log` and
`scratch/agent/s3693_m5_writer_gap/real_fixed_current.log`.
