# Next work unit: qualify the expansion-chain ownership guard when the patch toolchain is available

HYPOTHESIS-ID: m3-expansion-chain-links-4026

Competing hypotheses:

- H1: `func_8002221C` returns a well-formed expansion chain; the new
  reciprocal-link guard is behavior-preserving and the ordinary host build
  remains clean.
- H2: the source-level guard is malformed or introduces an ABI/build defect;
  the host build or patch compilation fails before runtime.
- H3: the chain can be malformed at runtime, but this checkout cannot qualify
  that because the configured MIPS toolchain/PatchesLib target is unavailable.

Discriminator: build the changed patch and ordinary Debug target in one
bounded check. H1 requires `git diff --check` and a successful
`RogueSquadron64Recomp` Debug build. H2 is a reproducible compiler/linker
failure attributable to this guard. H3 is the specific configured-toolchain
failure after the source/host checks pass; it is not evidence that the alias
occurs.

Commands:

```sh
git diff --check
cmake --build build --config Debug --target RogueSquadron64Recomp
cmake --build build --config Debug --target PatchesLib
```

If `PatchesLib` remains unavailable, record the exact CMake target failure and
leave runtime qualification blocked. Do not run the parked M5 census or add
another diagnostic field in this unit.
