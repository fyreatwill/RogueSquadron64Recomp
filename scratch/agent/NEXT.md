# Next work unit: qualify the M3 allocator cursor/free-list ownership class

HYPOTHESIS-ID: m3-allocator-cursor-free-list-ownership

Before the next runtime qualification, perform one bounded source audit and
ordinary Debug build for the missing ownership relation in `func_80007D74`.
The new guard must reject `heap_bump` when it aliases any node reachable from
`heap_free_head`, before the free-list dequeue or active-queue append stores.
Do not change audio, generated functions, or the M5 route.

Competing hypotheses and discriminator:

- H-m3-cursor-free-alias: `heap_bump` and a free-list node can alias; the new
  guard closes a real cross-owner publication hazard. Discriminator: the
  complete bounded free-chain walk is present and checked before mutation.
- H-m3-cursor-free-disjoint: the allocator invariant already makes the cursor
  disjoint; the audit should prove the relation structurally and the new guard
  remains a defensive no-op. Discriminator: all cursor and free-list writers
  are enumerated and no alias path exists.
- H-m3-invalid-chain: a malformed free chain is the actual class; the walk
  must reject invalid nodes/cycles rather than silently accept a cursor test.
  Discriminator: bounded traversal returns failure for invalid or overlong
  chains before any publication.

Exact commands:

1. Inspect `patches/heap_guards.c` and `patches/syms.ld`; add the guard with
   an `ORIGIN:` naming `heap_bump` and free-list link writers.
2. Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Record that `PatchesLib` runtime qualification remains unavailable if the
   configured macOS graph still lacks the MIPS GCC/LD toolchain.

Expected outcomes: a successful ordinary Debug build plus the committed guard
selects H-m3-cursor-free-alias as a landed ownership boundary, but does not
claim runtime firing; a failed build selects H-m3-build-invalid; a source
audit finding no missing relation selects H-m3-cursor-free-disjoint and the
guard must not be added.
