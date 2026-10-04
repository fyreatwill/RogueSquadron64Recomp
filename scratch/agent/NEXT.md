# Next work unit: validate the active-queue guard class

HYPOTHESIS-ID: m3-active-queue-guard-validation

The current source-level guard requires the node selected through
`heap_tail_loc` to be terminal before active-queue publication stores. This
maintenance iteration did not claim runtime behavior.

Competing hypotheses and discriminator:

- H1: the patch pipeline is present but CMake omitted `PatchesLib`. Fresh
  configure exposes the target and the target build reaches MIPS compilation.
- H2: the CMake target is correct but external MIPS/N64Recomp tools are absent.
  Configure still omits the target or the first build reports missing tools.
- H3: the pipeline builds but the guard source/link configuration is invalid.
  The target exists, tools run, and the build fails at source, linker, or
  N64Recomp generation.

Discriminator: the first failing stage in the prerequisite checks and one
configured target build distinguishes H1/H2/H3. If it builds, run the
allocator smoke and require either a named guard fire or a clean route with
the guard class exercised. A guard fire is not retail corruption proof.

Commands:

    command -v mips64-elf-gcc
    command -v mips64-elf-ld
    test -x build/Debug/N64Recomp.exe
    cmake -S . -B build
    cmake --build build --config Debug --target PatchesLib

Do not add another guard or run the stale M5 candidate-writer arm until this
validation checkpoint is resolved.
