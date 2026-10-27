# NEXT: G1e frame period from a game-side counter
HYPOTHESIS-ID: g1e-framerate
Pixel hashing fails (s6451: dumps alternate per VI, lag1 diff const 7.6). Find the game's per-frame counter/tick (grep CURRENT-TRUTH / PORTING-STATE for the frame counter or osViSetEvent retrace-divisor global; the render-loop func that waits on retrace) and log it per VI in the G1b instrument (one build). Count increments per 60 VIs: retail vs FPS60. H-30: ~30; H-20: ~20; H-60: ~60. Control: FPS60 arm must differ from retail. Then lever (1) of G1e.
