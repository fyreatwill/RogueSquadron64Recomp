# NEXT: G1d pause dim overlay band (after the s6721 pause-text fix)
HYPOTHESIS-ID: g1d-pause-dim

s6721: at 16:9/21:9 the in-flight pause screen darkens only a centre band (~x 222..802 of 1024 at 21:9); the sides stay
bright. 4:3 darkens the whole screen. Same in the anchor-off arm, so not the s6156 HUD anchor.
initOrUpdatePauseScreenDim (0x800C1D3C) only calls audio/menu-state helpers: the overlay is drawn elsewhere.

## Hypotheses
- H-fill: a G_FILLRECT / blended rect with a hard-coded 4:3 extent (320/640 * scale, or the camera viewport of a
  640-wide state) -> widen the constant at its builder (like s6694 scissor).
- H-tri: a screen-space quad drawn through a 3D viewport/projection that our wide path scales only partly (band
  580/1024 ~= 0.57, not 512/1024 or 640/1024 -> suspect a viewport x-scale mismatch).
- H-scissor: the overlay is full-width but clipped by a 4:3 scissor set by the pause renderer.
## Discriminator (one build, one 21:9 pause run, scratch/s6721/pause.sh)
Extend rs64_g1d_rect_scan (dpc_bridge, read-only) to also record, only while rs64_g1d_pause_live(): fill rects (op 0x36)
with x extents, SET_SCISSOR values, and tris with SET_OTHER_MODE blend (op 0x2F) + prim/env colour alpha < 255, per swap.
Paused swaps vs flight swaps: a new 0x36 or alpha tri whose x range is 222..802 names the primitive; its x extent vs
scissor selects H-fill/H-tri vs H-scissor. Then find its builder (grep the DL pointer back via the ucode-side G_FILLRECT
or the gfx DL owner) and widen it. Verify 21:9 + 16:9 + 4:3 control, then check debrief/game-over screens.
