# NEXT: same-pose retail-settings check of ROGUESQ_ASPECT 16:9 in flight, lvl1
HYPOTHESIS-ID: g3-aspect-samepose

Why: selfbranch-mission-null closed s6878 (H-dead on missions 1, 2). s6872-s6877 compared dd and FPS60 against dd1 with same-pose arms; check tools/g3_optin_pose_arms.sh first, and if ASPECT arms were already scored, take the next ladder rung instead. Aspect work closed on menus and owner sheets, not on a same-pose near-field number.
Hypotheses: H-same (centre 4:3 crop of 16:9 matches the 4:3 frame after the x scale, only the sides are new) / H-diff (near geometry, culling or HUD differs inside the crop, naming a real wide-mode defect) / H-scale (crop differs only by resampling, floor set by a dd1-vs-dd1 repeat).
Measure, one build, all arms in one iteration: lvl1 dt pinned, POSE_FREEZE, arms 4:3, 4:3 repeat (floor), 16:9. Score centre crop MAD per k. Positive control: adjacent-tick MAD in the same run must exceed the floor, or a null says nothing.
Outcomes: within floor -> H-same, record it. Above floor with resampling-like spread -> H-scale. Localised difference -> H-diff, name the draw and fix it.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these. lvl10 cloud clock only on an owner report.
