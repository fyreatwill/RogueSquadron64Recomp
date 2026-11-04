# NEXT: 21:9 same-pose scoring: pin sx = sy in g3_aspect_crop, then 21:9 + dd4 arm
HYPOTHESIS-ID: g1d-wide-219-samepose

Why: s6881 gave 16:9 dd4 same-pose frames. 21:9 is still single-source (s6880: free fit gave sx 1.22, sy 1.48, scored the frames backwards) and 21:9 + dd has never been frozen.
Hypotheses: H-fit (pinning sx = sy gives a 21:9 score with control separation, and n219 beats o219 as the sheets show) / H-crop (still no separation: the 21:9 picture is cropped or scaled differently from 16:9, so the fit model is wrong) / H-depth (scores fine, and 21:9 still loses terrain against 4:3).
Measure: add --pin to tools/g3_aspect_crop.py (one scale, from the known window geometry). Offline first on scratch/s6879/a n219, o219 vs t43, ctl shift. Then one run: env PIN=1 HOLD_S=130 TAGP=s6882 XMEM=800FA730:0:80137DBC:1 zsh tools/g3_optin_pose_arms.sh scratch/s6882/a h219d4=ROGUESQ_ASPECT=21:9+ROGUESQ_DRAW_DISTANCE=4+ROGUESQ_DD_GRIDLOG=1, base d43 from scratch/s6881/a.
Control: o219 must score worse than n219 at k2 and ctl_mad must sit well above the base score, or the number says nothing.
Outcomes: H-fit -> record 21:9 numbers, drop the "not valid at 21:9" note. H-crop -> measure the picture box per aspect and fix the model. H-depth -> name what still limits the footprint at 21:9.
Also: hd4 took ~2500 VI per freeze step vs ~1750 for d43 (s6881). Read [g1b] tasks/s in that log before calling 16:9 dd4 full speed; recipe logging may explain it.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree; the s6881 regen tree (with s6879, s6880) was compared by object only, never linked or run.
Owner judges: docs/owner_sheet_s6881_wide_dd4.png, docs/owner_sheet_s6880_219_depth.png, docs/owner_sheet_s6879_wide_depth.png, docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous, 21:9 lvl5/lvl10 at 300 s. Owner can lift the park for these. lvl10 cloud clock only on an owner report.
