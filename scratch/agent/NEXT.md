# NEXT: fold s6419 dd2+fix holds, then dd3 holds + owner sheet (G1c phase 2)
HYPOTHESIS-ID: g1c-dd-phase2
Read SOAK-RESULTS tail for s6419_dd2fix_lvl1/5/10 (crash/VI-stall/frame-time vs G1b baseline). If clean: queue dd3 300 s holds on lvl1/5/10 with the fix; check pop-in/LOD coarseness (H-lod-coarse: scale LOD table 0x8009DE98..A0 by dd^2) with a dd3 framebuffer sheet for the owner. If a crash: backtrace, root-cause (guest heap / pool at dd3).
