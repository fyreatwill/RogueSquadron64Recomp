# Next work unit: M5 family route/object identity join

HYPOTHESIS-ID: m5-family-route-object-join

The paired target-phase capture selected source-payload parity: retail and
port both reach title/hangar, and both have the zero hangar source span. The
remaining boundary is whether the port S/L/I family stores are writing an
alternate object because the clear-associated route identity is wrong.

Competing hypotheses and discriminator:

- H1: the family stores join the clear-associated object/route; the apparent
  alternate-object writes are an observation/aliasing error.
- H2: S/L or I writes a legitimate alternate object and no family store reaches
  the clear-associated `0x801797B0` source object.
- H3: the family control, clear witness, or target phase is absent, making the
  join coverage-invalid.

The discriminator is one bounded image-only run containing the existing
family-edge, S/L/I entry, clear-witness, target phase, and source-DMA controls;
report the joined object address, store destination, and clear-object identity
in the same phase-gated rows. H1 requires a family store to join
`0x801797B0`; H2 requires positive family stores with no such join; H3 is any
missing positive control or target phase.

Before running:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Then use the existing validated image route and its family controls in one
SIGKILL-bounded capture from `build/`; do not add a mitigation or guard.
