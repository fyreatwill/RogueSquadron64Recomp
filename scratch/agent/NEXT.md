# NEXT (s7899)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7898): crawl-tail island B (m11 N213@6073, m6 N212@6071) has guest crawl dt EXACTLY retail (2887/2887, cum 0 VI, plant PASS),
so H-dt is refuted. 5-10 white PRIM FFFFFFFF tris drift per frame out of 225-345 (tri count equal or +-2, no frame shift). m11's
cinematic part is mostly the fire-7 post-load half-frame (lever ROGUESQ_SNAP3_ONLY=c,7: N1054 -> N213 + 604 cinematic remnants).
Unit (offline first, kept bins: retail scratch/s7895/m11k/r1/retail.bin, port scratch/s7898/m11c7/p1.bin.zst):
  1. Name the object. Dump the differing tris (port-only vs retail-only) of port frames 6073..6100 with screen x/y/size: stars (tiny,
     scattered, many frames) vs one model (clustered) vs crawl text (in the text band). Extend tools/s7896_island_b_probe.py with
     --dump (control: a planted YH+1 tri must appear in the dump at its coordinates).
  2. Hypotheses: H-object-rng (star/particle positions from a guest RNG that is NOT rand 0x80003430, e.g. an inline LCG, so the
     s7896 replay could not reach it; check whether the drifting tris' positions are a permutation of retail's = same set, other order),
     H-cam (crawl-tail camera tilt: all drifting tris shift by one common delta), H-anim (an object stepped by call count, not dt:
     per-tri delta grows linearly with frames).
  Discriminator: per frame, the dx/dy between each port-only tri and its nearest retail-only tri. Common delta -> H-cam; set
  permutation / random pairs -> H-object-rng; delta growing with frame -> H-anim. Then ONE run with a write watch on the object's
  position source (oracle --watch-write on retail + XTRACE on port) named by the result.
  3. The m11 cinematic remnants N79/N15/N22/N92/N396 (scratch/s7898/m11c7_cmp.txt): run the same dump on 6297 and 6731 to see if the
     same object carries over (then one fix closes both).
Lever recipe: scratch/s7898/run_m11c7.sh (p1only, SNAP=3 + P1E SNAP3_ONLY=c,7 + RAND_REPLAY).
