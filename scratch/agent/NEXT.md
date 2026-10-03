# Next work unit: validate the heap metadata-slot guard override

HYPOTHESIS-ID: m3-heap-metadata-slot-guard

The work unit is the bounded M3 guard change in `patches/heap_guards.c`:
metadata slot pointers must equal their linker-published addresses before any
queue-link store. This is a code change, not another diagnostic field.

Competing hypotheses and discriminator:

- H1: the free-list metadata slots are fixed game globals; exact-address checks
  preserve normal allocator behavior and reject only corrupted slot pointers.
- H2: one or both slots are legitimately relocated; exact checks reject normal
  allocation and the original KSEG0 checks are required.
- H3: the patch cannot be built in this checkout; validation remains blocked
  by the missing configured patch toolchain/target.

Discriminating measurement: build `PatchesLib` and run the allocator-route
smoke. H1 requires a successful patch build and unchanged allocator smoke;
H2 requires an allocator failure attributable to a relocated slot; H3 is
selected only if the build command proves the required compiler, N64Recomp,
or CMake target is absent.

Starting command:

    cmake --build build --config Debug --target PatchesLib

If the target exists, run the repository's allocator-route smoke from the
configured build directory and capture its exit/log. Do not repeat the retail
task-pointer oracle join.
