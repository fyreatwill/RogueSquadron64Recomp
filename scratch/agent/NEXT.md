# NEXT work unit — trace the guest writer of the divergent audio task fields

HYPOTHESIS-ID: m5-task-field-writer

Session 3481 selected the first task-field divergence at enqueue PC
`0x80033FCC`: retail uses `data_ptr=0x80171CE0`, `data_size=2`, while the
port uses `data_ptr=0x8018FB70`, `data_size=3`; task pointer/type and zero
output/yield fields agree. The host send route is not the first observed
divergence.

Competing hypotheses and discriminating outcomes:

- `H-TaskWriterRoute`: the port and retail execute different guest writer
  routes before enqueue; writer-PC histograms differ.
- `H-TaskPayloadMutation`: both execute the same writer route, but the value
  or size is changed after that writer and before enqueue; ordered writer
  values match first, then diverge at enqueue.
- `H-TaskObservationInvalid`: the task enqueue PC or phase join is not live;
  missing whole-RDRAM/phase controls invalidate the comparison.

Discriminating measurement: arm the independent Rice oracle with whole-RDRAM
control plus physical writes to the task struct span `0x149470:0x1494B0`,
writer-PC histogram/detail, and execution at `0x80033FCC`, all phase-gated to
`0x00790400:1024`; add a regeneration-safe port witness for writes to the
same task fields and retain the host-task control. A first writer-PC route
divergence selects `H-TaskWriterRoute`; matching writer route with differing
post-store field values selects `H-TaskPayloadMutation`; missing controls
selects `H-TaskObservationInvalid`.

Build once after all hooks are present. Run both arms concurrently from
`build/` with SIGKILL watchdog cleanup. Use the existing Rice oracle route and
the validated `s3479_m5_downstream_requal/run_late.sh` route, and keep the
title phase/ordinal join. Do not infer from sequential task rows without both
controls.
