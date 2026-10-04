# Next work unit: validate the free-list reciprocal-link guard class

HYPOTHESIS-ID: m3-free-list-reciprocal-link-guard

The mandatory no-churn pivot selects a bounded M3 guard-class change instead
of the diagnostic-only M5 writer arm. The patch now audits reciprocal `prev`
links for every traversed free-list edge and requires the published free-list
head to have the null sentinel predecessor. ORIGIN: `func_8002221C` and the
allocator link stores publish these fields; malformed reciprocal links are not
legitimate allocator state. The configured patch toolchain is still absent, so
runtime validation is blocked and no allocator behavior is claimed.

Competing hypotheses and discriminator:

- H1: all valid free-list chains satisfy reciprocal `next`/`prev` links and
  the guard is observationally inert in an allocator smoke.
- H2: a malformed chain or non-null head predecessor reaches the patched
  entry; the guard returns before unsafe queue-link stores.
- H3: the patch cannot be built or loaded because the MIPS compiler, linker,
  N64Recomp executable, or `PatchesLib` target remains unavailable; no runtime
  conclusion is allowed.

The discriminator is one patch build plus allocator-route smoke: build the
patch ELF, generate the host patch, and run valid-list and malformed-link
arms in one executable. H1 requires the valid arm to preserve allocation and
queue-link stores with zero guard returns; H2 requires the malformed arm to
return before those stores; H3 is selected if any prerequisite tool or target
is absent. The positive control is a valid allocator allocation with the
expected head sentinel and reciprocal chain links.

Preparation and run when the environment is restored:

    cmake --build build --config Debug --target PatchesLib
    cmake --build build --config Debug --target RogueSquadron64Recomp

Then run the allocator smoke with both valid and malformed-link fixtures and
record whether the guard fires before any queue-link store. Do not proceed to
the M5 candidate-writer arm until this M3 validation dependency is resolved.
