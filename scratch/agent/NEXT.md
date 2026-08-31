# NEXT work unit — join task writer values to enqueue payloads

HYPOTHESIS-ID: m5-task-field-writer

Session 3482 matched the retail and port task-span writer-PC route at all ten
title-phase PCs but found differing resulting payloads at enqueue. The exact
writer operand versus intervening mutation is still open.

Competing hypotheses and discriminating outcomes:

- `H-WriterOperand`: the shared writer PCs store different values in the
  payload fields; ordered post-store values diverge at the writer.
- `H-TaskPayloadMutation`: shared writer values match, then a later guest
  store or host boundary changes the fields before enqueue.
- `H-TaskObservationInvalid`: the task enqueue PC or phase join is not live;
  missing whole-RDRAM/phase controls invalidate the comparison.

Discriminating measurement: extend the independent Rice oracle capture to emit
ordered post-store values for physical fields `0x1494A0` and `0x1494A4` at
writer PCs `0x8009177C` and `0x80091784`, retaining whole-RDRAM control,
task-PC control, and phase buckets. Join those rows to the existing port
`[m5-task-writer]` and `[m5-host-task-boundary]` rows by origin and per-PC
ordinal. Matching writer values followed by enqueue divergence selects
`H-TaskPayloadMutation`; first writer-value divergence selects
`H-WriterOperand`; missing controls select `H-ObservationInvalid`.

Build once after all hooks are present. Run both arms concurrently from
`build/` with SIGKILL watchdog cleanup. Use the existing Rice oracle route and
the validated `s3479_m5_downstream_requal/run_late.sh` route, and keep the
title phase/ordinal join. Do not infer from sequential task rows without both
controls.
