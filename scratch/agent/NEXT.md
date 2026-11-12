# NEXT (s7224): RETINA=1 live windowed<->fullscreen toggle and window resize, mid-flight
HYPOTHESIS-ID: retina-live-resize
Context: RETINA=1 static cases are all closed (fullscreen auto s7203-s7222, 21:9 windowed s7223: 2720x1188 chain for a
1360x594 pt window, full view, hf 0.914 vs 0.735). Not yet scored: changing size WHILE playing (owner presses the fullscreen
toggle Cmd+Ctrl+F / F11, or drags the window edge). Hypotheses: H-ok (each change -> one new [retina] swapchain row at
2 x new point size, viewport refit, presents recover within ~2 s); H-stale (chain keeps the old size -> blurry or cropped/
letterboxed view after the change); H-churn (repeated recreate / resize storm, presents <20/s for seconds or gaps >250 ms).
Run: copy scratch/s7223/arm.zsh (LEVEL=4, ASPECT=21:9 windowed, PRESENT_RING) to scratch/s7224; in flight (~120 s) send the
fullscreen toggle via osascript keystroke to the game process, +15 s toggle back, +15 s resize the window via System Events
(set size of window 1 to {1000,430}); screencapture -x +5 s after each change. Arms r1 RETINA=1 / r0 RETINA=0, sequential.
Score: Z rows / [retina] swapchain rows / [g1f] resized rows per change, scratch/s7222/sum2.py (P/s, gaps), and
tools/s7223_window_score.py (needs window rect: take the LAST [g1f] window row, or score the fullscreen shot whole).
Positive control: the toggle must log [g1f] fullscreen change in BOTH arms (else the keystroke never landed = no result);
hf ctl down/up2 in r1 must fall to r0 level.
Outcomes: H-ok -> RETINA fully closed, owner sheet; H-stale -> fix the resize path to recreate at backing pixels;
H-churn -> debounce the resize handler.
