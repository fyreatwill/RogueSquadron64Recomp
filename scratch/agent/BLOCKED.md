# Blocked: M3 patch qualification

Need a usable `mips64-elf-gcc` and `mips64-elf-ld` toolchain, either installed
on this Mac and exposed through `PATH`/`MIPS_TOOLCHAIN_DIR`, or a host with the
toolchain where the repository can be built.

This iteration measured `command -v mips64-elf-gcc` and
`command -v mips64-elf-ld` as absent. CMake skipped the patches graph,
`PatchesLib` had no build rule, and the ordinary target built successfully.

The unblocking experiment is exactly the same configure/build sequence after
the toolchain is supplied; success must produce `patches.elf`, generated
`RecompiledPatches/patches.c`, and `PatchesLib` before runtime qualification.
