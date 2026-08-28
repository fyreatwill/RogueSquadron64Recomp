# NEXT work unit (s2969)

HYPOTHESIS-ID: m4-accumulator-boundary

## Unit

Revisit the M4 accumulator boundary with one complete phase/task-keyed join
table using the existing `B74`/`C70` instrumentation and positive-control
mark. Do not change guest or audio behavior. Use the last qualified AUTOPILOT
route; if the route again stops before a target phase, report the join as
unevaluable and do not infer M4 from pre-title zeros.

## Competing hypotheses and discriminator

- H-M4-B74-Producer: the consumer's accumulator value is written by the
  producer slot, so the same task/phase row should join `B74` value to that
  slot and the consumer index.
- H-M4-B74-OtherWriter: a different guest writer supplies `B74`; the join
  should show a stable writer/value independent of the presumed producer.
- H-M4-StaleOrUnreached: the apparent `B74` value is stale or the route never
  reaches the consumer; the positive control fires but no target-phase join
  closes.

The discriminator is one row per target phase/task containing `B74` writer PC,
value, producer slot, consumer index, consumer read PC, and VI origin/width.
The positive control must visibly fire in the same run; only a closed join at
the qualified hangar phase selects a producer explanation. A pre-title null
is unevaluable.

## Commands

1. Confirm the existing B74/C70 probe and positive-control mark in source.
2. Build one binary:
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run the existing qualified AUTOPILOT from `build/` with
   `ROGUESQ_LOG_ALL=1`, `PROBE_PHASE_WIDTH=512`, and
   `PROBE_KEYS_FROM_PHASE=1`; capture to a non-dot final path and SIGKILL the
   process group at the bounded timeout.
4. Summarize the whole-RDRAM positive control, route phases, and complete B74
   join table.

Expected outcomes: a producer-slot/B74/consumer join selects H-M4-B74-Producer;
a different named writer selects H-M4-B74-OtherWriter; positive-control-only
or pre-title rows select H-M4-StaleOrUnreached and require a new route angle.
