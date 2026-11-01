# NEXT: G1f close-out — 21:9 and 4:3 window captures (owner ladder item G1f "take NOW"; 16:9 + fullscreen done s6688)
HYPOTHESIS-ID: g1f-window-fit

G1e is closed at the dd4 ceiling (s6716: bridge = essential work, pure-trace tail 2.2% < 3% bar; interpreter 76%).

## Hypotheses
- H-ok: since the s6690/s6694/s6695 fixes, ROGUESQ_ASPECT=21:9 opens a ~21:9 window sized to the desktop and lvl1 flight
  fills it edge to edge with the HUD at the real edges; 4:3 (ROGUESQ_ASPECT unset / 4:3) opens a 4:3 window.
- H-letterbox: the 21:9 window opens but the game image is pillar/letterboxed inside it (window size vs game width
  1024 mismatch, high-DPI drawable not following).
- H-route: 21:9 still fails on the forced route (crash/tear) — fold as a G1d datum, root-cause.
## Discriminator (one run per arm, sequential, same recipe as s6688)
Grep PORTING-STATE "## Session 6688" for the exact window-capture recipe (screencapture -l <windowid> + fbd). Run arms
21:9 (ROGUESQ_OSMEM_MB=12 as in OWNER-OPT-INS) and 4:3, lvl1 forced route, ~130 s. Check CGSSessionScreenIsLocked first.
Record window size, drawable size, game width, fraction of non-black columns at the left/right edges of the window shot.
Outcomes: H-ok -> mark G1f done in CURRENT-TRUTH + OWNER-OPT-INS, send sheet path, take G3. H-letterbox -> fix in
main.cpp window sizing. H-route -> root-cause.
