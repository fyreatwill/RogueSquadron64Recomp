# Next work unit: validate the accumulated M3 heap patch when toolchain exists

HYPOTHESIS-ID: m3-heap-guard-validation

The alignment guard landed this iteration in `patches/heap_guards.c`. Do not
add another guard or repeat the M5 candidate census until the patch pipeline
can compile and link the accumulated override.

Competing hypotheses:

- H1: allocator/free-list block bases are always `0x100`-aligned; the new
  `block_ok` predicate preserves every legitimate block and rejects only an
  invalid base.
- H2: the allocator can legitimately publish a non-`0x100`-aligned KSEG0
  block; the new predicate would reject valid queue work and must be reverted.
- H3: the patch pipeline is unavailable in this checkout, so neither runtime
  hypothesis is evaluable yet.

Discriminator: build `PatchesLib` and run the patched binary with the normal
heap positive control. H1 requires successful patch compilation plus normal
heap/route progress with zero alignment-guard failures; H2 requires a
legitimate non-`0x100`-aligned block observed in the same run or a route
regression attributable to the predicate; H3 is selected only by a fresh
`PatchesLib`/toolchain failure.

Commands:

    cmake --build build --config Debug --target PatchesLib
    cmake --build build --config Debug --target RogueSquadron64Recomp

If `PatchesLib` becomes available, run the normal phase-gated heap/route
recipe from `build/` with SIGKILL watchdog termination and inspect the guard,
heap progress, title VI 1024, and hangar VI 512 controls. Preserve the
`ROGUESQ_AUDIO_UCODE=1` M5 arm; it is not the active work unit.
