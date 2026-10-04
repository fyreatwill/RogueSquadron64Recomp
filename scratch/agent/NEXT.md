# Next work unit: qualify the regeneration-safe M3 patch target

HYPOTHESIS-ID: m3-patcheslib-qualification-4029

Competing hypotheses:

- H1: the configured `PatchesLib` target exists and builds with the supplied
  MIPS toolchain, so the heap-guard patch can be runtime-qualified.
- H2: the target is absent from the current build graph, so the blocker is
  CMake/configuration rather than a compile or link defect.
- H3: the target exists, but the configured MIPS compiler/linker or patch
  inputs are unavailable, so qualification is toolchain-blocked.

Discriminator: first enumerate the configured target, then invoke the target
once. H1 is a successful `PatchesLib` build; H2 is `No rule to make target
PatchesLib` and no target in `cmake --build build --target help`; H3 is a
target-recognized build that fails while locating or invoking MIPS tools or
patch inputs. Do not infer runtime guard behavior from a source-only build.

Exact commands:

```sh
cmake --build build --target help | rg -n 'PatchesLib|RogueSquadron64Recomp'
cmake --build build --config Debug --target PatchesLib
```

If H1, run the smallest available patch/runtime qualification and record its
positive control. If H2 or H3, record the exact blocker and keep the M5
writer census parked; do not repeat the route capture without a new schedule
discriminator.
