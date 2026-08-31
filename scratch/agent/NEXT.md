# NEXT work unit — validate the patches library on the configured MIPS host

HYPOTHESIS-ID: m5-patches-host-validation

Session 3316 confirmed this Unix checkout cannot run the configured-host
discriminator: the cache points to `E:/mips-toolchain`, both MIPS executables
and `RecompiledPatches/patches.c` are absent, and CMake has no `PatchesLib`
target. Do not repeat those local checks; run the command below on the
configured Windows/MIPS host.

Session 3315 found exactly three fixed-address B1C accesses: the reset at
5EE8 and conditional nonzero stores at 61D0 and 9360. There is no alternate
writer or pre-reset order; the observed-phase classification is
H-PortB1CDead. Do not repeat the B1C census.

## Competing hypotheses

- `H-GuardBuildWorks`: the Windows/MIPS toolchain and generated patch inputs
  are available and `PatchesLib` builds.
- `H-GuardHostMissing`: the configured target or generated patch inputs remain
  unavailable, as on this Unix checkout.
- `H-GuardSourceFails`: the host exists but the patch source/link contract
  fails.

## Discriminator

On the configured Windows/MIPS host, run `cmake --build build --config Debug
--target PatchesLib`. A successful `PatchesLib.lib` selects
`H-GuardBuildWorks`; the documented missing-target/generated-input failure
selects `H-GuardHostMissing`; a compiler/linker diagnostic after the target
exists selects `H-GuardSourceFails`. Do not repeat the local missing-target
build.

## Exact commands

```
cmake --build build --config Debug --target PatchesLib
```

Record the build result in a new evidence file. A successful library selects
`H-GuardBuildWorks`; a compiler/linker failure after the target exists selects
`H-GuardSourceFails`; absent host inputs select `H-GuardHostMissing`. No M5
Step 3 or behavior change is authorized by this validation.
