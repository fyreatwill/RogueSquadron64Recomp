# NEXT (s7904)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7903, scratch/s7903/bind.txt): on the m11 crawl-tail odd serials the port draws the SAME flame instance (mtx 700100/700140)
at the SAME vertex address as retail, but with retail's values from the neighbouring drawn frame: 700100 one drawn frame LATE,
700140 one EARLY (block hashes, retail task overlay replay control 6/6 exact). So the residual is the rand-replay ordinal keying of
the two flame sites (0x80054174 / 0x800541FC) in the crawl tail, offset by one 16-call frame with opposite signs per site.
s7901's single-site whole-burst SKEW fixed one instance and broke the earlier (already exact) frames.
Work unit: make ROGUESQ_RAND_REPLAY_SKEW tail-scoped and run the sign arms in ONE iteration (iron rule 13, max 2 runs at a time).
  1. src/main/rt64_render_context.cpp ~line 111: accept SITE:BURST:DELTA[:FROM] (apply delta only when in-burst ordinal >= FROM;
     missing FROM = 0, byte-identical to s7901). Find FROM per site = the in-burst ordinal of each site's first call in the
     crawl tail (crawl call ~2675; the burst-2 ordinal at port frame 5639 - read it from the p1 rand trace
     scratch/s7902/m11snap/p1_rand.txt.zst, rp_bno/ordinal per site at the frame of serial 5681).
  2. Arms (base = scratch/s7900 m11burst recipe, APM=1 burst replay 600, SNAP=3 ONLY=c,7, see scratch/s7902/run_snap.sh):
       A: 800541fc:2:+16:F1 , 80054174:2:-16:F2      B: signs swapped      C: control = no SKEW (must reproduce E2674 N1@5639 ...)
  3. Score with tools/s7868_det_frame_cmp.py map (and tools/s7903_retail_bind.py on new snapshots if an arm is partial).
Expected: one of A/B makes the crawl tail contiguous-exact (map E through ~5771) without touching frames before 5639 -> island B
on m11 closed; then m6 (0x31=5) with the same arm. If neither: the per-instance offset is not per-site (instances share a site
and alternate) -> key the skew on (site, parity of the call within its 16-call frame) instead.
Tools: tools/s7903_retail_bind.py (ORACLE.log RETAIL.bin PORT.bin -101 VI0:VI1 SNAPS...), tools/s7903_retail_overlay.py,
retail m11 dump scratch/s7903/r1 (VI 10540:10620 only).
