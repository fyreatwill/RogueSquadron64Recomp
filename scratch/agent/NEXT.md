# NEXT (s7325): audio RSP reads in heap gaps — name the owner
HYPOTHESIS-ID: audio-heapgap-read
Context: s7324 (class G closed) found 40330 audio-bank RSP DMA reads (4092 distinct addresses, len 8-0xC8 = ADPCM frame / loop
state sizes, raw tag 0x80) whose address lies in no live rs_malloc block of the s7317 map, at dd8 21:9 L4. Some streams run
contiguously across a block end through the 0x10 header gap into the next block (0x80190440 -> 0x80190490 -> 0x801904E0; blocks
80190410..80190490 and 801904A0..801905A0). Table: scratch/s7324/l4c.log (DI lines, heap-gap rows), tools/s7324_rcp_report.py.
Hypotheses:
- H-freed: the region was a live block that has been freed; the audio still DMAs from it (stale sample/voice buffer: use-after-free).
- H-untracked: memory came from a path that bypasses rs64_s6063_malloc (realloc, a game sub-pool, MusyX/audio heap carved inside a
  free region, or allocations made before the hook arms).
- H-adjacent: one logical buffer built from adjacent small blocks (the gap is the next block's header), so a stream reading across
  is by design and the "gap" bytes are rs heap headers read as sample data (retail would do the same).
- H-dd: dd8 heap pressure only; dd1 (retail layout) shows no gap reads.
Discriminator (ONE build, ONE run of two arms):
1. In upstream_compat.cpp keep a freed-block history (ptr, req, free time, freer host pc) for the last ~64k frees under ALLOCMAP; in
   s7324 note(), for each heap-gap alias-only/none audio read, look the address up: inside a freed block (H-freed: report seconds
   since free + owner), exactly in a 0x10 header between adjacent blocks with the stream continuing (H-adjacent), or never allocated
   (H-untracked). Also count audio reads in "none" class below 8 MB that are in neither live nor freed blocks.
2. Positive control: =ctl frees nothing extra; instead once per second classify the start of the most recently freed block (must
   class H-freed) and the header word of a live block's successor (must class H-adjacent).
3. Arms: dd8 21:9 L4 (as s7324 run c) and dd1 4:3 L4, same build, run sequentially (one game at a time).
Outcomes: H-freed at dd8 only -> real UAF exposed by heap pressure: find the freer and the stale holder, fix the root cause.
H-freed at dd1 too -> retail behaviour, document. H-adjacent -> by design, close. H-untracked -> name the allocator path, add it to
the map, re-run class G for that region.
Run recipe: env LEVEL=4 TAG_SUFFIX=s7325 HOLD_S=200 WIDE_ROUTE=1 XENV_EXTRA="ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=8
ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_ASPECT=21:9 ROGUESQ_S7317_ALLOCMAP=1 ROGUESQ_S7324_RCPREF=ctl"
zsh scratch/agent/g1_level_coverage_common.zsh  (log build/rs64_s7324.log; 640 s watchdog; SIGKILL after).
