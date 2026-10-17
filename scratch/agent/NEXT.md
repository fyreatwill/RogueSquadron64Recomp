# Next: make the host-side PatchesLib qualification regeneration-safe

The direct host-side qualification exposed a generated-source defect: the
existing ELF recompiles, but `RecompiledPatches/patches.c` calls
`findAndUnlinkSmallestEntry` without a declaration. An external prototype
control compiled and archived successfully, so the next unit is to repair the
declaration path and rerun from regenerated output. Do not claim this proves a
fresh MIPS compilation.

Competing hypotheses and discriminator:

- H1: adding the helper prototype to the regeneration-safe declaration path
  makes the generated host source compile and archive cleanly.
- H2: the prototype fix is insufficient because regeneration still omits a
  required declaration or another host compile error appears.
- H3: the host-side artifact qualifies after the fix, while fresh source
  qualification remains blocked until the external MIPS GCC/LD pair is
  supplied.

Discriminating measurement: regenerate, compile without the external
prototype shim, archive, and run `nm`. H1/H3 require zero compile errors and a
defined `allocateDisplayListBuffer`; H2 is any remaining generated-source
failure. The same-run positive control is the defined override symbol.

```sh
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
