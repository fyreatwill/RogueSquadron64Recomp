# Next work unit: add the next M3 free-list/active-queue alias guard

HYPOTHESIS-ID: m3-free-list-active-queue-alias

Audit and patch `patches/heap_guards.c` so a free-list block cannot be
inserted into the active queue when it aliases the queue sentinel, active
head, or current queue node. Build `PatchesLib` if the configured target is
available; otherwise record the exact prerequisite failure. Do not claim
runtime validation without the MIPS patch pipeline.

Competing hypotheses and discriminator:

- H1: the popped free-list block is distinct from every active-queue node;
  the new guard is never selected in a valid allocator-route smoke.
- H2: malformed state can alias the popped block with `tail`, the active
  queue head, or `tail->next`; the new guard returns before queue-link stores.
- H3: the presumed queue topology is wrong and one of the alias checks rejects
  legitimate allocations; the allocator-route smoke regresses or stops.

The discriminator is the patch build plus, if the toolchain exists, one
allocator-route smoke with guard-hit/route controls: H1 is a successful build
and unchanged smoke, H2 is a guard hit before queue writes, and H3 is a
legitimate allocation rejection/regression. The code-level ORIGIN is the
allocator's free-list and active-queue link stores: one block cannot be both
free and active in legitimate state.

Exact build command:

    cmake --build build --config Debug --target PatchesLib

If the target is available, run the existing allocator-route smoke from the
patch documentation and capture its output under `scratch/agent/`.
