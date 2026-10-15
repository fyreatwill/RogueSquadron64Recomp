# Next work unit: qualify the normal patch artifact after reference-symbol fix
HYPOTHESIS-ID: m3-assembly-patch-pipeline

Competing hypotheses:

1. The ELF-reader fix is sufficient for the normal patch-generation path; the
   generated host artifact is accepted by the configured patch target.
2. The assembly-only path is fixed but the normal CMake patch path has a
   separate toolchain/configuration blocker.
3. The generated artifact still exposes a symbol or relocation mismatch that
   the assembly-only result did not cover.

Discriminating measurement: run `cmake --build build --target PatchesLib`
with the normal patch inputs, then inspect `RecompiledPatches/patches.c` and
the target result. Successful generation/compilation selects H1; a missing
MIPS C toolchain or CMake skip selects H2; a generated relocation/symbol
failure selects H3. Keep the runtime override disabled.

Exact commands:

    cmake --build build --target PatchesLib -j2
    rg -n 'allocateDisplayListBuffer|findAndUnlinkSmallestEntry' RecompiledPatches/patches.c
