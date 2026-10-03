# Next work unit: validate the M3 heap metadata-slot guard

HYPOTHESIS-ID: m3-heap-metadata-slot-validation

Build and smoke-test the existing `patches/heap_guards.c` metadata-slot guard.
First verify the required tools and targets, then use the configured patch
pipeline if available:

    sed -n '1,260p' patches/README.md
    command -v mips64-elf-gcc mips64-elf-ld
    test -x build/Debug/N64Recomp.exe
    cmake --build build --config Debug --target PatchesLib

If that succeeds, run the allocator-route smoke described in
`patches/README.md`; capture both the guarded fixed-slot path and a deliberately
mispointed metadata-slot path in one run.

Competing hypotheses and discriminator:

- H1: the guard's fixed linker-published metadata-slot checks are reached and
  preserve valid allocator queue-link stores.
- H2: the configured build cannot compile/link the patch, so no validation is
  possible in this environment.
- H3: the smoke reaches a mismatched metadata slot, proving the invalid arm is
  rejected while the valid arm remains live.

The discriminator is tool availability followed by one build and one paired
allocator smoke. H1 requires successful patch build plus valid-route activity;
H2 is selected only by this iteration's direct tool/target checks; H3 requires
both valid and mismatched-slot outcomes in the same smoke.
