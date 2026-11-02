# NEXT: G3 SELECT GAME — left rebel emblem panel never drawn in the port
HYPOTHESIS-ID: g3-selgame-left-emblem

s6780: SELECT GAME backdrop is rand-driven in retail too (closed). Real defect: the LEFT emblem panel (512x448 box
70,325-135,390) is never drawn in the port (0 px, ~70 frames, 2 arms), retail draws it in both arms (scorer
tools/g3_frontend/emblem.py; right panel = control). Emblem objects: menuControllerInput 0x800B4944 jal 0x800B42D4
(result -> 0x800CF10C), 0x800B2A98 builds, 0x800B448C/0x800B3D08 attach; effect initCraftPreviewEffectWithRandom(0x800C4DF0,
a2=*0x800CF108, a3=*0x800CF10C).
Hypotheses:
- H-create: the left object is never created/attached in the port (pointer 0 or not linked into the draw list).
- H-draw: it is created and its display list submitted, but the port renders it invisible (zero alpha/scale, culled,
  bad texture load).
- H-anim: its animation (spin channel from 0x800C4DF0 / 0x800BC834) leaves it at an edge-on/zero-scale pose in the port.
Work unit: one run pair with tools/g3_frontend/selgame_rand.sh (seed pinned) plus oracle --exec-trace-also on 0x800B42D4,
0x800C4DF0, 0x800BC834 and an RDRAM dump at SELECT GAME (fb-dump or --watch-write 0x0CF108:0x0CF110); port
ROGUESQ_RAND_TRACE markers or a mem dump of 0x800CF108/0x800CF10C and the pointed objects' first 0x40 bytes. Compare
object words (pos/scale/alpha/flags) retail vs port.
Discriminating outcome: pointer/obj missing in port -> H-create; obj words equal but no pixels -> H-draw (check its DL);
scale/rotation words differ -> H-anim.
