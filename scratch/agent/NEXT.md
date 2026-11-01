# NEXT: G1d debrief pillars — blank them inside RT64 (host-only)
HYPOTHESIS-ID: g1d-menu-sweep

s6723: the debrief (mode 0x80128DA0, rs64_g1d_title_vi == 2 while live) draws only x 256..768 of its 1024-wide colour
image; the pillars hold the game's own live debrief heap (retail too, hidden by retail's full-width draw). RDRAM zeroing
and a VI centre window both FAILED (RT64 target + native-swap writeback keep the residue; RT64 ignores the VI offset).
Never write the pillars in guest RDRAM (live heap).
## Hypotheses
- H-target-clear: clearing the RT64 colour target outside x 256..768 (GPU side) each debrief frame, without writeback
  to RDRAM, hides the residue. Look in lib/rt64 (rt64_framebuffer_manager / rt64_present_queue) for a per-target clear
  or a present-time crop; gate on an exported flag set from rs64_g1d_title_vi == 2.
- H-present-crop: simpler: at present, when the flag is set, sample only the centre 512 columns (scissor/viewport of the
  final blit) and leave black bars. Owner sees the 4:3 debrief pillarboxed, like OPTIONS.
- H-writeback: if RT64 re-uploads RDRAM into the target on every frame (residue changes frame to frame), a GPU clear is
  undone; then the crop at present is the only host-only lever.
## Discriminator
One build with both levers behind env (ROGUESQ_G1D_DEBRIEF=clear|crop|0). Run scratch/s6723/abort.sh at 21:9 for each
arm in one session; measure pillar luma (x .02-.15, .85-.98) over debrief frames w133-w155: 0 = fixed. 0 arm = control
(must show residue). Any lib/rt64 edit -> ./submodule-patches/export.sh + commit.
Then: the 21:9 level-select name clip (left edge) and a game-over screen.
