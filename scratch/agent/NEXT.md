# NEXT (s7893)
HYPOTHESIS-ID: g3-island-a-m6-source
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7892): on m6 (0x31=5) ROGUESQ_RETAIL_SNAP=3 makes the crawl dt equal retail (cum delta 0, plant PASS) but island A N159@3398
stays in the RDP stream; on m11 SNAP=3 removed it. So m6 island A has another time/state source. SNAP=3 is pre-flight gated now.
Unit (ONE bounded discriminator, then park island A as pre-flight timing class):
  Which guest value differs on the crawl's first frames (port 3397-3610) on m6 under SNAP=3? Re-run the crawl dump with the
  cinematic/crawl accumulators plus the crawl object's scroll/spline time words added to M in tools/s7891_crawl_clock.sh (one build-
  free run, retail oracle log reusable from scratch/s7892/crawl6/r1 only if M is unchanged, else one fresh retail run):
  env EEP=scratch/s7892/m6/lvl.eep SNAP=3 zsh tools/s7891_crawl_clock.sh scratch/s7893/c6
Hypotheses: H-carry (state carried in from the hangar segment, which SNAP=3 moves to -2 VI vs retail: the crawl's start position
  is set from an accumulated hangar/cinematic time) -> a crawl-start word differs by a hangar-derived amount;
  H-text (the island is the text content/scroll origin, not time) -> time words equal and an object position word differs;
  H-retail-rdp (capture lag on this mission) -> all guest words equal on both sides.
Retail bin: scratch/s7892/m6/r1/retail.bin; port SNAP=3 bin scratch/s7892/m6s3c/p1.bin.
Budget: 1 iteration. Then park island A in CURRENT-TRUTH and take the next ladder item (everything else is owner-gated).
