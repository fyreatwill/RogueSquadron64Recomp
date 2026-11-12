# NEXT (s7226): ROGUESQ_ASPECT=auto when the window opens on a NON-main display
HYPOTHESIS-ID: aspect-auto-display-choice
Context: s7225 closed live resize (H-bars). auto reads SDL_GetDesktopDisplayMode(0) (main.cpp ~12453) = the MAIN display. The owner
plays on a 21:9 ultrawide and a 65" 16:9 TV; if either is a secondary display (laptop main), auto may take the laptop's 1.54 aspect.
Hypotheses: H-main (auto uses display 0 whatever display the window lands on -> wrong width on the secondary: bars in fullscreen);
H-window (SDL's display 0 / window placement both follow the main display, so the window also opens on main: then auto is
self-consistent and the question is only "how does the owner put the game on the TV" -> moving it later = s7225 bars);
H-ok (the window opens on the display with the cursor/last position and auto already matches it).
Run: build/virtual_display 2560 1080 400 (21:9 secondary; tools/virtual_display.m, s7202) in the background; boot ASPECT=auto
FULLSCREEN=1 RETINA=0 LEVEL=4 owner recipe, first with no placement lever (where does the window open? [g1f] window ... at X,Y vs the
[vd] bounds), then (if needed) add a placement lever (SDL_WINDOWPOS_CENTERED_DISPLAY(n) via a new ROGUESQ_WIN_DISPLAY=n, default
unset = old) so it opens on the virtual display. Score with tools/s7225_resize_aspect_score.py-style lit bbox of the virtual display
area (screencapture -D <n>). Control: same boot with ASPECT=21:9 fixed on the virtual display (must FILL).
Outcomes: H-main -> auto should read SDL_GetDisplayForWindow / the target display (fix, default on, =0 old); H-window -> add the
ROGUESQ_WIN_DISPLAY lever + document the owner command; H-ok -> close.
