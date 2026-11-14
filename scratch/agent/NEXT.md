# NEXT (s7332): item 24 — name the allocation path of the flags&4 carve block the host alloc map never sees
HYPOTHESIS-ID: hostmap-carve-blind
Context: s7331 closed item 23 (H-audio-only). Its guest heap walk showed the 0x809B6010 "post-free" writes sit inside a guest-ALLOCATED
fl=6 block (0x808927F0+0x28D800 after sync 4; 0x806F5FF0+0x41A000 after syncs 7/10, forced L4 dd8 21:9) that rs64_s6063_malloc never
reported; it spans the framebuffers and the temp arena (head 0x8010FEFC rebuild ranges == rt64_writeback ranges). s6128 met the same
thing at 21:9 (0x2DB000 / 0x3E4B00 "created by a path the heaplog misses"). Every ALLOCMAP consumer (s7317 holders, s7324 class G,
s7325 gap classes, s7331) therefore classes the fb/temp-pool region as freed/untracked.
Hypotheses:
- H-inner: the block comes from rs_malloc_s5041_inner (or the 0x80001ACC body) entered by a path that skips the hooked wrapper.
- H-carve: ensureHeapInitialized / partitionFramebufferMemory writes the header by hand (no allocator call): retail carve.
- H-heapcap: our s6631 heapcap patch (tools/apply_s6031_far.py, wide only) or s6689 heapslot plants/resizes the header.
Discriminating measurement (ONE build, ONE run): ROGUESQ_STORE_WATCH on the header line of the block (first run once to read the
address from the s7331 g= field at the same recipe; it was 0x808927F0 / 0x806F5FF0, so watch 8927F0:892800 and 6F5FF0:6F6000 in two
runs or one wider range) -> the writing guest PC names the function; plus the retail-settings dd1 4:3 arm (scratch/s7331/run_e.zsh
recipe) with the g= field to see whether a fl=6 carve block exists at 4:3 (H-heapcap predicts wide-only).
Outcome map: PC in rs_malloc internals called from a non-hooked caller -> H-inner, hook it (one fixup line) and re-run s7331 report
(the 2:6 rows must turn host-live); PC in partitionFramebufferMemory/ensureHeapInitialized -> H-carve, register the carve block in
the s7317 map at that point; PC in the s6631/s6689 helper -> H-heapcap, same registration from our patch.
Also fold soak s7331_abort_resetw when it lands (abort-route resets; exit 0 = item 23 holds there too).
