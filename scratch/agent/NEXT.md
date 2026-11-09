# NEXT: G1c — 300 s holds of the dd6 + fog-depth off-map cull recipe on L1, L4, L5 (qualify the s7035 opt-in)
HYPOTHESIS-ID: g1c-offmap-fogdepth
Context: s7034 (L1) + s7035 (L4) selected H-general: ROGUESQ_DD_OFFMAPCULL=2 _H=off _K=0.6 is ~invisible at 15 frozen poses (<=0.18 vs
uncut-cull controls up to 39) and saves rsp 3.04 ms (L1, 54.8->60 fps) / 1.52 ms (L4, 55.5->58.5). Opt-in line is in docs/OWNER-OPT-INS.md
but says "not yet held 300 s on a third level". G1c phase-2 done-criterion: 300 s holds, 0 crashes, no frame-time regression.
G5i/owner items: nothing to run (CURRENT-TRUTH Next steps 1-14).
Hypotheses:
 H-clean: L1/L4/L5 each hold >=300 s with K=0.6, 0 crash, 0 VI stall, fps >= the K=0 same-run phase -> OWNER-OPT-INS line loses "experimental", close the dd6 headroom thread.
 H-crash: a crash/stall appears only with the cull (culling list entries the game later dereferences) -> backtrace, name the reader, fix.
 H-L5cost: L5 (not yet measured) shows win < 0.5 ms -> state per-level wins; still offered.
Work (no build needed): per level LV in 1 4 5, one run of scratch/s7034/run_cost.zsh with a longer flight (copy to scratch/s7036/run_hold.zsh and pass
 dur 330 instead of 110 to arm.zsh; tog3 R=-1,2,2 K=0,0.6,0.6 gives same-run K=0 vs K=0.6 cost AND >=300 s exposure to the cull).
 Score: python3 tools/g5e_cost_by_parity.py --phases 3 --skip-s 130 <tl> scratch/agent/m6/g1_lvl<LV>s7031<N>/run.log ; crashes from scratch/s7031/crash_<N>.txt.
Pose-scoring trap (s7035): under NOREF runs split into two discrete paths; base and A/A must be on the same path as the arm.
