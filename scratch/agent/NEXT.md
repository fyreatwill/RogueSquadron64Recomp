# NEXT: 21:9 sky-side corner holes past the cloud band (CURRENT-TRUTH item 29a), after the s7133 horizon-x fix
HYPOTHESIS-ID: g3-owner-recipe-219
State (s7133): the horizon clear builder 0x8005B51C now places its split right under ASPECT (ROGUESQ_HORIZON_XFIX default on).
The remaining 21:9 burst (F1 swaps 7524-7541, up to 30k of 458k px) is bottom-left at about 150 deg roll. Those pixels are on the SKY
side of the horizon, beyond the edge of the cloud-band triangles (F1 7541: no tri and no rect at (200,420); the clouds at (60,200) are
tri #75). The ground-side clear rects never cover the sky side. Plus 14 no-clear hole swaps per 21:9 run (7564-7591).
Hypotheses:
- H-skyband: the cloud band has a fixed angular height. A 21:9 corner in a steep roll looks above its top, which a 4:3 corner cannot reach.
- H-skycull: the band's segments are selected or culled with a 4:3 frustum, so the extra width loses segments, not elevation.
- H-retail: 4:3 at the same pose shows the same gap. s7133 R1 had a different pose (camera inside the wall), so this is undecided.
Discriminator, offline first (F1.cap is kept, 12.6 GB, scratch/s7133/F1.cap + F1.idx + F1.rects):
in F1 7530/7541, list the cloud-band tris (s7132_tricover census; find the band by texture/combiner) and their screen extent.
If the band's edge is a smooth arc parallel to the horizon at a fixed distance, that is H-skyband. If it ends in vertical or
segment-shaped cuts near the 4:3 x-extent (|x - 512| < 512 / k), that is H-skycull. Then read the band's submit code (grep the
writer of the band's DL or its vertex source) for the culling or extent constant.
Fix candidates: H-skycull: widen the band's x-cull by ASPECT_SCALE (like s6144 fpx). H-skyband: under ASPECT > 1, also clear the
sky-side remainder (one extra rect from the line to the far edge) so holes get the fill colour instead of stale pixels. Opt-in first,
then same recipe tools/s7133_arm.zsh 6 F2 "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000",
replay with scratch/s7124/al16/frame_replay16 in 6 parallel chunks (zsh: $(cat chunk), not an unquoted $S), score by
clear / no-clear with the s7133 inline split. Pass = 0 clear swaps over 3000 px at 21:9 and 16:9 still 0.
Side item (b): what the static single-range stretch at 16:9 S1 7500-7566 is (no HUD, no clear, 67 identical streams).
Owner save rule applies. CURRENT-TRUTH ~59.9 KB: keep edits net-zero (a maintenance pass is due soon).
