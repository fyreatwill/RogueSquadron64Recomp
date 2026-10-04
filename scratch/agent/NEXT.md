# Next work unit: validate the accumulated M3 patch pipeline

HYPOTHESIS-ID: m3-patch-pipeline-validation

The current unit landed one bounded guard in `patches/heap_guards.c`:
`bump_cursor_ok` rejects an existing non-null `heap_bump` that is not a
KSEG0, 0x100-aligned allocator cursor before queue-link stores. The writer is
the allocator's `heap_bump = popped + 0x100` publication; that value is
legitimate only at the next block boundary, so this is a guard rather than a
mitigation for a known legitimate value.

Competing hypotheses:

- H1: the configured build now exposes `PatchesLib` and the accumulated MIPS
  patch can be compiled, linked, regenerated, and host-built.
- H2: the patch target remains absent or the MIPS toolchain remains missing,
  so no MIPS/runtime qualification is possible.
- H3: the ordinary Debug target is independently broken by this change.

Discriminator: run both build commands in one iteration and record target
discovery, MIPS compiler/linker availability, and each build result. H1 is
selected only if the patch pipeline completes; H2 if the patch target or
toolchain is absent; H3 if the ordinary target fails while the patch
preconditions are present.

Commands:

    cmake --build build --config Debug --target PatchesLib
    cmake --build build --config Debug --target RogueSquadron64Recomp

Do not add another guard until this validation checkpoint is resolved.
