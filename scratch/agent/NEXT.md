# NEXT (s7221): RETINA=1 fullscreen display hot-plug (1x virtual display removed while fullscreen -> game lands on the 2x built-in)
HYPOTHESIS-ID: retina-hotplug
Context: RETINA=1 is CLOSED for flight (s7218/s7219) and front end (s7220). s7202 fixed fullscreen display removal (leave fullscreen
+0.3 s, re-enter +1.5 s, plume needsResize on drawable mismatch) but ran only at RETINA=0 (RETINA arrived s7203); s7203 checked a
WINDOWED 1x->2x hot-plug at RETINA=1 only. Untested: the s7202 leave/re-enter path when contentsScale changes 1 -> 2 at RETINA=1.
First fold SOAK-RESULTS for s7220_bootloop_retina (12 owner-env boots, auto + RETINA=1; exit 0 = 0 FROZEN with hunter control PASS).
Hypotheses: H-ok (after the re-enter the swap chain re-creates/resizes to 3024x1898, on-screen presents ~60/s within ~2 s, picture
full-screen); H-half (needsResize/getScaleFactor keeps the 1x scale: 1512x949 or 1920x1080 chain on a 2x panel, i.e. RETINA lost
after the move, or a quarter-size image like the s7202 windowed bug); H-dead (Space hidden / 0 on-screen presents, s7202 class back
at RETINA=1).
Run: copy scratch/s7202/arms2.zsh (build/virtual_display 1920 1080 <hold>, ROGUESQ_WINDOW_POS on the virtual display, destroy ~26 s);
arms r1 = FULLSCREEN=1 RETINA=1 ASPECT=auto, r0 = same with RETINA=0 (s7202 control), plus a reverse arm (start on built-in, add the
1x display, move is NOT automatic -> skip unless trivial). Witnesses: [retina] swapchain create / Z resize rows, [g1f-win] rows
(drawableSize, contentsScale, active_space, occlusion), PRESENT_RING P at>0 per second after removal, screencapture -x at +5 s.
Positive control: CGGetActiveDisplayList 1->2->1 and SDL_DISPLAYEVENT 3 in the log; r0 must reproduce s7202's fixed result.
Outcomes: H-ok -> hot-plug closed at RETINA=1; H-half -> fix the scale path (plume_apple.mm getScaleFactor / needsResize) and export
submodule patches; H-dead -> extend rs64_display_hotplug_tick for the scale change.
