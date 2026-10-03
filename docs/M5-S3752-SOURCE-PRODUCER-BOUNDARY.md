# M5 session 3752 — source producer boundary after exact-load closure

## Ground truth

The independent retail oracle passed the whole-RDRAM positive control at
10,000 callbacks and reached title VI `0x00790400`/1024 and hangar VI
`0x006AB400`/512. The source span `0x1797B0..0x179A48` had 1,830 writes;
the exact route-field watch `0x128C70..0x128CD4` had 11,109 writes. Retail
execution attribution included `0x80007670` (300 executions), `0x8001E2C0`
(19), and the `0x8001F...` family (18–19 per observed site).

## Port measurement

The first paired run was invalid: the real arm crashed at 1.1 seconds before
either target phase, while the silent arm reached hangar. The fixed real-alone
run used the same build, hooks, schedule, and 75-second watchdog. Its source
hook control fired; it reached title and hangar; and it emitted 1,024
phase-gated source-reader rows, 512 source-writer rows, and 4,096 source
transition rows. In the hangar phase, the qualified source read was always
`0x1798B0`, length `0x198`, to DMEM `0xCB0`, with
`source_fnv=762B22A5`, `source_nz=0`, and task data pointer `0x80171E70`.
The paired silent arm passed its source-hook control, reached hangar, and
emitted no source rows, as expected for the silent control.

The source reader confirms the expected descriptor and route join, but its
task-data object is already zero before the source DMA. This selects
`H-PortSourceProducerAbsent` for the measured producer/read class and refutes
`H-PortSourceJoinMismatch` at the source-DMA edge. The next boundary is the
producer of task data at `0x80171E70`, including the route/task identity that
retail's writer families use.

ORIGIN: diagnostic source-reader/writer/transition joins and independent retail
watches; no guest value, branch, DMA, or rendering behavior was changed.

Evidence: `scratch/agent/s3752_oracle_producer_boundary/oracle.log`,
`scratch/agent/s3752_m5_source_producer_boundary/real-alone/run.log`, and
`scratch/agent/s3752_m5_source_producer_boundary/silent-summary.txt`.
