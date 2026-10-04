# Next work unit: audit empty active-queue tail alias

HYPOTHESIS-ID: m3-active-queue-tail-alias

Land one bounded guard in `patches/heap_guards.c` for the empty active-queue
append path, then build the ordinary host target. The guard rejects the case
where the free-list block selected by `func_80007D74` is the same object as
the published active-queue tail before any queue-link stores. The writer is
the free-list dequeue publishing `popped`; that alias is not legitimate
allocator ownership. MIPS patch compilation is expected to remain unavailable
in this checkout, so do not claim runtime qualification.

Competing hypotheses:

- H1: the free-list dequeue can alias the active tail in a corrupt state; the
  new pre-store guard rejects it and preserves all valid queue paths.
- H2: the alias is a legitimate empty-queue representation; the guard would
  reject valid allocation and is not safe to land.
- H3: the existing non-empty-only check already covers this state; the new
  branch is redundant and should be removed.
- H4: the patch source cannot be compiled in this checkout; code review and
  host-target build are insufficient for MIPS/runtime qualification.

Discriminator: inspect the original append invariant and compile the changed
host tree. A valid empty queue has no published queue head and therefore no
queue-owned tail; the tail-alias case is only a corrupt ownership collision.
The host build must pass, while the `PatchesLib`/MIPS build result is recorded
as either successful or unavailable. H1/H2/H3 are bounded to this exact
empty-queue alias class; H4 is an environment result, not a runtime claim.
