# NEXT work unit (s2868) — M5-post-dispatch-discriminator

HYPOTHESIS-ID: M5-post-dispatch-discriminator

## Work unit

Design and run one new M5 post-dispatch/scheduling discriminator that can
separate a real audio publication edge from route failure. Qualify the
title/hangar route first with the same-run oracle control; do not interpret
service, slot, MORT, or PCM nulls until the target phase is live.

## Competing hypotheses and discriminator

- H-post-dispatch-edge: a new phase-qualified discriminator shows a distinct
  retail post-dispatch producer/consumer ordering at title or hangar.
- H-route-failure: the whole-RDRAM control fires but the qualified target phase
  is absent, so audio nulls remain unevaluable.
- H-no-new-edge: the target phase is qualified but the new discriminator is
  unchanged across the relevant lifecycle, ruling out that angle.

The discriminator must be a complete same-run table of positive-control hits,
VI phases, and the selected post-dispatch ordering/producer observations.
Before building, identify the exact retail ground-truth observation and its
port counterpart; new ordering selects H-post-dispatch-edge, missing phase
selects H-route-failure, and qualified unchanged ordering selects
H-no-new-edge.

## Exact commands

No exact command is authorized yet: first ask the retail oracle for the
ground-truth address/ordering that the new discriminator will measure, then
batch all port counters and A/B arms in one build/run.
