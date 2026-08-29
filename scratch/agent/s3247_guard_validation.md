# Session 3247 — guard validation result

## Competing hypotheses

- `H-GuardBuildable`: the configured MIPS/generated-host patch pipeline can be built here and supplies the prerequisite for M5 Step 3.
- `H-GuardHostMissing`: this checkout cannot build the patch target, so the result says nothing about guard correctness.

## Discriminator and result

Ran from the repository root:

```text
cmake --build build --config Debug --target PatchesLib
make: *** No rule to make target `PatchesLib'.  Stop.
exit_code=2
```

The cache names `E:/mips-toolchain`, while this host has no configured
`PatchesLib` rule or generated `RecompiledPatches/patches.c`; the checkout only
contains the patch inputs and stale `patches/patches.map`. This selects
`H-GuardHostMissing`. No guard behavior, M5 behavior, or runtime explanation is
supported by this result, and the Step 3 validation recipe was not run because
its build prerequisite failed.

## Unblock condition

On the configured Windows host, the exact target must produce `PatchesLib` with
the configured MIPS GCC/LD and Debug N64Recomp, after which the existing M5
Step 3 validation can be run with both image and silent arms.
