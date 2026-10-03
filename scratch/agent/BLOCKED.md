# Blocked: M3 heap block-span guard validation

Need the MIPS cross-toolchain and the configured newer N64Recomp executable,
or valid replacement paths, from the environment owner. This iteration
showed `PatchesLib` is not a CMake target because
`E:/mips-toolchain/bin/mips64-elf-gcc.exe` and
`build/Debug/N64Recomp.exe` are absent; `/usr/bin/make` is present.

Already tried:

- `cmake --build build --config Debug --target PatchesLib`
- inspected the CMake conditional and build target list
- verified both configured executable paths are missing

The single refuting experiment is to restore/reconfigure those inputs and
confirm `PatchesLib` appears in the CMake target list. Then build it, verify
`func_80007D74` in `RecompiledPatches/patches.c`, and run the allocator smoke.
