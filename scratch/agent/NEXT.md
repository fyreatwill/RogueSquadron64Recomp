# G1d: find the texrect that draws up_167 (maskt=5, lrt=80) and its t-range
HYPOTHESIS-ID: g1d-widescreen
s6238: texrectT logger (ROGUESQ_LOG_TEXRECT_T) filtered on fmt4/4bpp/tmem0/line4 saw only lrt=60 (16 rows, t<=15.75) and lrt=316 (80 rows) draws, maskt=0; the maskt=5/lrt=80 render tile never appeared in the first 120. H-sample-stale unproven either way.
Next: change filter to tt.maskt==5 (any fmt), uncapped for that class, keep 20-any control; run scratch/agent/s6238_run.sh wide. If a draw exists with t beyond 21 -> H-sample-stale (then zero/clamp rows >=21 in one arm). If none -> the noise is not from up_167 sampling; revisit which draw produces the garbage rect (key by screen rect in the corrupt region).
