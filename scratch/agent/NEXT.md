# Next work unit: validate the heap block-span guard in the normal allocator route

HYPOTHESIS-ID: m3-heap-block-span-audit

This iteration landed the guard-class change in `patches/heap_guards.c`.
The writer under audit is `func_8002221C` plus the free-list link stores; the
new predicate rejects only a KSEG0 block base whose complete `0x100`-byte
object would cross `0x80800000`. It does not alter any valid in-range block.

Competing hypotheses and discriminator:

- H1: All allocator blocks are wholly inside the 8 MiB KSEG0 RDRAM window;
  the new predicate is behavior-preserving. Select if the patch builds and
  the normal route remains clean with no new allocator guard return.
- H2: A published block can be in KSEG0 but too near the upper boundary;
  the old predicate admitted an unsafe full-object dereference. Select only
  if a bounded allocator audit or runtime evidence identifies such a pointer.
- H3: The patch changes the MIPS ABI or patch-link output rather than only
  the guard class. Select if the patch build or generated symbol/link check
  fails, or if the override is not present in the produced library.

Discriminator: build `PatchesLib`, then inspect the generated patch symbol and
link output for `func_80007D74`; no runtime claim is valid without a normal
allocator-route smoke run. A build failure selects H3. A successful build
with the override present selects H1 provisionally; H2 remains unevaluable
until a target-phase allocator pointer sample exists.

Exact commands:

    cmake --build build --config Debug --target PatchesLib
    rg -n "func_80007D74" RecompiledPatches/patches.c

Do not repeat the s3841 retail/port task-field observation until this guard
change has been validated. If the target is unavailable on this host, record
that as a build-environment blocker rather than inventing runtime evidence.
