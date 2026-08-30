# NEXT work unit — validate the completed free-list guard on the configured host

HYPOTHESIS-ID: m3-free-list-queue-guard-validation

Run the configured `PatchesLib` build on the Windows/MIPS host, then run one
validated port smoke if the generated patch library is produced. The current
checkout cannot perform this validation because it lacks the MIPS toolchain,
the target, and generated patch output; do not claim runtime guard evidence
from this Unix checkout.

## Competing hypotheses

- `H-GuardValidPath`: the new alignment and cycle guards compile and preserve
  valid allocator/queue behavior.
- `H-GuardCatchesCorruption`: a controlled invalid or cyclic chain takes the
  guard return without queue mutation.
- `H-GuardBuildUnavailable`: the configured host prerequisites remain absent,
  so runtime behavior is unevaluable.

## Discriminator

The discriminator is a successful `PatchesLib` build followed by valid-path
execution plus a controlled invalid/cyclic free-list fixture on that host.
Successful compilation and unchanged valid-path smoke select
`H-GuardValidPath`; the fixture returning before queue writes selects
`H-GuardCatchesCorruption`; missing prerequisites select
`H-GuardBuildUnavailable` only for this environment.

## Exact command

```sh
cmake --build build --config Debug --target PatchesLib
cmake --build build --config Debug --target RogueSquadron64Recomp
```

If the build is unavailable again, obtain the configured Windows/MIPS build
artifact before attempting another validation iteration. Do not modify audio
or repeat the scheduler oracle while this guard validation is pending.
