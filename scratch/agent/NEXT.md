# NEXT: G1c - size the pool multiplier to the heap
HYPOTHESIS-ID: g1c-draw-distance
s6062: px4 at dd1 hits rs_malloc NULL (control fired) => poolx alone exhausts the 8 MB guest heap. px2 is clean (dd1.5, dd2). px3_dd2 crashes at a second NULL deref (no mallocnull).
Hypotheses: (A) heap budget between px2 and px3 is the limit -> find the fit point; (B) a cheaper consumer (stream tile cache, audio buffers) can be shrunk to buy room for px3/4; (C) terrain still flat at px2 because pool is not the extent limit (HUD restored only).
Unit: instrument rs_malloc wrapper (src/main/upstream_compat.cpp rs64_s5041_malloc area) to log request size + running live-bytes high-water at poolx alloc and on first NULL; run px2, px2.5(if poolx accepts fractions, it does: atof), px3 at dd1 in one batch; then check HUD/terrain via tools/g1c_ddtog_fold.py with --hud. Control: px4 must show NULL.
Check queued px4_dd2b/px8_dd1 results in SOAK-RESULTS first.
