# NEXT: does L13 (second load-bearing level) at 21:9 earn K=0.5 too?
HYPOTHESIS-ID: dd6-219-levelK-l13
Context: s7056 landed ROGUESQ_DD_OFFMAPCULL_KLEVEL (auto 12:0.5 at FB_WIDTH>796). L13 (64x64) was the other level the cull holds at 16:9
(48.3 -> 59.9, s7043); it has never been run at 21:9. If it sits below 60 there, K=0.5 may buy what it bought on L12.
Hypotheses:
 H-l13-gain: L13 21:9 bundle < 59.5 fps and K=0.5 gives >= +0.5 fps (rsp <= -0.8 ms) same run, poses <= 0.05 vs K=0.6 -> add 13:0.5 to the auto KLEVEL.
 H-l13-free: L13 21:9 already ~60 fps at K=0.6 -> nothing to gain, close; KLEVEL stays 12:0.5.
 H-l13-visible: K=0.5 frees fps but poses > 0.1 (horizon band like L4) -> keep 0.6.
Unit: (1) zsh scratch/s7056/run_hold.zsh L13t 13 tog   (K 0.5/0.6/0.5 same run; 508 s); edit KLEVEL in the script to 13:0.5 first.
      score: python3 tools/g5e_cost_by_parity.py --phases 3 --skip-s 130 --split xor8 scratch/s7056/tl_L13t.bin* scratch/agent/m6/g1_lvl13s7031L13t/run.log
(2) only if H-l13-gain on cost: frozen poses at K 0.5 vs 0.6 vs KEDGE=0 control (s7050 recipe; tools/s7032_pose_cull_score.py).
Owner-gated items (G5a-G5i, L15 21:9, G1d) still need nothing run.
