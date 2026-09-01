# M5 Session 3536 — output-contract qualification

The rebuilt real-audio port and independent retail oracle were run in one
batch. The port reached title (`1024 @ 0x00790400`) and hangar
(`512 @ 0x006AB400`); the oracle ran for 120 seconds with a whole-RDRAM
positive control and target execution/write watches.

The oracle control fired 10,329 times and retail reached both target phases.
Retail executed `0x80033FCC` 10,144 times, `0x80090E04` 13,568 times, and
`0x80029D20` six times. Target writer watches reported 17 writes to
`0x800A0F50`, 108 writes in `0x80141AD0:0x80141AF0`, 25 writes to
`0x80154620`, and 87/6/86 writes to the three sampled status spans; the
`0x80155848` watch was zero. The oracle task dump at `0x80033FCC` was not
phase-qualified (`rows=0`), so it is not task-field parity evidence.

The port's same-build controls were live. It dispatched 86 real image tasks,
recorded 2,946 task-ABI rows, 9,624 DMA-range rows, 17,092 image-stage rows,
3,087 image completion calls, and 533 audio returns. Phase-keyed rows existed
in both title and hangar: image-stage 2,778/14,314; completion 459/2,628;
audio-return 258/275; audio/SP route 774/1,314 each; PCM source and consumer
102/102 total. Image tasks returned at `break_pc=0x1328` with `exit=1`, and
the SP completion/delivery/guest-receive chain was live.

Every sampled PCM source and consumer row was zero-valued with
`fnv=0xF59C39C5` and `nz=0` in both target phases. Image-stage payloads were
also zero-valued. The host `copyToRAM` boundary was active, but no sampled
writer produced a legitimate nonzero output payload. The port therefore
matches the task/DMEM/DMA/completion route at the observed scope while the
output payload remains unresolved.

This selects `H-ContractGap` over a missing task-dispatch or completion edge,
but does not select a writer or authorize a writeback change. `H-CaptureInvalid`
is rejected by the controls; `H-OutputParity` is rejected for payload
correctness because the port endpoints agree on zero, not because zero is
known correct. The next useful unit is a new phase-qualified source-payload
writer/consumer join with independent retail writer attribution.

Evidence: `scratch/agent/s3536_m5_output_contract/oracle.log` and
`scratch/agent/s3536_m5_output_contract/port/run.log`.

ORIGIN: diagnostic-only task, DMA, completion, route, host-boundary, and PCM
observations; no audio state, task field, selector value, writeback, or output
was rewritten, skipped, or validated.
