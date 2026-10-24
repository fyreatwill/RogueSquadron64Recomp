# NEXT: G1c - fold s6071_togcap_far{1,4,025} (post-submit culler discriminator)
HYPOTHESIS-ID: g1c-heap-exhaustion
Soaks queued s6071 (SOAK-RESULTS.md, logs in scratch/agent/soak_results/): within-run dd1<->dd2 toggle, ucode cap 262144, DD_FAR=1/4/0.25. Fold: per arm, mean [g1cf] tri at dd=1 vs dd=2 (filter tri>=50), and score fb dumps with tools/g1c_fixed_score.py / g1c_ddtog_fold.py.
Positive control: far025 must cut tri (~-45%). If far4 raises dd2 tri/terrain fraction vs far1 => H-clip: far plane is the lever (then wire ROGUESQ_DRAW_DISTANCE to scale far at dd>1 and auto-raise cap). If flat => H-fog / H-cull-guest: compare gridlog kept vs req at dd2, read the second distance test after streamTerrainGridCellsByDistance (0x80042B50); also view one fb pair by eye.

S6072 note: far025 already folded (dd1 489 vs ref 674 = -27%, dd2 695, ratio 1.42; control weaker than the -45% expected). Remaining: far1 and far4 logs in scratch/agent/m6/g1_lvl1g1c6071far{1,4}/run.log; use the same fold (tri>=50 split by [ddtog] blk). Do not re-fold far025.
