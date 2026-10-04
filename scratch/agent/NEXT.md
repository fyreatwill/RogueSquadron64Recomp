# Next work unit: qualify the active-queue sentinel guard in the patch pipeline

HYPOTHESIS-ID: m3-active-queue-sentinel-ownership

Competing hypotheses:

- H1: the new sentinel-disjointness guard is accepted by the patch toolchain and the ordinary Debug target, so this M3 ownership class has a regeneration-safe code change ready for runtime qualification.
- H2: the guard source is valid but the configured patch pipeline is unavailable; the ordinary target can still establish host-tree compatibility, while runtime qualification remains blocked by the missing target.
- H3: the new walk rejects a legitimate queue shape or fails compilation, disproving the assumed sentinel ownership invariant and requiring rollback before further M3 work.

Discriminator: build the ordinary Debug target after the guard change. H1 is a successful build with the patch source included; H2 is a successful ordinary build plus an explicit `PatchesLib`-target absence; H3 is a compiler/link failure attributable to the guard. Do not run a route soak: this unit tests one bounded ownership guard and its build integration, not runtime behavior.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
cmake --build build --config Debug --target PatchesLib
```

Record whether the active-queue sentinel walk compiles, whether the ordinary target links, and whether `PatchesLib` is present. The guard must remain out of the generated-function tree and retain its `ORIGIN:` statement.
