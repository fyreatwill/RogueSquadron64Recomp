# Next: obtain the missing 512 route-task join

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3664's fixed bucket-local join passed whole-RDRAM and title controls
and emitted 120 rows. Retail title buffers select different task objects:
`0x00790400 -> 0x80171CE0` and `0x00790800 -> 0x80173B20`, under the stable
writer caller `prev_pc=0x80090DE0`, `$ra=0x80090ABC`. The capture remained in
title and did not reach hangar 512, so this is not yet an all-phase result.

Next unit: run one phase-valid 512 capture using the same `--pc-task-join`
oracle instrument, with the validated hangar-driving press schedule. Keep the
whole-RDRAM watch, both title origins, both hangar origins, the four descriptor
watches, and the type-2 task/writer controls. Use `--pc-phase-quiet`; the join
mode already suppresses per-task audio-object dumps. The discriminating
outcomes are:

- H-RouteTaskSelection: each 512 VI origin joins a distinct task tuple, with
  stable writer caller fields.
- H-SharedLogicalProducerAllPhases: both 512 origins join one logical task
  tuple/field family consistent with the title mapping.
- H-SeparateLogicalProducer: writer caller or joined `$s1` family changes after
  a phase-valid task join.
- H-CaptureInvalid: whole-RDRAM, title, or hangar controls fail; discard the
  census and do not infer ownership.

Build command: `bash tools/oracle/build.sh`.
Run from `build/` with the prior s3664 oracle command, retaining
`--watch-write 0x0:0x800000`, `--pc-task-dump 0x80033FCC`,
`--pc-field-dump 0x80090DE4`, `--pc-task-join`, `--pc-phase-quiet`, and the
four phase buckets. Capture to `scratch/agent/s3665_m5_hangar_task_join/` and
SIGKILL the process group after the watchdog deadline.
