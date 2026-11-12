# NEXT (s7215): long-route present-shape census at 21:9, fix on, then close mode-switch-pillarbox
HYPOTHESIS-ID: mode-switch-pillarbox
Context: s7213 fixed the 21:9 mode-switch letterbox (ROGUESQ_PRESENT_SHAPEFIX, lib/rt64 present_queue). s7213 checked 4:3/16:9/21:9 windowed
and s7214 checked ASPECT=auto and ASPECT=expand fullscreen, all on the SHORT L17 route (5 s + 45 s capture). Both: H-ok (only real
mode-switch mismatches, all viewports full). The long s7210 route (boot -> menus -> L17 -> MISSION FAILED -> Elite Rogues x2) has more mode
switches (fail screen, ER double-stride stills) that were never covered.
Hypotheses: H-ok (every [s7213-shape] line on the long route sits at a VI mode switch, every non-upload viewport full, no box frame);
H-new (a mode switch on the fail/ER path shows a lit box the fix misses, e.g. a scratch/RDRAM-upload target, since those are excluded
from the fix, or a target whose rs ratio matches but whose VI height changed).
Discriminator, 1 run (+1 fix=0 control only if a non-full viewport shows up):
  env CW=1680 CH=720 zsh tools/s7141_arm.zsh 17 L21 "ROGUESQ_G5B_FRAME_EVERY=100000 ROGUESQ_VI_SHAPE_LOG=1 ROGUESQ_ASPECT=21:9" 150 80
  (delay/duration as scratch/s7210/fc.zsh so the capture covers MISSION FAILED -> ER). Then: grep [s7213-shape] and list non-full
  [g1d-vishape-vp]; python3 tools/s7213_box_scan.py scratch/s7141/L21.raw scan; tools/s7214_gain_sheet.py on any narrow frame not
  explained by a fade. Raws are ~11 GB at 1512x949, so delete after scoring.
H-ok -> close the thread in CURRENT-TRUTH (move it to Closed work), take the next backlog item. H-new -> fix it in the same iteration.
