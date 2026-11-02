# NEXT: G3f hangar fish-eye during the ship-scroll pan
HYPOTHESIS-ID: g3f-hangar-fisheye-pan

Done s6790: G3e closed (lvl5/lvl10 dd4 clean). G2b fixed: the Chapter II crawl runs the AI at 32006 Hz and the fixed 2048 B
drain threshold starved SDL every ~96 ms; the threshold now scales with the rate (1023 -> 0 underruns). Owner to listen.

G3f (ITERATION 3c): owner saw a fish-eye look in the hangar ONLY while the camera pans between ships (FPS60 only, dd1, default
window), gone 1-2 s after it settles. Hypotheses:
- H-retail: retail does an FOV/zoom swing during the pan.
- H-fps60: FPS60 steps the pan's camera/FOV interpolation at the wrong rate or overshoots.
- H-proj: a per-frame projection value (guPerspective fovy/perspNorm) lags or is reused across the 60 Hz split.
- H-present: non-uniform presentation scaling during the pan (unlikely: it is transient).
Discriminator, one build, one run per arm (FPS60 on / off) plus the retail angrylion oracle: phase-gate on the hangar Left/Right
press, log per frame the hangar camera fovy / projection matrix x/y scale (find the guPerspective call in the hangar camera
path) and capture window frames through the whole pan. Fish-eye = projection x/y scale (or fovy) swinging during the pan.
If retail swings identically -> H-retail (offer an opt-in). If only FPS60 swings or overshoots -> fix the interpolation.
Hangar route: tools/g3_port_capture.sh (Start 6..21 s reaches the 512 hangar at ~24 s); add right/left presses at 26..40 s.
