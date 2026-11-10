# NEXT: qualify the s7050 21:9 K=0.5 bundle default on L1/L4/L13 (image) + one L12 hold at the default
HYPOTHESIS-ID: dd6-bundle-219-l12-cost
Context (s7050): dd6 bundle now uses OFFMAPCULL_K=0.5 when FB_WIDTH>796 (21:9). L12 21:9: +0.9/+0.7 fps vs 0.6, poses 0.00 (ctl 0.60).
Only L12 poses checked; s7038 qualified L1/L4 21:9 at K=0.6 (<=0.18/<=0.23).
Hypotheses: H-clean (K0.5 vs K0.6 <=0.1 mean dLum at every in-flight pose on L1, L4, L13) / H-visible-elsewhere (some level shows a
horizon sliver/cut at K0.5 > 0.3 -> revert to 0.6 or make K per-level) / H-l1-sliver (L1 low eye poses see the fog line move but <0.3).
Unit (no build):
1. Poses: copy scratch/s7050/run.zsh; arms k05 (=new auto default, no explicit K) / k06 (+ROGUESQ_DD_OFFMAPCULL_K=0.6) / foldk0 ctl
   (+KEDGE=0) per level LV=1, 4, 13: `zsh run.zsh <LV>`; score tools/s7032_pose_cull_score.py <dir> --base k06 --aa foldk0. Ctl must be >0.3 on L4/L13 at least.
2. Hold: scratch/s7050/run_hold.zsh-like on L1 with K tog3 "0.5,0.6,0.5" for A/A and cost on a non-L12 level.
Outcomes: H-clean -> close the 21:9 L12 cost thread, owner look; H-visible-elsewhere -> revert the 21:9 branch in main.cpp (s7050 block) or gate it.
