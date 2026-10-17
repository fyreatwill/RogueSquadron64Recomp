# cxd4 RSP mid-task VACC dump

Session 5129 added an env-gated `RS64_RSP_MID_DUMP` path to the maintained
external cxd4 source tree. `run_task()` calls `rs64_rsp_mid_sample(PC, step)`
every 256 instructions; the callback records only graphics tasks and writes
`RSM1`, sequence, task type, PC, instruction step, and the 24 signed 16-bit
VACC halfwords. `rs64_rsp_task_type` is set by `DoRspCycles` before entering
`run_task()`.

The existing `RS64_RSP_DUMP` completion record remains enabled in the same run
as the positive control. The task-keyed variant emits a task serial in both
records: `RSM1` is 72 bytes (`magic, sample_seq, task_serial, task_type, PC,
step, VACC`) and `RSD1` is 4160 bytes (`magic, dump_seq, task_serial,
task_type, VACC, DMEM`). The serial is assigned at `DoRspCycles` entry and is
copied to every mid-task sample until the completion dump. The one-run
recipe is `scratch/agent/s5129_m4_mid_acc.sh`; the bounded join parser is
`tools/analyze_m4_task_join.py`.
