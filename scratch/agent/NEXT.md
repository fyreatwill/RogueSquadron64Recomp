# NEXT: G1d step 2d - read the s6107 k-sweep, then widen the framebuffer
HYPOTHESIS-ID: g1d-widescreen
Fold s6107_g1d_k0p5/k1p0/k2p0 from SOAK-RESULTS.md. Compare the SAME early fb dump index (first flight VI, fixed intro camera): measure craft/ring pixel width per k. Width ~ 1/k => lever is the projection aspect (H-lever); unchanged => H-other. k=1.0 must look retail (control).
Then ONE build widening game colour image/scissor/VI width under ROGUESQ_ASPECT=16:9 plus a 16:9 window screenshot; then HUD x anchoring.
