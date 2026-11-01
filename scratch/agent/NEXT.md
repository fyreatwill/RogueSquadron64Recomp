# NEXT: G1d game-over entry — why the backdrop's top-right tile does not land for ~7 swaps at 21:9
HYPOTHESIS-ID: g1d-menu-sweep

s6727: at 21:9, epoch 27 (game-over backdrop) swaps 1-7 leave image x 640..768, rows 0..~70 undrawn (stale buffer shows;
window = black block + white top row). 4:3 draws everything from swap 1. 112 texrects/swap in both arms.
Hypotheses:
- H-tex: the tile's texture (SETTIMG address) is still being streamed/decoded at 21:9 (memory moved by the wide fbs),
  so the rect draws transparent/zero until it arrives.
- H-g1d: a G1d rewrite (rs64_g1d_title_clear / pause_dim / anchor shift) edits or drops that rect on early swaps.
- H-clip: the rect's xh = 768 (edge of centre) with a scissor/clip edge case at the epoch's first swaps.
Discriminator, one build: extend rs64_g1d_rect_scan (ROGUESQ_LOG_G1D_RECT=2) to log, for the first 12 swaps of a
chosen epoch (ROGUESQ_G1D_RECT_EPOCH=27), EVERY texrect: x0..x1, y0..y1, the last SETTIMG addr/fmt/width, SETTILE,
other-mode and combine. Run scratch/s6727/gameover.sh at 21:9 and 4:3 (same FB_DUMP_EPOCH=27 dumps; fbd under
scratch/agent/m6/<tag>/fbd). Compare the top-right tile's rect: present & identical timg in both -> look at the texture
bytes (H-tex: dump RDRAM at that timg on swap 1 vs 8); absent/modified at 21:9 -> H-g1d; y/x clipped -> H-clip.
Then: owner contact sheet per aspect (s6726 NEXT item 2), then G3 render fidelity.
