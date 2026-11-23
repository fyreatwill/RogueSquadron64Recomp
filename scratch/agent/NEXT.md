# NEXT (s7872)
HYPOTHESIS-ID: g3-cinematic-half-frame-phase
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7871): flight render = retail on 4 missions (b17, m12, m6, m11 Bespin 2519/2519). The only non-exact frames are pre-flight.
Island A (opening cinematic, 64 PRIM-FF tris, p1 == p2) is value-identical in m6 (s7870) and m11 (s7871): the port draws that
element ~half a frame later in animation time (offset 0.51 x speed).
Unit (offline, no game run; retained data scratch/s7871/v10: r1/oracle.log, p1/run.log, p1_rand.txt; s7870 v5 the same):
decide what sets the half-frame phase. Hypotheses: H-vi-phase (the cinematic's animation clock samples a VI/frame counter and the
port starts the cinematic at a different VI parity relative to retail's gfx task), H-dt (the cinematic advances by a per-frame dt
that differs by half a step on the first frame: s7835 DT / s7839 snapshot rows in p1 run.log vs the oracle dt watch), H-count
(retail double-counts or skips one VI before the cinematic: compare VI count between boot and port frame 3393 / retail 2864).
Discriminator: for both missions, the VI index at the cinematic's first frame (port 3393 / retail 2864) mod 2 and the dt row of
that frame on both sides. Same parity offset in both missions + equal dt -> H-vi-phase; dt differs -> H-dt; VI counts differ by
an odd number -> H-count. Re-capture only if the retained logs lack VI stamps (then one det pair with RBIN unset is enough).
Fallback: extend coverage with one more mission (env RBIN=1 zsh tools/s7849_det_pair.sh <v> scratch/s7872/v<v>), delete bins after.
