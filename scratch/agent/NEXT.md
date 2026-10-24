# NEXT: G1c - fold px2/px2.5 heaplog arms
HYPOTHESIS-ID: g1c-heap-exhaustion
Fold scratch/agent/m6/g1_lvl1g1c64{2,25,25d2}/run.log (NOT soak_results; those are verdict lines). grep '\[heaplog\].*-> 00000000' after the [poolx] line; compare with SOAK-RESULTS rc.
Outcomes: px2.5 rc=0 and no post-pool NULL -> raise to 300 s holds on L1/5/10 at dd2, then g1c_ddtog_fold.py --hud for terrain/HUD; px2.5 NULLs -> px2 is the ceiling, document and measure its visual gain vs px1 (or find pool-block shrink: the 0x5C000 unit).
