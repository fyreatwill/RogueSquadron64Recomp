# NEXT: identify what guest code at 80007A44/80007AA0/80007AFC does, and whether its off-chain head stores are the chunk loss
HYPOTHESIS-ID: g1c-dd-phase2
Facts (s6560): head is only rewritten by hooked guest stores (tracked==actual, 199/199, positive control fired). 134+ OTHER stores at pc 80007A44/AA0/AFC set head to a node off the old chain (see PORTING-STATE s6560). Reclaim kind=1 never runs.
Hypotheses:
- H-A: those 3 pcs are a legit allocator (e.g. takes chunk from a per-size free list / popped via findAndUnlink) that reads the head from a different variable and writes it back, losing the chain prefix = the writer of the loss. Predicts: loss per burst == old-chain prefix length between oh and nv's position.
- H-B: they are pops from a second structure whose pointer was aliased to the cache slot by our fixups; harmless to the list. Predicts: walk(actual) after the store >= walk(before) - 1.
- H-C: stale local (_h captured in a recompiled function across a call that pushed/popped) written back. Predicts: nv == value of head at function entry.
Discriminator (ONE build): extend rs64_s6559_head OTHER rows to log walk(oh) before and walk(nv) after (cap 8192), plus whether nv equals the head value seen at the last begin or at previous store from the same pc. Find the function containing 80007A44 via the symtab (nm -n) and read its recompiled C. No new run needed if the log suffices; else s6553_run.sh 4 2 same env as hw6. Positive control: a pop (nnear row) must show walk delta -1.
Do NOT redo head-store classification, tracked-vs-actual, census or chunkcut.
