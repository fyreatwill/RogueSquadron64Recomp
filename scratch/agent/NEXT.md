# NEXT work unit — validate the heap dequeue/link guard class

HYPOTHESIS-ID: m3-heap-dequeue-link-guards-validation

Session 3254 landed the complete `func_80007D74` free-list dequeue and
active-queue guard class. Do not repeat the retail writer watch or rerun the
unavailable local target. The next single work unit is host validation on the
configured Windows/MIPS environment.

## Competing hypotheses

- `H-GuardBuildValid`: the patch ELF and generated host artifact can be built
  on the configured host and the override is linkable.
- `H-GuardHostMissing`: the host still lacks the configured MIPS/generated
  prerequisites, so only the source audit is available.
- `H-GuardRuntimeSafe`: the built override preserves valid allocations and
  returns before writes for invalid metadata in a bounded route run.

## Discriminator

Run the exact configured `PatchesLib` build on the Windows/MIPS host, confirm
`RecompiledPatches/patches.c` contains the override, then build the Debug
executable and run the existing bounded validation recipe. A successful
artifact selects `H-GuardBuildValid`; absent prerequisites select
`H-GuardHostMissing`; a clean valid/invalid metadata exercise selects
`H-GuardRuntimeSafe`. Do not infer runtime safety from this source-only
iteration.

## Exact commands

1. On the configured Windows/MIPS host, run
   `cmake --build build --config Debug --target PatchesLib`.
2. Build `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run the existing bounded M5 Step 3/guard validation recipe with SIGKILL;
   require the normal allocation path and invalid-pointer fallback controls.
