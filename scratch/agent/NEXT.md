# Next work unit: validate the accumulated M3 heap guards

HYPOTHESIS-ID: m3-heap-guard-validation

Build the MIPS patch pipeline for `patches/heap_guards.c`, then run the
validated allocator route and determine whether the new active-queue
reachability guard preserves legitimate allocations and rejects only malformed
chains. Do not add another guard or run the queued M5 writer census first.

Competing hypotheses:

- H1: the patch toolchain and target are available; compile, link, recompile,
  and host-link the guard successfully.
- H2: the toolchain is available but the guard changes valid allocator behavior
  or rejects a legitimate active queue.
- H3: the toolchain/target remains unavailable; record the exact missing
  command or target and stop the M3 validation loop pending human setup.

Discriminator: successful MIPS compile/link plus a valid allocator route with
the active-queue guard enabled. A host-only build is not MIPS validation.

Exact commands:

    cmake --build build --config Debug --target PatchesLib
    cmake --build build --config Debug --target RogueSquadron64Recomp

ORIGIN: `func_8002221C` and the active-queue link stores publish the node
successors and predecessors. The new guard treats a detached/cyclic terminal
as illegitimate; valid queue nodes must be reachable from the published head.
