The M3 active-queue guard cannot be runtime-validated in this checkout.

Need from the human: provide a Windows build environment or install/provide
the `mips64-elf-gcc`/`mips64-elf-ld` toolchain and a built `N64Recomp.exe`,
then point CMake at them. This iteration measured that both required tools are
absent, CMake skipped the patch pipeline, and `PatchesLib` has no build target.

The falsifying experiment is to rerun configure with those exact tools present:
if `PatchesLib` appears and reaches compilation, the current environment blocker
is refuted and validation can continue.
