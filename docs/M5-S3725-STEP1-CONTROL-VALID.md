# M5 s3725 — control-valid Step 1 qualification

The same-build real-vs-silent comparison used the full validated route:
`ROGUESQ_M4_Y8000_WIDTH=512`, missing-function stubs, ungated LLE, LLE solo,
spin-yield, and phase-gated probing. Both arms reached VI 1024 and VI 512,
and both emitted the phase, RSP-source, task-handoff, and SP-completion
positive controls. The run was therefore valid for the target comparison.

In the real arm, target phase produced 256 task-handoff rows, 512 source-range
writer rows, 2554 image-queue rows, 256 consumer-entry rows, and 313
image-complete calls. The source-range rows joined the expected target DMA;
the sampled payload remained zero, which is a separate image-content issue.

In the silent arm, target task handoffs were tagged `musyx_stub`. Its repeated
`audtask-abi`/`audtask-dma-row` records reported unchanged DMEM, no field
writes, and `dma_count=0`; it produced no target `m5-image-queue` or
`m5-source-range-writer` rows. Both arms still produced host audio queue and
drain rows, so host queue activity alone does not establish image-task
completion.

This selects `H-ImageContractProgress` for the measured paired port boundary
and refutes `H-ImageRouteOnly` and `H-AudioControlInvalid` at this scope. The
comparison is port-side evidence; retail callback parity remains open.

Evidence: `scratch/agent/s3725_audio_real/run.log` and
`scratch/agent/s3725_audio_silent/run.log`, both captured by the same build
and phase-gated run.
