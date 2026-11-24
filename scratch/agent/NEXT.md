# NEXT (s7892)
HYPOTHESIS-ID: g3-snap3-default
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: s7891 closed island A (g3-cinematic-half-frame-phase) as H-index. The crawl's post-load frame stores 1/60 on retail but
2 VI under the ROGUESQ_RETAIL_SNAP=1 pin. ROGUESQ_RETAIL_SNAP=3 (unpins only the first frame after a flags-clear / prev==-1 reset)
removes island A on m11 (scratch/s7891/fix3b: exact from port 3397, flight 2554/2554, det ticks identical). Single mission so far.
Unit: confirm on a second mission where island A recurred (m6 = 0x31=5; s7870 island A N159 identical to m11):
  env RBIN=1 SNAP=3 zsh tools/s7849_det_pair.sh 5 scratch/s7892/m6
  python3 tools/s7868_det_frame_cmp.py scratch/s7892/m6/r1/retail.bin scratch/s7892/m6/p1.bin --plant --neg scratch/s7892/m6/p2.bin
Hypotheses: H-general (SNAP=3 removes island A on m6 too, flight stays exact) -> make SNAP=3 the s7849_det_pair default (one-line
  change, keep SNAP=1 reachable), rescore nothing else. H-m11-only (island A persists on m6) -> the post-load value there differs
  (retail's post-load frame can be 1, 2 or 3 VI, per load); dump the crawl site with tools/s7891_crawl_clock.sh EEP=<m6 eep> and read it.
  Flight non-exact under SNAP=3 -> SNAP=3 changes the pinned flight path; keep =1 as the default and record it.
Controls: the plant (now mid-flight, s7891 tool fix) and the unpinned p2 neg; also report whether port pre-flight phase 6 exact span
starts at the first phase-6 frame.
Budget: 1 iteration. Then pick the next ladder item (Next steps 1+: owner looks are waiting; G6/G5 items are owner-gated).
