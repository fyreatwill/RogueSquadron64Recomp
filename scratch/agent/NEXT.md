# NEXT: cheaper fog-depth K at 21:9 for L12 with the dd6 bundle (cap lever closed s7049)
HYPOTHESIS-ID: dd6-bundle-219-l12-cost
Context (s7049): cap 8192 +0.7/+2.0 fps but drops a distant ground band (13.4 at L12 21:9 poses k4/k5); 9216 invisible, +0.5 fps only.
Same config gave 59.0 and 56.3 fps in two runs (host/path spread ~3 fps): only same-run deltas count.
Hypotheses: H-K (OFFMAPCULL_K 0.5 or 0.45 with KEDGE 0.8,12 keeps the L12 21:9 poses <=0.1 vs K0.6 and gains >=1.5 fps same run) /
H-K-visible (lower K shows the hard cut again at the poses; then K is not a lever at 21:9) / H-noop (lower K culls little extra:
ocull/f rises <10%, fps flat -> cost lives in near/on-map cells; then G1c phase 2 21:9 L12 is closed as "host-dependent ~57-59").
Unit (no build):
1. Hold: copy scratch/s7049/run_hold.zsh, WIDEWIN=1 CAP=10240, ROGUESQ_DD_OFFMAPCULL_K=0.6,0.5,0.45 (tog3), KEDGE "0.8,12" all
   phases; run twice with the order rotated (0.5,0.45,0.6); tools/g5e_cost_by_parity.py <tl.bin.PID> <run.log> --phases 3 --skip-s 130 --split xor8.
2. Poses: scratch/s7049/run.zsh arms k06 (=cap10240 base) / k05 / k045 (+ROGUESQ_DD_OFFMAPCULL_K=...; set OFFMAPCULL=2 H=off explicitly)
   / foldk0 ctl; tools/s7032_pose_cull_score.py <dir> --base k06 --aa foldk0. Positive control foldk0 must score ~0.6.
Outcomes: H-K -> per-aspect K in the s7037 bundle (main.cpp) as a code change; H-K-visible / H-noop -> OWNER-OPT-INS note and close.
