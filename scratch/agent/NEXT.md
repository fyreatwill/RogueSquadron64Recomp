# NEXT: verify the s6852 region Z gate at 16:9 and name the post-world z-off object
HYPOTHESIS-ID: g1d-region-shift-scope

State (s6852): rs64_region_scan now shifts only z_cmp-off prims after the frame's first z_cmp-on prim
(ROGUESQ_G1D_REGION_ZGATE, default on) with a 32 px left pad for tris (ROGUESQ_G1D_REGION_TRI_PAD). lvl17 21:9: disc fully
shifted, world 61724 kept / 12 shifted, the left-behind grey wedge gone. First fold SOAK-RESULTS for s6852_zgate_lvl5/lvl9.

Unit: one run of scratch/s6852/abd.sh adapted to ROGUESQ_ASPECT=16:9 (MISSION_WIDTH per main.cpp auto width), lvl1,
SHIFT=<auto value printed by "[g1d] hud anchor=... shift=" in run.log>, KEEPBIN=1 with SHIFT=0 for the offline arm.
Hypotheses:
- H-ok: at 16:9 the disc is wholly shifted, no wedge left behind, world kept (pad scales with box width).
- H-pad: the 16:9 box is narrower, the scaled pad misses (wedge left) or over-reaches (HUD text/bracket moved).
- H-post: the residual z-off post-world object (lvl17 textures 79F7C0..7A5120, 171 tris/frame) is a world effect visible
  in the box at 16:9 too -> needs a stronger HUD boundary (e.g. texture-run adjacency to the ring).
Discriminator: tools/g1d_regiontex.py on the SHIFT=0 16:9 bin with --box from the run's "[g1d] ... disc region=" and
--ring <the 16:9 ring texture: in-box/anchored texrect 112x32>, plus [region-zgate] counters and a 3-frame crop.
Budget: 1 iteration; then return to G1d close-out (owner judgement) / next ladder rung.
