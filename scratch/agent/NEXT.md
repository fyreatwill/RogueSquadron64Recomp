# NEXT (s7895)
HYPOTHESIS-ID: g3-island-a-lever
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7894): island A is H-index on m6 and m11. `ROGUESQ_RETAIL_SNAP=3 ROGUESQ_SNAP3_ONLY=6` (only post-reset fire 6 = crawl
post-load frame unpinned, el forced 0) removes it deterministically on m6 (scratch/s7894/m6o vs control m6c). Plain =3 is host-timing
dependent (real el 0 or 781250), so it can never be a det default.
Unit (ONE bounded check, then decide the det-pair default):
  Is fire 6 the crawl on other missions, and does ONLY=6 keep flight exact there? Run on m11 and m3 (one at a time):
  env RBIN=1 SNAP=3 P1E=ROGUESQ_SNAP3_ONLY=6 zsh tools/s7849_det_pair.sh 10 scratch/s7895/m11   (retail: reuse scratch/s7872/v10/r1 if
  still present, hard-link oracle.log + retail.bin into OUTDIR/r1 first; else fresh)
  then python3 tools/s7868_det_frame_cmp.py r1/retail.bin p1.bin --plant in OUTDIR. Check `[snap7891] ... forced 0` VI is the crawl
  (~5600) in p1/run.log. The det_pair p2 arm can exceed the 10-min task cap: run it in the foreground with a long timeout or skip p2.
Outcomes: island A gone + flight exact on both -> make SNAP3_ONLY=6 (with SNAP=3) the s7849_det_pair default (SNAP= unset keeps =1
  for byte-identical old runs: add a new SNAP=6 shorthand), close island A; fire 6 not the crawl on some mission -> key the unpin on the
  crawl dt site (ra 0x800C9D94 path: mark 0x800C6674 sets a flag) instead of the fire index; flight forks -> lever not general, document.
Then island B (N212@6071 on m6, unchanged by the lever) is the next pre-flight item.
