# NEXT: G1c - fold s6061 arms (heap exhaustion hypothesis), then fix heap for dd2
HYPOTHESIS-ID: g1c-draw-distance
s6061: px4_dd2 SIGBUS = rs_malloc(0x1E4) NULL in allocateAndInitCraftNpcContext (unchecked), i.e. guest heap exhausted by the dd2 window (kept 1243 vs ~365 cells). `[mallocnull]` log built.
Fold arms in scratch/agent/SOAK-RESULTS.md / soak_results: s6061_px4_dd2b (expect [mallocnull] = positive control), px3_dd2, px4_dd1, px8_dd1.
Hypotheses: (A) heap use scales with active window (dd2 crashes at px>=3-4, dd1 never) ; (B) poolx alloc alone exhausts (px8_dd1 crashes) ; (C) NULL is from a different allocator limit (fragmentation).
Next unit: log rs_malloc free/high-water at the window rebuild; if A, either enlarge guest heap under DRAW_DISTANCE or cap NPC spawn to retail cells; then rerun `python3 tools/g1c_ddtog_fold.py scratch/agent/m6/g1_lvl1g1cpx4_dd2 4500 --hud`.
