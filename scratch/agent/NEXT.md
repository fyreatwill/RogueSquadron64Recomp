# Next work unit: M5 alternate family-object route join

HYPOTHESIS-ID: m5-alternate-family-object-route-join

Session 3824 selected legitimate alternate-object writes: the active,
phase-qualified S/L/I family stores never joined the clear-associated
`0x801797B0` object or span. The next boundary is whether those alternate
objects are the intended route state or a disconnected output family.

Competing hypotheses and discriminator:

- H1: alternate family objects are route-owned state and are joined to the
  active route/source-DMA handoff.
- H2: alternate family objects are real but disconnected from the active
  route/source object, explaining the zero source payload.
- H3: route identity or source-DMA controls are absent, making the join
  coverage-invalid.

The discriminator is one bounded image-only run containing the existing
family-edge, S/L/I entry, clear-witness, route snapshot/order, target phase,
and source-DMA controls. Join each family entry's object arguments and store
destinations to the active route row and the source-DMA descriptor in the same
phase-gated rows. H1 requires a stable route/source join; H2 requires
phase-qualified alternate objects with no such join; H3 is any missing
positive control or target phase.

Before running:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Then use the existing validated image route and its family controls in one
SIGKILL-bounded capture from `build/`; do not add a mitigation or guard.
