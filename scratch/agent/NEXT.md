# NEXT work unit (s2461) — qualify the explicit zero-update resolver edge

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Run one qualified port capture with the existing first-null resolver,
`slotDispatcherIter` pre-call, and indirect positive-control diagnostics. Test
whether the `slot->update_func==0` edge identified in s2460 occurs immediately
before `get_function(0)`, or whether the update pointer is nonzero and the
failure is instead in the match-keyword dereference path. Do not add guards or
change dispatch/audio behavior.

## Competing hypotheses and discriminator

- H-ZeroUpdateTerminal: `slotDispatcherIter` observes `update_func==0`, then
  `get_function(0)` terminates the run before target capture.
- H-NonzeroSlotThenMatch: the slot callback pointer is nonzero; the route fails
  later in `matchKeywordWithPriority` or its input producer.
- H-ResolverControlFailure: the indirect positive control does not resolve in
  the same run, making the null result non-discriminating.

The discriminator is one phase-scoped row joining the slot pre-call's
`update_func`, the resolver's requested address, and the indirect positive
control. `update_func=0` immediately followed by `get_function(0)` selects
H-ZeroUpdateTerminal. A nonzero update pointer followed by match-path failure
selects H-NonzeroSlotThenMatch. Missing positive-control resolution requires a
corrected capture.

## Exact commands

1. Build the current tree using the normal qualified configuration.
2. Run one instance from `build/` with `ROGUESQ_LLE_FORCE=1`,
   `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
   `ROGUESQ_LOG_ALL=1`, `ROGUESQ_LOG_SLOT_DISPATCH=1`,
   `ROGUESQ_SLOT_DISPATCH_PHASE_MIN=4`, `ROGUESQ_LOG_M5_SECOND_EXEC=1`, and
   `ROGUESQ_LOG_A1_ABORT=1`; capture output to a non-dot final path and kill
   with SIGKILL after the existing hangar/abort boundary.
3. Record joined rows and positive-control counts in one artifact. Do not
   interpret a null without the indirect resolver control firing.
