# NEXT: fold s6419 lvl5 + s6420 dd3 holds, then dd3 contact sheet + H-lod-coarse (G1c phase 2)
HYPOTHESIS-ID: g1c-dd-phase2
Read SOAK-RESULTS tail for s6419_dd2fix_lvl5 and s6420_dd3fix_lvl1/5/10 (crash/VI-stall/G1b frame time). If clean: fixed-camera dd1 vs dd3 contact sheet for the owner; test H-lod-coarse (scale LOD table 0x8009DE98..A0 by dd^2) for pop-in. If a crash: backtrace, root-cause (guest heap/pool at dd3).
