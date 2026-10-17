# Next: qualify the host-side PatchesLib artifact without the cross-compiler

The fresh source-to-MIPS qualification remains externally blocked, but the
existing `patches/patches.elf` and generated host source permit a bounded
host-side qualification. Do not claim this proves a fresh MIPS compilation.

Competing hypotheses and discriminator:

- H1: N64Recomp can regenerate the host source from the existing ELF, Clang
  can compile it, and the archive exports the intended override.
- H2: the existing artifact is stale or incompatible; regeneration, compile,
  or symbol verification fails.
- H3: host-side qualification passes, but fresh source qualification remains
  blocked until the external MIPS GCC/LD pair is supplied.

Discriminating measurement: one run of `build/N64Recomp patches.toml`, host
compile/archive, and `nm` must succeed and show `allocateDisplayListBuffer`.
H1 selects the artifact path; H2 selects an artifact failure; H3 remains the
known open dependency for fresh source qualification.

Commands:

```sh
build/N64Recomp patches.toml
clang -c RecompiledPatches/patches.c -o /tmp/rs64-patches-host.o \
  -I include -I RecompiledPatches \
  -I lib/N64ModernRuntime/ultramodern/include \
  -I lib/N64ModernRuntime/librecomp/include \
  -I lib/N64ModernRuntime/N64Recomp/include
ar rcs /tmp/rs64-PatchesLib.a /tmp/rs64-patches-host.o
nm -g /tmp/rs64-PatchesLib.a | grep allocateDisplayListBuffer
```

HYPOTHESIS-ID: patcheslib-host-artifact-qualification
