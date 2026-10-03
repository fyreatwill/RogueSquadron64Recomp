# Next work unit: M5 route-witness qualification for alternate-object ownership

HYPOTHESIS-ID: m5-alternate-family-object-route-join

Session 3825 selected H2 at a qualified scope, but the s3826 reproduction was
coverage-invalid: target phases and family/source-transition controls fired,
while route-preparation/order and input-DMA witnesses were absent. First
restore that witness before interpreting alternate-object ownership.

Competing hypotheses and discriminator:

- H1: route preparation and input DMA fire, and alternate objects match a
  route-state/handoff identity.
- H2: route preparation and input DMA fire, but no route/source identity joins
  the alternate objects.
- H3: target phases or any route-preparation/order/input-DMA positive control
  remain absent, so ownership is unevaluable.

The discriminator is one bounded image run using the validated autopilot and
phase transitions, with explicit `ROGUESQ_LOG_M5_ROUTE_PREPARE`,
`ROGUESQ_LOG_M5_ROUTE_ORDER`, `ROGUESQ_LOG_M5_RSP_SOURCE`,
`ROGUESQ_LOG_M5_EXACT_ROUTE`, and `ROGUESQ_LOG_M5_SOURCE_TRANSITION` gates.
Require target phases plus route-preparation/order and input-DMA positives;
then correlate each alternate object with the active route ordinal/row and
source-DMA descriptor. H1 requires a stable identity join; H2 requires the
positive controls plus no identity join; H3 is any missing positive control.

Before running:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Run `cmake --build build --config Debug --target RogueSquadron64Recomp`, then
run `zsh scratch/agent/run_s3826_m5_family_object_join.sh` from the repository
root. Use SIGKILL and keep all existing positive controls. Do not add a
mitigation or repeat an ownership conclusion without the route witnesses.
