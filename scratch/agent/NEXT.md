# Next work unit: M5 alternate family-object semantic ownership

HYPOTHESIS-ID: m5-alternate-family-object-route-join

Session 3825 selected H2 at the qualified scope: the active route/source-DMA
handoff was present, but every sampled S/L/I family entry and store remained
outside the clear-associated `0x801797B0..0x80179A47` object. The remaining
question is whether those alternate objects are intended route state or a
disconnected output family.

Competing hypotheses and discriminator:

- H1: alternate objects are route-owned state and match a route-state table or
  handoff identity.
- H2: alternate objects are a disconnected output family; no route-state or
  source-DMA identity joins them.
- H3: the current route/object instrumentation lacks the ownership field, so
  the result is unevaluable.

The discriminator is one bounded image run using the validated autopilot and
phase transitions, extending the existing family/store and route controls with
the already available route-state/route-order rows. Correlate each distinct
alternate family object with the active route ordinal/row and source-DMA
descriptor in the same target-phase rows. H1 requires a stable identity join;
H2 requires positive controls plus no identity join; H3 is any missing target
phase, route/source control, or ownership field.

Before running:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Run from the repository root with the validated image environment from
`scratch/agent/s3825_m5_family_route_object_join_fixed/`; use SIGKILL and keep
all existing positive controls. Do not repeat the completed aliasing census or
add a mitigation.
