# NEXT: G1d 21:9 level-select level-name clip
HYPOTHESIS-ID: g1d-menu-sweep

s6724 fixed the debrief pillars (content-gated present crop). Next open G1d item: at 21:9 the hangar level select draws
the level name clipped at the left edge ("NDEZVOUS ON BARKHESH"); 16:9 fits (scratch/s6724/gate219/w153+.png).
## Hypotheses
- H-anchor: our s6156 HUD anchor (or another left-anchor shift) moves the name text left by a per-aspect offset that
  overshoots at fbw=1024; at 16:9 the overshoot stays on screen.
- H-game-x: the game centres/left-aligns the name at a fixed 4:3 x, and the text is long; the 3D hangar is wide but the
  text x is in a 512 frame that we shift by (fbw-512)/2 - the clip is a negative x clipped by scissor.
- H-scissor: the text texrects start at a positive x but a scissor set for the text panel clips them.
## Discriminator
ONE run with ROGUESQ_LOG_G1D_RECT=1 (rect scan) at 21:9 on scratch/s6724/abort.sh; log texrect x for the level-name
strings in the level-select epoch (rs64_g1d_vi_epoch, [g1d-pillar] marks epochs), plus the active scissor. Negative /
sub-zero ulx -> H-game-x or H-anchor (then an anchor-off arm in the same session splits them); positive ulx clipped by
scissor ulx -> H-scissor. Then game-over at 21:9/16:9, then the 4:3 debrief right-edge column (fix43 w139).
