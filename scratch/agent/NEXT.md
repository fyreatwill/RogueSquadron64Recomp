# Next work unit (s4464): does rs_malloc know the SND blob that spans 0x801928E8..0x8021E538?

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4463): insert pointers span ~0x8C000 bytes from 0x801928E8; rs_malloc handed the audio node block 0x80193C20 and buffer 0x80196CC0 inside that span (VI 640). Port-only.
Hypotheses: (A) SND blob allocated by rs_malloc at a base below 0x80193C20 with size covering it, then allocator overlaps = allocator/free bug; (B) SND blob never rs_malloc'd (DMA'd to a fixed or stale address) so heap is unaware = port load-path bug; (C) span is a pointer table over data the retail also overlaps (benign, pool nodes unlinked).
Discriminator: one run logging every rs_malloc/free (0x80001ACC / its free) call with size+return+ra that intersects 0x801928E8..0x8021E538, plus relocateSndPointer arg/return. A: an alloc covering 0x801928E8+ exists and a later alloc overlaps it (or it was freed). B: no alloc covers the span. C: needs oracle retail comparison.
Commands: hook rs_malloc return (fixup script for generated code, or store hook on its result), reuse scratch/agent/s4463_run.sh recipe.
