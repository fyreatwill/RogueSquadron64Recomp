# Session 5279 M4 accumulator boundary revisit

The retail oracle was run once with the cxd4 RSP mid-task VACC dump and the
existing per-task dump in the same run. The run also armed a whole-RDRAM write
watch as the independent positive control and requested the task-publication
watch from `0x80033FCC`.

Command: `scratch/agent/s5279_m4_acc_boundary.sh`, 75 emulated seconds, Rice/
rdplog, the qualified nine-Start schedule. The run reached 320, 640, 1024,
and 512-wide phases, including both hangar origins `0x006ab400` and
`0x006ab800`.

Controls and capture:

- Whole-RDRAM watch: 10,000 writes, so the oracle watch fired.
- RSP completion dump: 2,085 graphics records aligned 1:1 with 2,085 RDP
  rows; the dump was 27,151,148 bytes.
- Mid-task dump: 3,036,036 records in 2,085 graphics tasks; the dump was
  206,450,448 bytes. The record parser used the on-disk signed-16-bit VACC
  representation and compared each halfword as `value & 0xffff`.
- The requested `0x80033fcc` task-publication watch produced zero rows. That
  arm did not pass its own positive control and is unevaluable here.

Results:

- Task-end VACC had zero `0x8000` lanes in all 2,085 graphics tasks, including
  all 572 512-wide tasks and the 286 tasks at the two hangar origins.
- Mid-task VACC had `0x8000` lanes in all 572 512-wide tasks, including all
  286 hangar-origin tasks. It contained 100,993 such lane samples across the
  512-wide tasks.
- The same pattern is present in the retained s5129 raw dump. The earlier
  claim that mid-task VACC had zero `0x8000` lanes was a signed-16-bit decoder
  error: `0x8000` is represented as `-32768` in the dump. That conclusion is
  superseded; no runtime mitigation follows from this result.

Discriminator: the retail RSP does carry `0x8000` in mid-task accumulator
state during hangar graphics and does not retain it at task end. This supports
the mid-task-state branch of the M4 revisit, but it does not compare the port
or identify the writer/publication ordering. The evidence is single-source
retail evidence, with independent positive-control streams in the same run.
