# NEXT: name the lvl17 post-world z_cmp-off object the region gate still shifts (21:9)
HYPOTHESIS-ID: g1d-region-shift-scope

State (s6853): ROGUESQ_G1D_REGION_ZGATE verified at 21:9 (lvl17/5/9) and 16:9 (lvl1): only the radar disc is moved.
One residual (s6852, lvl17 only): a z_cmp-off object drawn after the world pass, textures 79F7C0..7A5120, ~171 tris/frame
for ~600 swaps, still selected and shifted +256. lvl1 at 16:9 has no such object (all non-disc textures 0 shifted).

Unit: one lvl17 21:9 run, scratch/s6852/abd.sh with KEEPBIN=1 SHIFT=0 FBDV=500 (frames for the swaps where those
textures appear; find them with the [region-zgate] windows of s6852 ab_l17_z1_sh256/zgate.txt), then
tools/g1d_regiontex.py --ring 792DA0 on the bin + crops of the box region.
Hypotheses:
- H-hud: the object is HUD (targeting/lock overlay, radar blip layer) -> shifting it is correct; close.
- H-fx: a world effect (explosion/flash/smoke billboard drawn z-off after the world) that crossed the box -> moving it
  is wrong; key the gate on texture adjacency to the disc (same cmd run as T7965C0) instead.
Discriminator: does the same texture draw OUTSIDE the box at scattered positions in the same VIs (regiontex out/outVIs,
med_dist), and does the crop show it shifted away from its world anchor?
Budget: 1 iteration. Then G1d is fully awaiting owner judgement; next ladder rung G3 (in-flight frame diffs vs retail).
