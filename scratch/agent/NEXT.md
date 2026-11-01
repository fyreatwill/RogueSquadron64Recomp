# NEXT: G1d remaining menu screens at wide aspect (game-over / continue, then 4:3 debrief right-edge column)
HYPOTHESIS-ID: g1d-menu-sweep

s6725 fixed the 21:9 level-select name clip (s6156 HUD anchor now flight-only via rs64_g1d_hud_flight). Remaining G1d
menu items from s6724: (1) the game-over / out-of-lives screen at 21:9 and 16:9 (never captured at wide aspect);
(2) the 4:3 debrief thin noisy right-edge column (single-source, scratch/s6724/fix43 w139).
## Step 1: get the screen
Find the route: grep PORTING-STATE for "game over"/"GAME OVER"/lives; the HUD lives counter is the "6" icon. If no
forced lever exists, the abort route (scratch/s6725/abort.sh) reaches debrief + level select only; consider a lives
poke (find the lives byte via the HUD lives element on vp 0x800CDC80) - a poke is a harness lever, fine for G1d.
## Hypotheses (once captured)
- H-anchor-residue: another anchored list or the s6159 region shift (ROGUESQ_SHIFT_REGION, radar-gated since s6695)
  moves game-over text; split with ROGUESQ_HUD_ANCHOR_AUTO=0 in the same session.
- H-pillar: the screen draws only the centre 512 columns of a wide image and the s6724 content-gated crop does not fire
  (draws < 64 or a stray outside draw); read [g1d-pillar] lines.
- H-game: the game draws it correctly (centred, [g1d-rect] x 256..768) and nothing is wrong.
## 4:3 right-edge column
ROGUESQ_LOG_G1D_RECT=1 at 4:3 on the debrief: does any draw touch x>=508 of the 512 image (game) or is the column
outside every draw (stale bytes, VI hStart/width edge)? Retail mupen64plus oracle frame would settle retail-or-not.
