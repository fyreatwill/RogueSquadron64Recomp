# NEXT: 21:9 check of the folded dd6 bundle (KEDGE=0.8,12 default since s7047) on L12, plus L1 21:9 cost
HYPOTHESIS-ID: dd6-bundle-l12-horizon
Context (s7047): src/main/main.cpp s7037 block now sets ROGUESQ_DD_OFFMAPCULL_KEDGE=0.8,12 (overwrite=0) for dd>=6+WIDEWIN. Qualified at 16:9
only (L12 poses 0.07 vs 0.81 with KEDGE=0; holds L12 59.6-59.9, L13 60.0). The bundle was first qualified at 21:9 (s7034-s7037: L1/L4/L5),
and the owner's ultrawide is 21:9: the wider frustum loads more off-map side cells, so k2cells and cost may be higher there.
Hypotheses: H-same (21:9 L12 poses fold <=0.1 and L1/L12 holds >=58.5 fps with KEDGE) / H-wide-visible (21:9 shows the cut at a side
edge the 12-cell gate misses: fold >0.1 vs dd6off) / H-wide-cost (invisible but L12 21:9 <58.5 with KEDGE while K0.6 >=59).
Unit (no build):
1. Poses L12 21:9: copy scratch/s7047/run.zsh with ROGUESQ_ASPECT=21:9 in C, arms dd6off / fold / foldk0 (foldk0 = positive control,
   must show the cut). Score tools/s7032_pose_cull_score.py <dir> --base dd6off; crop sheet like docs/owner_sheet_s7047_l12_kedge_variants.jpg.
2. Same-run hold L12 21:9: scratch/s7047/run_hold.zsh with ASP=21:9 (and CW/CH 840x360), "0.8,12" "0.8,12" (p1 = K0.6 baseline);
   tools/g5e_cost_by_parity.py tl run.log --phases 3 --skip-s 130 --split xor8. Then L1 21:9 if time.
Outcomes: H-same -> close the thread (owner look on docs/owner_sheet_s7047_*); H-wide-visible -> per-side N or K by aspect; H-wide-cost ->
report the trade in OWNER-OPT-INS and leave KEDGE=0 as the 21:9 fallback.
