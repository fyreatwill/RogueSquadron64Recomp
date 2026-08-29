# NEXT work unit — validate the free-list guard ordering patch on a toolchain host

HYPOTHESIS-ID: m3-freelist-guard-order

Session 3242 landed a guard-class change in `patches/heap_guards.c`. Sessions
3243–3244 confirmed that this checkout cannot run the validation: the configured
build has no `PatchesLib` target and the MIPS/N64Recomp prerequisites are
absent. The next unit remains a bounded build/validation on a toolchain-capable
host; do not infer runtime behavior from the source-only check.

## Competing hypotheses

- `H-GuardBuilds`: the patch compiles through MIPS GCC, N64Recomp, and the
  generated host library, preserving the override symbol.
- `H-GuardRejectsInvalid`: a focused harness or runtime trace demonstrates
  that an out-of-window `popped` value returns before queue publication.
- `H-GuardRegression`: valid in-window allocator values fail compilation,
  linking, or the existing full route, requiring rollback of this patch.

## Discriminator

Build `PatchesLib`, inspect the generated patch symbol/map, and run the
existing bounded route with the normal dispatch controls. A successful
cross-build and preserved override selects `H-GuardBuilds`; a focused invalid
pointer check before queue publication selects `H-GuardRejectsInvalid`; any
valid-path build/link/route failure selects `H-GuardRegression`.

## Exact commands

1. On the Windows toolchain host, build:
   `cmake --build build --config Debug --target PatchesLib`.
2. Confirm `patches/patches.map` contains `func_80007D74` and the generated
   `RecompiledPatches/patches.c` contains the override.
3. Run the existing bounded route with the normal positive controls and
   inspect for valid allocator progress and absence of a pre-publication AV.

## Environment prerequisite

The local `build/CMakeCache.txt` expects `E:/mips-toolchain` and a Debug
`N64Recomp.exe`; `RecompiledPatches/patches.c` is not present. Do not substitute
host Clang or the stale July `patches.map` for this validation. Human action
required: provide or mount the Windows/toolchain-capable checkout, then rerun
this exact work unit; no port-side M5 change is authorized before it.
