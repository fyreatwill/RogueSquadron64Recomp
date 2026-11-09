# NEXT: G1c — height-occlusion gate for the off-map cull (s7032: fixed-R cull is visible once the eye climbs above the plateau)
HYPOTHESIS-ID: g1c-offmap-cells
Context (s7032, frozen poses, L1 21:9 dd6 WIDEWIN cap 10240 MELT FPS60): A/A 0.01, FOGCULL=0.3 control 0.5-4.0. OFFMAPCULL=2: 0.13-0.51 below the plateau top
(a wall-top sliver), 10.6/39.0 at poses 5/6 where the craft (y -5.7/-6.9, eye cell x 52/60 of 64, still on the map) looks out over the flat off-map plateau.
R=8: 6.2/15.5. Sheet docs/owner_sheet_s7032_offmap_pose.jpg. The eye-on-map gate (apply_s7032_eyegate.py) never fired. The cull saves rsp 9.75 ms on L1 (s7031).
G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14); check first.
Hypotheses:
 H-height: the off-map plateau = edge-cell heights clamped outward; its top is invisible while eye_y is below the clamped edge height (the wall face occludes it).
   A per-cell gate (cull off-map ring > R only if eye height < clamped edge height - margin) is image-neutral at all 7 poses AND keeps most of the cost win
   (most of a flight is below the plateau top).
 H-fullview: the plateau top is visible from on-map terrain below its height too (e.g. the plateau slopes or the edge cells vary), so the gate still cuts
   something at poses 0-4 -> no cheap image-neutral cull; report the cost/look trade to the owner instead.
 H-costgone: the gate keeps the image but disarms the cull on most frames (the eye is often above the edge heights), so the cost win collapses.
Work, ONE build:
 1. Find the units: the eye y = rf(a0+4) (a0 = 0x80130C10 in rs64_s7030_begin; world, y DOWN-negative? pos y -2.5 at low flight, -6.9 after climbing, so more
    negative = higher). Cell height: what getGridCellValueAt returns for the clamped edge cell (funcs_9.c, clamp branch, s7024); check its height field
    vs world y on one on-map cell under the craft (log both for the eye's own cell: eye y minus ground ~ altitude).
 2. In rs64_s7032_cell: for an off-map cell, clamp (x,z) to the edge cell, read its height (cache per edge cell per frame), cull only if R test passes AND the
    eye is below that height by > margin (ROGUESQ_DD_OFFMAPCULL_H=<margin>; default gate on; =off restores fixed R). Count gated-off cells per phase.
 3. Arms (scratch/s7032/run_L1g.zsh as template, separate same-pose runs): offA, r2h (R=2 + height gate), r2 (fixed, positive control: void at poses 5/6),
    k03 (control). Score with tools/s7032_pose_cull_score.py; then one OWNER_TIMING tog3 run R=-1,2h,2 for cost (scratch/s7031/run_A.zsh).
Outcome map: r2h at the A/A floor at all poses (incl. 5/6), r2 still voids, and r2h keeps >= half the rsp win -> H-height: offer it in OWNER-OPT-INS,
 then repeat on L4. r2h still cuts at poses 0-4 -> H-fullview. Image clean but rsp win < 2 ms -> H-costgone (close the lever, report to the owner).
