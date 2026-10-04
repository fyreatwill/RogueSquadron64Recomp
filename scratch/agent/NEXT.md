# Next work unit: validate the free-list reciprocal-link guard

HYPOTHESIS-ID: m3-free-list-reciprocal-links

The source guard landed in session 3873. Restore the patch pipeline before
running the allocator-route smoke; do not resume the M5 writer sweep until
this guard class is either validated or the environment is explicitly
blocked.

Competing hypotheses and discriminator:

- H1: malformed free-list successor links occur on the failing route; the
  corrupted-link control fires while the valid-link control continues.
- H2: the route only publishes reciprocal links; valid and corrupted controls
  show no runtime guard fire because the bad-link arm is not reached.
- H3: the new complete-block predicate rejects a legitimate boundary case;
  the valid allocator control fires the guard or fails to return normally.

The discriminator is one patch build plus one allocator smoke containing both
valid-link and deliberately corrupted-link controls. H1 requires a guard hit
only in the corrupted arm; H2 requires a clean valid arm and no natural-route
guard hit; H3 requires a guard hit or failure in the valid arm. Record both
the guard counter and allocator return/queue state.

Exact prerequisite and build commands:

    command -v mips64-elf-gcc
    command -v mips64-elf-ld
    test -x build/Debug/N64Recomp.exe
    cmake --build build --config Debug --target PatchesLib

Then run the existing allocator-route smoke from `patches/README.md`, using
SIGKILL for watchdog termination. If any prerequisite is still absent, record
the direct output and do not claim runtime validation.
