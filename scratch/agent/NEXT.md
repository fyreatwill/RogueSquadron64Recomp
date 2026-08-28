# NEXT work unit (s2905) — new M5 route-transition producer census

HYPOTHESIS-ID: m5-route-transition-producer-census

Add one bounded, source-backed port diagnostic at the VI commit/route handoff
that records the producer callsite, committed width/origin, phase ordinal,
route-prepare sequence, and whether the next audio dispatch observes the same
key. Run it with the retail oracle whole-RDRAM positive control and both image
and silent arms in one build/run. This is a route-qualification probe, not an
audio behavior change; do not repeat the closed scheduler-ID table or add a
downstream audio field.

## Competing hypotheses and discriminator

- H-TransitionKeyMatches: the port's VI transition producer and subsequent
  audio route prepare share the expected phase key, identifying a valid route
  handoff boundary.
- H-TransitionKeyDiverges: the port commits a phase but the route/audio
  consumer sees a different key or stale origin, identifying the handoff as
  the route failure boundary.
- H-NoTransitionProducer: the port never emits a target transition producer;
  the route failure is upstream of this handoff and needs a different census.
- H-InstrumentAbsent: the oracle whole-RDRAM control or same-run positive
  transition control fails, making the rows unevaluable.

The discriminator is one phase-keyed handoff table for both arms containing
the VI producer tuple, route-prepare tuple, first following audio-dispatch
tuple, key equality, and crash/abort markers. The oracle must first show
10,000 whole-RDRAM writes and title/hangar transitions; a target transition
control is mandatory before interpreting a port null.

## Exact commands

Build and run the new bounded probe script from `build/Debug`; launch the
oracle and both port arms concurrently, and use SIGKILL cleanup. Do not run
the old Step 6 recipe again until this handoff qualifies the route.
