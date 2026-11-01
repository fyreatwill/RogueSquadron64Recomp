# NEXT: G1d game-over sliver — RT64 render-target side (H-rt64-target)
HYPOTHESIS-ID: g1d-menu-sweep

s6729: RT64 receives identical texrect commands and identical TMEM (same src/TMEM hashes) on undrawn and drawn swaps,
no RDRAM upload or fb-texture path touches the block (RAM_PATTERN 0 magenta there, NO_GPU_COPY still reproduces), and
RT64's writeback reads 0 at the block: its render target lacks the draw for ~7 swaps at 21:9.
Hypotheses:
- H-rt-resize: the A40000/B20000 render targets were created for an older/narrower fb (640/768 wide or fewer rows) and
  are resized/recreated at epoch start; draws in the grown region are lost or the region is re-initialised for a few
  frames (fits: only x>=640 region, shape varies).
- H-rt-pair: RT64 splits the 112 texrects into framebuffer pairs/draw calls and some calls bind a different target or a
  stale scissor/viewport (per-call record differs on undrawn swaps).
- H-rt-clear: a later GPU op in the same workload (fill/clear, depth-as-colour reinterpret) paints that region.
Instrument (one build, lib/rt64): per epoch-27 swap log (a) RenderTargetManager get/resize/create for A40000/B20000
(width, height, resolution, whether contents were copied), (b) per draw call of texrects with x>=640: target address,
scissor and viewport as RT64 converts them, textureIndex, fbPair index, (c) any fill/clear op on those targets.
Run scratch/s6729/gameover.sh <tag> 21:9 "ROGUESQ_FB_DUMP_EPOCH=27 ROGUESQ_FB_DUMP_VI=1 <new flags>" and score with
scratch/s6729/tiles.py. Discriminator: which record differs between undrawn swaps (tiles.py) and drawn swaps.
Fix in lib/rt64 (then export.sh + commit), regression: 4:3 game-over + 21:9 flight + title.
Then: owner contact sheet per aspect, then G3 render fidelity.
