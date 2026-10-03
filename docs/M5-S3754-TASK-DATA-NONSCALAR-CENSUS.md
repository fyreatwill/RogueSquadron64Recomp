# M5 s3754 — task-data host/RSP producer census

The independent retail oracle was rerun with a whole-RDRAM positive control,
the physical task-data watch, and the source-span watch. The control fired
61,104 times; the task-data span `0x171E70..0x171F70` fired 50,387 times and
the source span fired 717 times. Phase-scoped writer attribution included
`0x80090A..0x800911`, confirming the retail producer path is live.

The port build extended the existing central host-write census to include the
task-data span. The same hook already receives RSP DMEM-to-RDRAM transfers, so
the batch covered PI ROM, PI SRAM, zmemcpy, and RSP DMA with per-API positive
controls. Real and silent arms ran concurrently with the validated autopilot;
the real arm reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, while silent passed its controls but remained the
expected no-source control.

All four API controls fired in both arms. Neither arm produced a phase-gated
host/RSP row overlapping `0x171E70..0x171F70`; the real arm separately
produced 4,096 generated scalar-store rows in that span, all zero-valued.
The real source-DMA join remained zero-valued and silent emitted no source
rows. This selects `H-TaskDataNonScalarAbsent` for the censused central host
and RSP classes, refutes `H-TaskDataHostProducer` and
`H-TaskDataRspProducer` for those classes, and leaves arbitrary direct/native
or other non-central ownership open.

ORIGIN: diagnostic-only host/RSP overlap census and retail watches; no guest
value, branch, DMA, or rendering behavior changed.

Evidence: `scratch/agent/s3754_oracle_taskdata/oracle-attribution.log`,
`scratch/agent/s3754_m5_taskdata/real/run.log`, and
`scratch/agent/s3754_m5_taskdata/silent/run.log`.
