# Next work unit: configure the MIPS patch pipeline on a toolchain host

HYPOTHESIS-ID: m3-active-queue-ownership-guard

Competing hypotheses:

- H1: configuring with a valid MIPS toolchain root exposes `PatchesLib`, and
  the sentinel-disjoint guard compiles, regenerates, and links.
- H2: the toolchain host still omits `PatchesLib`, so only ordinary host-build
  evidence is possible.
- H3: the guard exposes a compile/link or ABI error once the target exists.

Discriminator: configure/build `PatchesLib` after supplying
`-DMIPS_TOOLCHAIN_DIR=<toolchain-root>`, then build the ordinary Debug target.
H1 is selected by a successful generated patch library plus final link. H2 is
selected by a specific missing-tool/target diagnostic after configuration. H3
is selected by a compiler, linker, or generated-patch error attributable to
this change.

Exact commands:

```sh
cmake -S . -B build -DMIPS_TOOLCHAIN_DIR=<toolchain-root>
cmake --build build --config Debug --target PatchesLib
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Do not run a route or writer census until the patch target result is recorded.
