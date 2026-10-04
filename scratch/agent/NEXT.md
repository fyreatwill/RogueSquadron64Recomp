# Next work unit: audit the active-queue tail-anchor guard

HYPOTHESIS-ID: m3-active-queue-tail-anchor

Before building, retain this hypothesis table and discriminator as the audit
contract. Add one guard in `patches/heap_guards.c` for the active-queue append
anchor: when the published queue is non-empty, the node reached via
`heap_tail_loc->next` must either be the queue head with no predecessor, or
have `q->prev == *heap_tail_loc`. Then run
`cmake --build build --config Debug --target RogueSquadron64Recomp` once and
attempt `cmake --build build --config Debug --target PatchesLib` once. No
runtime soak is valid without a built MIPS patch.

Competing hypotheses:

- H1: the tail metadata is a legitimate predecessor of the terminal queue
  node, so the new relation check passes for valid allocator state.
- H2: the queue head is the terminal node, so the valid empty-predecessor
  special case passes.
- H3: a foreign or detached tail is possible, so the new guard rejects it.
- H4: the patch pipeline is unavailable, so source-level correctness cannot
  be runtime-qualified in this checkout.

Discriminator: the guard must accept both valid queue-anchor shapes and reject
the detached/foreign shape in a MIPS/runtime test. If `PatchesLib` is absent,
the result is H4 only; the ordinary host build is not patch validation.
