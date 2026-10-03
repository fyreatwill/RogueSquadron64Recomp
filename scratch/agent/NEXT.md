# Next work unit: M5 corrected route/source witness qualification

HYPOTHESIS-ID: m5-alternate-family-object-route-join

Session 3825 selected H2 at a qualified scope, but s3827 did not split H1/H2.
The run was target-valid and did record accepted `[route-prep]` plus handoff
rows; the old summary searched stale names. Exact-route DMA and source-range
reader/writer rows were absent. First collect the real input-DMA witness before
interpreting alternate-object ownership.

Competing hypotheses and discriminator:

- H1: route preparation and input DMA fire, and alternate objects match a
  route-state/handoff identity.
- H2: route preparation and input DMA fire, but no route/source identity joins
  the alternate objects.
- H3: target phases or the actual input-DMA positive control remain absent, so
  ownership is unevaluable.

The discriminator is one bounded image run using the validated autopilot and
phase transitions, with `ROGUESQ_LOG_M5_ROUTE_PREPARE`,
`ROGUESQ_LOG_M5_ROUTE_ORDER`, `ROGUESQ_LOG_M5_ROUTE_TRANSITION`,
`ROGUESQ_LOG_M5_RSP_SOURCE`, `ROGUESQ_LOG_M5_EXACT_ROUTE`, and
`ROGUESQ_LOG_M5_SOURCE_TRANSITION` enabled. Require target phases, accepted
route-preparation/order, and an exact-route or source-range input-DMA row;
then correlate each alternate object with the active route ordinal/row and
source-DMA descriptor. H1 requires a stable identity join; H2 requires all
positive controls plus no identity join; H3 is any missing input-DMA control.

Before running:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Run `cmake --build build --config Debug --target RogueSquadron64Recomp`, then
run the existing script after adding only the missing
`ROGUESQ_LOG_M5_ROUTE_TRANSITION=1` gate and correcting its summary patterns to
`m5-route-prepare`, `route-prep`, `m5-route-order`, `m5-exact-route`,
`m5-exact-route-dma`, `m5-source-range-reader`, and
`m5-source-range-writer`. Use SIGKILL and keep all existing positive controls.
Do not add a mitigation or repeat an ownership conclusion without the input-DMA
witness.
