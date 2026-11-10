# NEXT: cheaper lever for 21:9 L12 at the dd6 bundle (bundle holds ~56 fps there, s7048)
HYPOTHESIS-ID: dd6-bundle-219-l12-cost
Context (s7048): 21:9 L12 frozen poses: KEDGE gate invisible (0.06 vs KEDGE=0 ctl 0.66). Same-run hold 21:9 L12: K0.6 56.5 fps rsp 13.48,
ke12 55.6-55.8 rsp 13.75, P(>=2VI) 0.06-0.08. At 16:9 the same bundle holds 59.7 (rsp ~12). The gap is the 21:9 cell load, not the gate.
s7026 (L1 21:9): cap 10240 = 53-54 fps vs 59 at 8192 before the bundle existed -> the cap is the cheapest lever.
Hypotheses: H-cap (WIDEWIN_CAP 8192 at 21:9 L12 holds >=58.5 with the bundle and the poses stay <=0.1 vs cap 10240) /
H-cap-visible (8192 is fast but shows side-edge ground loss >0.1 at the poses) / H-other (8192 does not reach 58.5: cost is elsewhere,
e.g. near cells / objects at 21:9; then measure rsp split or try K per aspect).
Unit (no build):
1. Same-run hold L12 21:9: copy scratch/s7048/run_hold.zsh, set ROGUESQ_DD_WIDEWIN=tog3 ROGUESQ_DD_WIDEWIN_CAP=10240,8192,9216 and KEDGE
   0.8,12 in all phases ("0.8,12;0.8,12;0.8,12"), K=0.6 all phases; tools/g5e_cost_by_parity.py tl run.log --phases 3 --skip-s 130 --split xor8.
2. Poses L12 21:9 (scratch/s7048/run.zsh) arms cap10240 (=fold) / cap8192 / cap9216; score with tools/s7032_pose_cull_score.py --base cap10240
   plus a dd6off-vs-dd4 style positive control (foldk0 arm again, must score ~0.66).
3. If time: L1 21:9 same-run KEDGE cost (run_hold.zsh lvl 1), still unrun.
Outcomes: H-cap -> per-aspect cap in the s7037 bundle (21:9 -> 8192/9216) as a code change; H-cap-visible -> report the trade in OWNER-OPT-INS;
H-other -> rsp breakdown at 21:9 L12.
