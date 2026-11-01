# NEXT: G1d debrief / game-over screens at wide aspect (after the s6722 pause dim fix)
HYPOTHESIS-ID: g1d-menu-sweep

Pause menu is clean at 21:9/16:9 (s6721 text, s6722 dim). Remaining G1d screens: the mission debrief (reached via
pause -> ABORT LEVEL, or mission end) and game over.
## Hypotheses
- H-clean: debrief/game-over use the title-style VI mode or full-width rects already handled (s6720) -> no change.
- H-4:3-geometry: a 4:3-sized panel/quad (like the s6722 dim) or a 640-wide fill rect leaves bright/stale pillars.
- H-anchor: our s6156 HUD anchor splits debrief text (like s6721) -> extend the pause-byte gate to the debrief state.
## Discriminator (one build, ROGUESQ_LOG_G1D_RECT=1 already logs fills + new tri signatures while paused)
Copy scratch/s6721/pause.sh; after pausing at t=112, press down x1 (ABORT LEVEL), A, confirm with A; capture windows
to t=170. Arms in one session: 21:9, 16:9, 4:3. Look at the captures: pillars/bands/split text select the hypothesis;
the rect log names the primitive (note the pause byte may clear on abort, so the GRP filter may need a debrief gate).
