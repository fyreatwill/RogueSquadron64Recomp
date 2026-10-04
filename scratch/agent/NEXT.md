# Next work unit: unblock and validate the active-queue guard class

HYPOTHESIS-ID: m3-active-queue-guard-validation

The current source-level guard requires the node selected through
`heap_tail_loc` to be terminal before active-queue publication stores. Session
3899 confirmed that this checkout cannot validate it: CMake skipped the patch
pipeline because the MIPS compiler and generated N64Recomp executable are
absent, and `PatchesLib` therefore does not exist.

Competing hypotheses and discriminator:

- H1: the patch pipeline is present but CMake omitted `PatchesLib`. A fresh
  configure exposes the target and the target build reaches MIPS compilation.
- H2: the configured checkout lacks the external MIPS/N64Recomp tools. CMake
  skips the target, as it did this iteration.
- H3: the pipeline builds but the guard source/link configuration is invalid.
  The target exists, tools run, and the build fails at source, linker, or
  N64Recomp generation.

Discriminator: configure with the required tools present and build
`PatchesLib`. If it builds, run the allocator smoke and require either a named
guard fire or a clean route with the guard class exercised. A guard fire is
not retail corruption proof.

Required human unblock and commands:

    provide a Windows checkout/environment with E:/mips-toolchain, or set
    MIPS_TOOLCHAIN_DIR to an installed mips64-elf toolchain and provide a
    built N64Recomp executable at N64RECOMP_EXE
    cmake -S . -B build -DMIPS_TOOLCHAIN_DIR=<toolchain> -DN64RECOMP_EXE=<exe>
    cmake --build build --config Debug --target PatchesLib

Do not add another guard or run the stale M5 candidate-writer arm until this
validation checkpoint is resolved.
