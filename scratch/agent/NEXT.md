# Next work unit: qualify the active-queue tail-alias guard

HYPOTHESIS-ID: m3-active-queue-tail-alias

The bounded M3 audit adds one guard in `patches/heap_guards.c`: reject an
active-queue tail anchor when `tail == q`, where `q` is the node reached by
`tail->next`. This is a code change, not a diagnostic-only run. Build:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    cmake --build build --config Debug --target PatchesLib

The ordinary target must compile. `PatchesLib` either compiles the accumulated
MIPS patch pipeline or fails with the missing-toolchain/configuration evidence;
that result does not count as runtime qualification.

Competing hypotheses:

- H1: the tail alias is an invalid active-queue state and the new guard is
  sufficient for this idiom class.
- H2: the alias is legitimate in the game allocator, so the guard would reject
  valid work.
- H3: the source compiles but the MIPS/PatchesLib qualification path is absent.

Discriminator: Debug compilation selects source/build validity; `PatchesLib`
success selects toolchain availability, while a missing target selects H3.
Runtime legitimacy remains unproven until the accumulated MIPS patch is
built and exercised with allocator-chain controls.
