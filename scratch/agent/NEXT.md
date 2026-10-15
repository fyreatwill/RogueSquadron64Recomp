# Next work unit

HYPOTHESIS-ID: m5-next-contract-edge

Before any behavior change, select one named M5 contract edge from
`docs/M5-AUDIO-PLAN.md` and run one same-build phase-gated validation with the
production arm and its rollback arm. The edge must have a named writer or
consumer, a positive control that reaches title and hangar, and a measurement
whose outcomes distinguish a real contract gap from route-only progress.

Competing hypotheses and discriminator:

1. H-contract-gap: the selected edge is incomplete and the production arm will
   show the expected upstream control but fail its downstream join.
2. H-route-only: the downstream null is caused by route reachability; both arms
   will have the same edge and downstream results once title/hangar controls
   fire.
3. H-rollback-specific: only the rollback arm diverges, identifying the edge as
   behaviorally active rather than dormant.

The discriminating measurement is one phase-keyed table containing dispatch,
task/SP completion, the selected edge's writer/consumer join, slot/voice or
PCM downstream control, and title/hangar VI controls for both arms. Do not add
another diagnostic field unless it changes this decision table.

First inspect the M5 plan's current sequence and choose the next still-open
edge; then batch both arms in one build/run. No mitigation is authorized
without an ORIGIN naming the writer and establishing value legitimacy.
