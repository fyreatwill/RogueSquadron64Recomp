# NEXT work unit — port-side VI consumer parity

HYPOTHESIS-ID: m5-port-vi-consumer-handoff-parity

## Single work unit

Instrument one build of the port's consumer-side VI handoff around
`ultramodern::ViManager::update_vi` and the following `update_screen` action.
Phase-gate all rows on VI transitions and retain the existing whole-RDRAM
positive control. Compare whether the port consumes the same framebuffer and
mode context that retail publishes at the 640-to-1024 transition. Do not
change behavior.

## Competing hypotheses

- H-PortConsumerParity: the port consumes the queued context and publishes
  the same framebuffer/mode transition; the missing behavior is downstream.
- H-PortConsumerStale: the port consumer runs but sees a stale or mismatched
  framebuffer/mode context at the target transition.
- H-PortConsumerAbsent: the port never reaches the consumer handoff in the
  target phase, so the route stop is upstream.

## Discriminating measurement

In one run, a positive-control row plus target-phase paired snapshots of
`next_state` before `update_vi`, `update_screen_regs` after the screen action,
and VI width/origin split the hypotheses. Matching retail-equivalent context
selects H-PortConsumerParity; a live consumer with stale/mismatched fields
selects H-PortConsumerStale; no target-phase consumer row with passed controls
selects H-PortConsumerAbsent.

## Exact commands

1. Add the phase-scoped diagnostic to the existing VI event consumer path,
   using the canonical env-var catalog and no behavior change.
2. Build with `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run from `build/` with the existing validated spin-yield/F5-LLE route,
   capturing the whole-RDRAM positive control and VI phase lines to a new
   `scratch/agent/s3123_*` directory; kill with SIGKILL if the watchdog fires.
4. Record the paired consumer snapshots and select exactly one hypothesis.
