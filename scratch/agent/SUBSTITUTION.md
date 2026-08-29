# Session 3243 substitution

1. Planned unit stopped: `PatchesLib` cannot be built in this checkout. The
   configured CMake target is absent because the required MIPS/N64Recomp
   prerequisites are not installed on this host.

2. This iteration's evidence: `cmake --build build --config Debug --target
   PatchesLib` returned `make: *** No rule to make target \`PatchesLib'.  Stop.`
   `build/CMakeCache.txt` points at `E:/mips-toolchain`, while neither
   `mips64-elf-gcc` nor `N64Recomp` is on PATH. `RecompiledPatches/patches.c`
   is absent, and the existing `patches/patches.map` timestamp is July 9,
   before the August 29 guard edit.

3. Refuting experiment: run the same `PatchesLib` build on the configured
   Windows toolchain host (or reconfigure with installed MIPS GCC and
   N64Recomp paths), then verify the generated host source and override map.
