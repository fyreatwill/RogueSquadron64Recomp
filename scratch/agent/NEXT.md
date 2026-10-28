# NEXT: rerun CAP_ALT with reversed rotation and denser frame dumps
HYPOTHESIS-ID: g1c-span-reject-predicate
State (s6542): same-run toggle works (positive control ok). inf cap ~2.9x cost per swap; cap0 vs cap120 order-confounded; only 8 fbd frames.
Work unit: add ROGUESQ_CAP_ORDER=rev (inf,120,0) to s6537_take, rebuild, run lvl1 with ROGUESQ_FB_DUMP_EVERY=20, fold with tools/g1c_bycap.py and the fbd-by-cap scorer (inline in s6542 session, needs w640 + tag via [fbdump] n= after last [capalt]).
Outcomes: cost cap0 < cap120 in both orders -> cap cost real; terrain fraction cap120 > cap0 with >=15 frames each -> cap buys terrain; else cap irrelevant, then proceed to dd3/dd4 holds on lvl 1/5/10.
