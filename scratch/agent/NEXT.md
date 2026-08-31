# NEXT work unit — join host audio-task ABI against retail

HYPOTHESIS-ID: m5-host-task-contract

Session 3480 qualified the selected late-store null: retail and port both show
no execution at the six late `rs_free` PCs, while the port host-task and
`osSendMesg` controls are live. The remaining boundary is the host task/send
contract.

Competing hypotheses and discriminating outcomes:

- `H-HostTaskContract`: the first divergence is in task fields or output
  metadata at the host audio-task enqueue boundary.
- `H-HostSendContract`: task fields match, but the `osSendMesg` queue/message/
  result route diverges before delivery.
- `H-ObservationInvalid`: either retail task dump, port host control, or the
  phase join is not live; no contract conclusion is allowed.

Discriminating measurement: run the retail oracle with its whole-RDRAM
control and `--pc-task-dump` at the title audio-task enqueue PC, phase-gated
to `0x790400:1024`; retain the port host-task, `osSendMesg`, and host-boundary
controls and join rows by title phase and task ordinal. Matching task
ABI/output fields with a send divergence selects `H-HostSendContract`; the
first task-field divergence selects `H-HostTaskContract`; missing controls
select `H-ObservationInvalid`.

Use the existing Rice oracle route and the validated port
`scratch/agent/s3479_m5_downstream_requal/run_late.sh` route. Build once after
all hooks are present, run from `build/`, and use SIGKILL watchdog cleanup.

Expected outcomes: matching task ABI with send divergence selects
`H-HostSendContract`; the first task-field divergence selects
`H-HostTaskContract`; missing title or controls select
`H-ObservationInvalid` and require route repair.
