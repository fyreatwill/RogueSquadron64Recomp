# Next work unit: validate the active-queue head guard when the patch pipeline is available

HYPOTHESIS-ID: m3-active-queue-head-integrity

Session 3859 added a guard to the allocator queue-link class: a non-null
active-queue head must be a complete aligned KSEG0 block before queue stores.
The change is intentionally unvalidated until the patch pipeline exists.

Competing hypotheses and discriminator:

- H1: the active-queue head is legitimate and the new guard is transparent on
  the allocator-route smoke.
- H2: the head is malformed or outside the complete block span, and the guard
  prevents a queue-link dereference.
- H3: the patch pipeline remains unavailable, so no runtime conclusion is
  permitted.

The discriminator is one configured `PatchesLib` build followed by the
existing allocator-route smoke. H1 requires a successful patch build and
unchanged valid queue progress; H2 requires a guard return before the invalid
link store without an access violation; H3 is selected if the compiler,
linker, generated recompiler, or target is still absent. The writer origin is
the allocator's active-queue head slot at `0x801163FC`; a malformed pointer is
not legitimate.

Exact preparation and run shape:

    command -v mips64-elf-gcc mips64-elf-ld
    test -x build/Debug/N64Recomp.exe
    cmake --build build --config Debug --target PatchesLib
    # If the target builds, run the existing allocator-route smoke from build/
    # with its normal watchdog and SIGKILL teardown; do not add a new probe.
    git status --short
