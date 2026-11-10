# NEXT: tune the L12 eye-to-edge K gate, then fold the best into the dd6 bundle
HYPOTHESIS-ID: dd6-bundle-l12-horizon
Context (s7046): ROGUESQ_DD_OFFMAPCULL_KEDGE=<k2>[,N[,mask]] (src/main/upstream_compat.cpp, rs64_s7031_cell). KEDGE=0.8,12 is invisible on
L12 poses (0.07 / 0% px vs dd6off) and holds 58.0 fps on L12 (bundle K=0.6 59.0, off 45.9, same run), L1 no cost. N=8 does not trigger at the
L12 poses (eye >8 cells from that edge). Bar for folding: invisible (<=0.1) AND L12 >=58.5 fps.
Unit (no build needed; all arms are env):
1. Frozen poses L12 (copy scratch/s7046/run.zsh): arms dd6off / ke12 (0.8,12) / ke10 (0.8,10) / k07e12 (0.7,12). Score
   tools/s7032_pose_cull_score.py scratch/s7047/L12 --base dd6off; crop sheet as in s7046 (python PIL, bottom 45%, cols k4/k6).
2. One L12 hold with tog3 phases K=0.6 / KEDGE-best-A / KEDGE-best-B: scratch/s7046/run_hold.zsh uses mask 4 for one variant; for two
   variants in one run you need per-phase k2/N (extend KEDGE parse to k2a/k2b or run p1=K0.6 baseline, p2 variant and do two holds).
Outcomes:
- a variant <=0.1 on poses and >=58.5 fps on L12 -> fold it into the s7037 bundle (src/main/main.cpp ~12049: setenv KEDGE overwrite=0),
  re-run L1 + L13 holds (cost) and the L1 poses (image), update OWNER-OPT-INS.
- none clears 58.5 but ke12 stays at ~58 -> fold KEDGE=0.8,12 anyway only if the owner says so; otherwise leave it opt-in and close the thread
  (owner choice already in OWNER-OPT-INS).
