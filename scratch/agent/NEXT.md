# NEXT (s7223): RETINA=1 + ASPECT=21:9 WINDOWED on the 2x built-in
HYPOTHESIS-ID: retina-wide-window
Context: RETINA=1 is closed for fullscreen auto (s7203-s7222: flight, front end, endurance, hot-plug). Not yet scored: a
non-fullscreen 21:9 window at RETINA=1 (owner plays 21:9; the window path sizes via rs64_g1f_fit_window, swap chain at
backing pixels). Hypotheses: H-ok (backing chain = 2x window size, full 21:9 viewport, same route as RETINA=0, hf higher);
H-letter (viewport/scissor computed in points -> a quarter-size or letterboxed 3D view in the 2x chain); H-cost (gaps >250 ms
or presents <30/s at 2x on 21:9).
Run: arms r1 RETINA=1 / r0 RETINA=0, both `ROGUESQ_ASPECT=21:9` no FULLSCREEN, LEVEL=4 owner flight recipe (see
tools/s7125_arm.zsh / scratch/s7220 for the route), PRESENT_RING, screencapture at fixed phase points. Score with
scratch/s7222/sum2.py (P/s, gaps, Z rows), tools/s7220_shot_pair.py for in-phase shot pairs, hf residual as in s7221 scores.txt.
Positive control: [retina] swapchain create row = 2x window size in r1, 1x in r0; hf ctl (r1 down/up 2x ~= r0 level).
Outcomes: H-ok -> RETINA windowed closed, owner sheet; H-letter -> fix viewport scale on the windowed path; H-cost -> G1b
instrument on the 2x chain.
