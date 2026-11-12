# NEXT (s7225): ROGUESQ_ASPECT=auto after a live window resize (G1f goal 3)
HYPOTHESIS-ID: aspect-auto-live-resize
Context: s7224 closed RETINA for live changes. ASPECT=auto is resolved ONCE at boot (main.cpp ~12450: SDL_GetDesktopDisplayMode ->
clamp -> setenv ROGUESQ_ASPECT=r:1 -> rs64_g1f_fit_window), so the game FB width and the RT64 aspect are fixed from then on.
G1f goal 3 asked for auto to follow "a resize or moving between displays if feasible"; never measured.
Hypotheses: H-follow (something already re-derives width on resize: view fills the new window, no bars); H-bars (game width stays,
RT64 letter/pillarboxes inside the new window: correct geometry, wasted area); H-stretch (picture stretched to the new window:
wrong geometry - a defect).
Run: copy scratch/s7224/arm.zsh to scratch/s7225; ASPECT=auto windowed (no FULLSCREEN), RETINA=0, one arm; levers
ROGUESQ_WIN_TEST_RESIZE_S=120:1000:430,140:900:675,160:1200:675 (2.33, 4:3, 16:9). Control arm in the same iteration: ASPECT=16:9 fixed
with the same resizes (expected H-bars). Score with tools/s7223_window_score.py-style window crop: lit bbox per shot (bars show as
bbox < 1 in one axis) and circle/HUD aspect (radar disc width/height in px; stretch shows as != 1).
Outcomes: H-follow -> close G1f goal 3; H-bars -> decide if a live FB-width change is feasible (game reads width at boot? check
FB_WIDTH users) or document bars as the design; H-stretch -> fix the RT64 aspect rewrite on resize.
