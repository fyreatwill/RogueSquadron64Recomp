# Next work unit: validate the active-queue reciprocal-link guard

HYPOTHESIS-ID: m3-active-queue-reciprocal-guard

The current iteration landed one regeneration-safe M3 guard in
`patches/heap_guards.c`. Before the next behavioral experiment, restore the
patch build prerequisites and run the allocator smoke if they become
available.

Competing hypotheses and the discriminating measurement:

- H1: the patch pipeline is available and the guard can be built and run. A
  successful `PatchesLib` build plus allocator smoke reaching the guarded
  insertion path selects H1; a guard fire must be attributed to the named
  malformed reciprocal link, not treated as proof of a runtime corruption
  source.
- H2: the source change is valid but the configured patch pipeline remains
  unavailable. `cmake --build build --config Debug --target PatchesLib` and
  direct checks for `mips64-elf-gcc`, `mips64-elf-ld`, and
  `build/Debug/N64Recomp.exe` select H2; no runtime allocator conclusion is
  allowed.
- H3: the reciprocal-link invariant is too strong for the retail queue shape.
  Only a built allocator smoke with a legitimate queue transition that hits
  the guard and then fails selects H3; source inspection alone cannot select
  it.

Discriminator: the first successful patch build followed by the allocator
smoke's guard-path result. Do not spend the next iteration on another guard
until this build/runtime result is available.

Exact commands:

    cmake --build build --config Debug --target PatchesLib
    zsh scratch/agent/soak_queue/<allocator-smoke>.sh

If the build is still blocked, record the exact missing target/tool output and
ask for the toolchain or CMake configuration needed to run the smoke.
