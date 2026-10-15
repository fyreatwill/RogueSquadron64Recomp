# Next work unit: resume normal patch-artifact qualification after MIPS GCC is available
HYPOTHESIS-ID: m3-assembly-patch-pipeline

Competing hypotheses:

1. A supplied MIPS GCC toolchain will enable the normal patch-generation path;
   the generated host artifact will then compile.
2. The normal path will remain configuration-blocked despite a toolchain
   override.
3. The generated artifact will expose a relocation or symbol mismatch not
   covered by the assembly-only result.

Discriminating measurement: with a real `mips64-elf-gcc` available, reconfigure
and run the normal `PatchesLib` target. Successful generation/compilation
selects H1; CMake still omitting the target selects H2; a generated
relocation/symbol failure selects H3. Keep the runtime override disabled.

Exact commands:

    cmake -S . -B build -DMIPS_GCC=<toolchain>/bin/mips64-elf-gcc -DMIPS_LD=<toolchain>/bin/mips64-elf-ld
    cmake --build build --target PatchesLib -j2
    rg -n 'allocateDisplayListBuffer|findAndUnlinkSmallestEntry' RecompiledPatches/patches.c

Current blocker: this host has `/opt/homebrew/bin/mips-linux-gnu-as` and `ld`,
but no `mips64-elf-gcc` or `mips-linux-gnu-gcc`; CMake consequently omits
`PatchesLib`. `MIPS_GCC` and `MIPS_LD` are now explicit cache overrides, so use
those exact paths when the compiler is supplied. Do not rerun the same command
until then.
