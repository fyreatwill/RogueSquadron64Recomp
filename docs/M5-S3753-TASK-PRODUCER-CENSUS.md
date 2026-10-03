# M5 s3753 — task-data producer census

The independent retail run was performed before changing the port instrument.
Its whole-RDRAM positive control fired 127,554 times. The physical task-data
span `0x171E70..0x171F70` fired 117,245 times, including target-phase writes
from the `0x80090A..0x800911` family. The source span
`0x1798B0..0x179A48` fired 309 times.

The port build added `tools/apply_s3753_m5_task_producer.py`. It attaches a
phase-gated census to the existing regeneration-safe all-scalar-store helper,
with `[m5-task-producer-control]` as the same-run any-store positive control.
The qualified real and silent arms were run together for 75 seconds with the
validated autopilot and SIGKILL cleanup.

Both arms fired the instrument control 39 times and reached title and hangar.
Each produced 4,096 bounded target-phase task-data rows; every row was a
zero-valued scalar store. The real arm's source-DMA control/read/writer rows
remained present (1,024/1,024/512) and its joined source payload remained
`FNV=0x762B22A5`, `nonzero=0`. The silent arm remained the expected no-source
control. The real task handoff used `data_ptr=0x80171CE0`, while the censused
task-data target was `0x80171E70`; no nonzero scalar producer joined it.

This selects `H-TaskDataProducerAbsent` for the complete generated scalar-store
class in the port. It does not explain arbitrary host writes, RSP DMA, or other
non-scalar producers. No mitigation was added; the writer is still the
legitimate zero-valued generated store family.

Evidence: `scratch/agent/s3753_oracle_task_producer/oracle.log`,
`scratch/agent/s3753_m5_task_producer/real-summary.txt`, and
`scratch/agent/s3753_m5_task_producer/silent-summary.txt`.
