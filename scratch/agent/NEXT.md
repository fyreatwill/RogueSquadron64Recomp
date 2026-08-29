# NEXT work unit — parity-check the post-consumer handoff on the port

HYPOTHESIS-ID: m5-audio-route-upstream-boundary

## Single work unit

Use one phase-gated port probe for the exact guest-PC range
`0x800356AC:0x80035B00`. Session 3125's independent retail run passed its
whole-RDRAM control, reached title 1024 and hangar 512, and executed this
range 5,631,581 times across the run. The paired port qualification still
stops at VI 640, so audio behavior remains out of scope. Do not change
behavior.

## Competing hypotheses

- H-PortConsumerAbsent: the port never executes the retail-live continuation
  before its VI-640 stop; the divergence is at or before this range.
- H-PortConsumerLive: the port executes the range at target width, so the
  route marker or phase gate is incomplete rather than the range being absent.
- H-PortControlInvalid: the port's controls fail or the probe is not actually
  armed, so a null is unevaluable and must not be promoted.

## Discriminating measurement

In one bounded port run, the range must be phase-gated by VI transitions and
run beside the existing all-width VI-context and host voice positive controls:
target-phase range rows select H-PortConsumerLive; no such rows with both
controls positive selects H-PortConsumerAbsent; a missing control or marker
selects H-PortControlInvalid and requires a fixed run, not a conclusion.

## Exact commands

1. Add one phase-gated port watch for `0x800356AC:0x80035B00`, using the
   existing VI-context and host voice controls; keep the log budget per phase.
2. Build once, run from `build/`, and kill with SIGKILL. Require both controls.
3. Record range rows at VI 640, title 1024, and hangar 512; select one
   hypothesis, or mark the probe unevaluable.
