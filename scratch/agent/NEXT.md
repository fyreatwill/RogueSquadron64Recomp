# Next: reconcile the route-dependent hangar task tuple

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3663 ruled out a caller-family split: the retail oracle saw
`prev_pc=0x80090DE0`/`$ra=0x80090ABC` for the dominant writer across target and
non-target buckets. Controls passed with 133,677 whole-RDRAM writes and 1,107
valid type-2 task rows, but task tuples were title `data_ptr=0x80173B20` and
hangar `data_ptr=0x80173CB0`. This differs from s3662's validated hangar
`0x80171E70`; the paired s3663 port arm crashed before phase controls.

Next unit: one bounded route-reconciliation capture using the exact s3662
validated route and the s3663 all-phase oracle fields in one run. Join every
phase task row to writer `$s1`, `prev_pc`, `$ra`, and the four range watches;
retain whole-RDRAM and port title/hangar controls. Do not add a mitigation or
infer ownership from caller identity alone.

Competing hypotheses and discriminator:

- H-RouteTaskSelection: the s3662 and s3663 schedules select different live
  task objects, explaining `0x80171E70` versus `0x80173CB0`.
- H-SharedLogicalProducerAllPhases: both routes join each selected task's
  `data_ptr+0x10` to the same caller family and range ownership.
- H-SeparateLogicalProducer: the tuple difference persists within one route,
  or its caller/field family changes after exact joining.
- H-CaptureInvalid: selected only if whole-RDRAM, task, phase, or port controls
  fail; discard the census rather than infer ownership.

Planned command: add the route-reconciliation join to the existing oracle
field/task instrument, build `tools/oracle/rs64_oracle`, then run one paired
SIGKILL-watchdog capture from `build/` with the validated real-audio/LLE route.
Matching route-specific tuples select H-RouteTaskSelection; one stable tuple
and shared join select H-SharedLogicalProducerAllPhases; a persistent split
selects H-SeparateLogicalProducer; failed controls select H-CaptureInvalid.
Do not add a writeback, zero-fill, guard, or game-state forcing.
