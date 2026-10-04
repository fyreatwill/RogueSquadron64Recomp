# Next work unit: qualify the active-queue sentinel guard at source/build scope

HYPOTHESIS-ID: m3-active-queue-sentinel-predecessor

Run one ordinary Debug build after the new regeneration-safe guard in
`patches/heap_guards.c`; attempt `PatchesLib` once to record whether the host
can compile the patch pipeline. Do not run another route permutation or writer
census in this unit.

Competing hypotheses:

- H1: the active-queue sentinel is a dedicated anchor whose `prev` must remain
  null; the new guard is structurally valid and the ordinary host target still
  builds.
- H2: the sentinel may legitimately carry a predecessor during a non-empty
  queue; the guard would be over-restrictive and must be reverted or redesigned.
- H3: the source is valid but the configured host cannot build `PatchesLib`,
  leaving runtime qualification blocked on the MIPS toolchain.

Discriminator: the code-level ownership contract and build result. Select H1 if
the sentinel contract is consistent with the existing append code and the
ordinary Debug target builds; select H2 only if source inspection shows the
sentinel is intentionally linked from an active node; select H3 if `PatchesLib`
is absent despite the source change.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
cmake --build build --config Debug --target PatchesLib
```

Record ordinary-build success and the exact patch-target result. If the patch
target is unavailable, runtime qualification remains blocked; do not infer
guard behavior from the ordinary host build.
