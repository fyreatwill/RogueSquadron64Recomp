# Next: qualify a fresh PatchesLib source build when the cross-toolchain exists

The host-side declaration path is now regeneration-safe: generation from the
existing `patches.elf`, Clang compilation, archiving, and `nm` all passed in
Session 5341. The remaining unit is the source-to-MIPS step, which must not be
claimed from that artifact result.

Competing hypotheses and discriminator:

- H1: `mips64-elf-gcc` and `mips64-elf-ld` are available and the complete
  source-to-ELF-to-host pipeline can be run.
- H2: the cross-toolchain is absent, so fresh source qualification remains
  blocked and the next action requires supplying it.
- H3: the toolchain exists but the fresh source build or relink exposes a new
  source, linker, or regeneration defect.

Discriminating measurement: run `command -v mips64-elf-gcc mips64-elf-ld`,
then, only if both resolve, build `patches/patches.elf`, regenerate the host
source, compile, archive, and inspect `nm`. H1 requires a fresh ELF plus zero
host errors and a defined `allocateDisplayListBuffer`; H2 is the measured
absence of either compiler; H3 is any fresh-build failure. The same-run
positive control is the defined override symbol.

```sh
command -v mips64-elf-gcc mips64-elf-ld
make -C patches clean all
./build/N64Recomp patches.toml
clang -c RecompiledPatches/patches.c -o /tmp/rs64-patches-host-next.o \
  -I include -I RecompiledPatches \
  -I lib/N64ModernRuntime/ultramodern/include \
  -I lib/N64ModernRuntime/librecomp/include \
  -I lib/N64ModernRuntime/N64Recomp/include
ar rcs /tmp/rs64-PatchesLib-next.a /tmp/rs64-patches-host-next.o
nm -g /tmp/rs64-PatchesLib-next.a | grep -E 'allocateDisplayListBuffer|findAndUnlinkSmallestEntry'
```

HYPOTHESIS-ID: patcheslib-host-artifact-qualification
