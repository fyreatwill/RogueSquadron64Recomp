# Next work unit: validate the landed M3 heap metadata-slot guard

HYPOTHESIS-ID: m3-heap-guard-validation

M5 session 3857 ruled out the dominant `0x800078EC` writer as a nonzero
image producer. No legitimate retail producer is currently identified, so do
not add an M5 writeback guard or repeat the closed destination census.

Competing hypotheses and discriminator:

- H1: the configured patch pipeline builds and the guard-linked allocator
  smoke reaches the guarded metadata-slot stores without rejecting legitimate
  fixed-slot pointers.
- H2: the pipeline/toolchain is still unavailable, so allocator behavior is
  unevaluable and no guard conclusion is allowed.
- H3: the build succeeds but the smoke shows an unexpected metadata-slot
  value; classify the writer and stop before changing the guard.

The discriminator is a successful `PatchesLib` build followed by the existing
allocator-route smoke, with the fixed linker addresses and guard diagnostics
captured. H1 requires the build and smoke; H2 is selected only by direct
tool/target failure; H3 requires a completed smoke with a value mismatch.

Exact checks:

    command -v mips64-elf-gcc mips64-elf-ld
    test -x build/Debug/N64Recomp.exe
    cmake --build build --config Debug --target PatchesLib

If the prerequisites are restored, run the allocator-route smoke documented
in `patches/README.md`; do not claim allocator behavior from a failed build.
