# NEXT: G1d step 3 - widen the framebuffer under ROGUESQ_ASPECT=16:9
HYPOTHESIS-ID: g1d-widescreen
s6108: aspect lever (ROGUESQ_ASPECT_SCALE) confirmed ~1/k on craft width. First fold s6107_g1d_k2p0 from SOAK-RESULTS.md (expect craft ~half of k1.0 width, flight fb index 4500).
Then ONE build: with ROGUESQ_ASPECT=16:9 set guPerspective aspect scale = 4/3 / (16/9) and widen game colour image width, scissor and VI width; run L1 with a 16:9 window and capture. Outcomes: extra width drawn undistorted => proceed to HUD x anchoring; stretched => viewport/scissor not widened; black bars => VI/colour image width missed.
