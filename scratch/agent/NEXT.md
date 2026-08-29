# NEXT work unit — validate guard patch and unlock M5 Step 3

HYPOTHESIS-ID: m5-step3-guard-validation

Session 3246 selected `H-PortRowMissing`: the port-side target logger is
present, but the validated image/silent pair stops at VI 640/origin
`0x0066A500`, while retail reaches the target relation. The next unit is the
already-planned guard validation on a host with the configured MIPS toolchain;
it is the prerequisite for M5 Step 3 and must not be substituted by Clang.

## Competing hypotheses

- `H-GuardBuildable`: MIPS/generated-host validation runs and supplies the
  required Step 3 gate.
- `H-GuardHostMissing`: the exact target remains unavailable, leaving Step 3
  blocked without evidence about guard correctness.

## Discriminator

Run `cmake --build build --config Debug --target PatchesLib`, then the existing
M5 Step 3 validation recipe from `docs/M5-AUDIO-PLAN.md`. A successful
MIPS/generated-host build selects `H-GuardBuildable`; `No rule to make target
PatchesLib`, missing `E:/mips-toolchain`, or missing generated patches selects
`H-GuardHostMissing`. The latter is an environment result, not guard evidence.

## Exact commands

1. On the configured host, run `cmake --build build --config Debug --target PatchesLib`.
2. If it builds, run the bounded guard validation with its existing image and
   silent controls; capture build, dispatch, target VI, and downstream joins.
3. Do not modify audio/output behavior unless the complete Step 3 validation
   row proves one named legitimate writer/consumer contract.

## Open dependency

The current checkout has no MIPS GCC/LD, no generated
`RecompiledPatches/patches.c`, and no `PatchesLib` target. Do not substitute
Clang or the stale `patches.map`.
