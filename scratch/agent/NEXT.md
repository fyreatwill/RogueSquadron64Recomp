# Next work unit: restore runtime qualification for the audited M3 patch

HYPOTHESIS-ID: m3-active-queue-ownership-guard

Competing hypotheses:

- H1: the checked-in `PatchesLib` target is available after the normal CMake
  configure/build path; the new sentinel-disjoint guard can be compiled and
  linked into the runtime.
- H2: the source guard is valid, but this checkout still lacks the toolchain
  or generated patch target, so only ordinary host-build evidence is possible.
- H3: the guard exposes a compile/link or ABI error, requiring correction
  before any runtime qualification is meaningful.

Discriminator: configure/build `PatchesLib` and then the ordinary Debug target.
H1 is selected by a successful generated patch library plus final link. H2 is
selected by a specific missing-tool/target diagnostic after the source-level
guard is accepted. H3 is selected by a compiler, linker, or generated-patch
error attributable to this change.

Exact commands:

```sh
cmake --build build --config Debug --target PatchesLib
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Do not run a route or writer census until the patch target result is recorded.
