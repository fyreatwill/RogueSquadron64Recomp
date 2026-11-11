# NEXT: sky top-fade bins — drawn in retail (dd1 4:3) but lost at dd4, or never drawn? (follow-up to s7136, item 29)
HYPOTHESIS-ID: g3-sky-topfade
State: s7136 closed the wide sky-corner hole with ROGUESQ_HORIZON_SKYFILL (full-viewport clear under ASPECT). The corner now
shows flat haze beige as a stair against the clouds. loadSkyHorizonHob (0x8005AB34) builds 8 azimuth sectors plus 8 'top' bins
whose polys fade (vertex colour A89880 alpha 0..FF) into that beige. tools/s7136_topfade.py counted 0 top-fade-colour tris in
15 sampled swaps of L6 dd4 21:9 flight (scratch/s7136/Y1.cap); detector positive control at shade (26,26,26) = 1629.
Sky bin objects are at S+0x1C+0x5C*k (S = 0x8056E010 on L6, tools/s7136_skybins.py finds S by signature). Objects 4-6 and 12-14
hold pointers in 0x80C1xxxx (the dd>1 spill arena, s6858); the others hold pointers in 0x8087xxxx.
Hypotheses:
- H-topdd: dd>1 loses the top bins (spill-arena placement, or the dd far/LOD changes). Predicts top-fade tris > 0 at dd1.
- H-topretail: retail never draws them in L6 flight (a cull, or the 0x30 per-object field / LOD keeps them off). Predicts 0 at dd1 too.
- H-topcolour: they ARE drawn, but shade is modulated (fog / prim), so the detector misses them. Check: at dd1, list the textured
  tris drawn with the sky textures 0x78B600-0x799620 (tools/s7134_band.py) and compare the count with 8 sectors x polys.
Discriminator, ONE run: tools/s7136_arm.zsh 6 D1 "ROGUESQ_ASPECT=4:3 ROGUESQ_DRAW_DISTANCE=1 ROGUESQ_G5B_FRAME_EVERY=20" (note: the arm
script hardcodes DRAW_DISTANCE=4 and ASPECT=16:9 in XENV_EXTRA; later env wins only if the game reads the last occurrence —
check, otherwise copy the arm with dd1/4:3). Then python3 tools/s7136_topfade.py scratch/s7136/D1.cap <first> <last> 20, plus
s7134_band.py on 3 swaps: band tri count and sky-texture set vs Y1 (dd4).
Outcomes: dd1 > 0 and dd4 0 -> H-topdd: find what dd changes for those objects (S+0x1C+0x5C*k fields at dd1 vs dd4, same RAM
offsets), fix, and rerun Y1 to get the authored fade in the corner. Both 0 + same band tri count -> H-topretail: close the thread;
the beige corner stays (owner look). Detector 0 but extra sky-texture tris at dd1 -> H-topcolour: fix the detector first.
Owner save rule applies. CURRENT-TRUTH is 58.7 KB: keep edits net-zero.
