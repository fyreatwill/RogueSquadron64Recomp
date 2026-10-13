# Name the allocation/loader that takes the audio node arena 0x80179400-0x8017B000

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4779: the +5808 crash is the synth list walking an arena that was repurposed (pointers become ptr-0x80170000 offsets, then foreign data) at VI 640 phase 3 with the synth still registered (no dereg). Hypotheses: A) allocator overlap (rs_malloc hands out inside the live 0x80179480/73728 block, s4558 lead); B) legit freed block (audio shutdown not run / not wired) reused by loader; C) unhooked bulk store (memcpy/DMA) into the arena.
Discriminator: run scratch/agent/s4779_listwriter.sh with the rs_malloc/rs_free log (see s4558 hooks in main.cpp rs64_m5_lowfield_store / ROGUESQ_LOG_ALLOC_CALLERS) gated to ranges overlapping the arena, and print the allocation returned just before the first `[s4779-unhooked]` row (caller ra + size). A => returned range overlaps a live block; B => a prior free of the arena block; C => no alloc event, only DMA/copy.
Control: the alloc log must show the original audio arena allocation near boot.
Write ORIGIN: if a guard is added.
