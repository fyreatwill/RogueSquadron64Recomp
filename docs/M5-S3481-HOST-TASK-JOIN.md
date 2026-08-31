# M5 Session 3481 — host-task ABI join

The paired capture used the Rice retail oracle and the validated port route,
with the whole-RDRAM positive control in the retail arm and the host-boundary
control in the port arm. Both arms reached the title phase at origin
`0x00790400`, width 1024.

At the shared audio-task enqueue edge `0x80033FCC`, the retail oracle emitted
type-2 `OSTask` rows. The first title row had:

    task_ptr=0x80149470 data_ptr=0x80171CE0 data_size=0x00000002
    output_buff=0 output_buff_size=0 yield_data_ptr=0 yield_data_size=0

The first corresponding port host-task row had:

    task_ptr=0x80149470 data_ptr=0x8018FB70 data_size=0x00000003
    output=0 output_size=0 yield=0 yield_size=0

The retail positive control reached 10,000 whole-RDRAM callbacks before being
removed. The port emitted its host-boundary control, 482 host-task rows, and
512 `osSendMesg` return rows. Thus the observations are live; the task pointer
and task type agree, while the first task data pointer and size do not.

This selects `H-HostTaskContract` at the observed enqueue boundary. It rules
out an absent task hook or a send-only divergence as the first observed
difference, but does not identify the guest writer that populated the task
fields or establish whether the differing payload is legitimate for the same
title ordinal. No runtime behavior was changed.

Evidence artifacts:

- `scratch/agent/s3481_m5_host_task_join/retail.log`
- `scratch/agent/s3481_m5_host_task_join/port.log`
- `scratch/agent/run_s3481_m5_host_task_join.sh`
