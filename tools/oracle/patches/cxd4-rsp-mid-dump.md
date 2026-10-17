# cxd4 RSP mid-task VACC dump

Session 5129 added an env-gated `RS64_RSP_MID_DUMP` path to the maintained
external cxd4 source tree. `run_task()` calls `rs64_rsp_mid_sample(PC, step)`
every 256 instructions; the callback records only graphics tasks and writes
`RSM1`, sequence, task type, PC, instruction step, and the 24 signed 16-bit
VACC halfwords. `rs64_rsp_task_type` is set by `DoRspCycles` before entering
`run_task()`.

The existing `RS64_RSP_DUMP` completion record remains enabled in the same run
as the positive control. Record size for `RSM1` is 68 bytes. The one-run
recipe is `scratch/agent/s5129_m4_mid_acc.sh`.
