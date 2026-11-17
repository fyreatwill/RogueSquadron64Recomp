# NEXT (s7505)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7504_fb_levels (rows `tag=s7504_fb_levels fb arm=` in scratch/s7504_fb_levels/out.txt). Score 5 is
EXPECTED. Pass = ctl=ok every arm, every t~28.2 mission-load row in0 (field stride / before origin), every in1 row <=4 px for <=2 swaps.
An in1 row on a LIT frame (meanlum > 0.05) or a header shown for > 2 swaps is new: read it. Then FB CLOSED 6 levels.

Work unit, class FC (generalises FB beyond upload-armed fbs; one instrument, one run): over a whole run, how often does ANY heap header
appear inside the scanned VI window? Per swap (rs64_s7503_swap), walk the live heap chain (upstream_compat rs64_s7496 walker) and test each
block header address against the scanned rows of the committed VI fb (VI_WIDTH stride, h/v window, odd-row field rule from s7504).
Hypotheses: H-fc-load (hits only at load/abort transitions, black frames, <=2 swaps: closes the heap-on-screen idiom class) /
H-fc-flight (a header inside a lit flight frame: real visible garbage, name the block owner) / H-fc-none (0 hits outside FB's rows).
Control: synthetic header address = VI origin + 40 rows (must hit every swap the ctl runs). Recipe: wrap tools/s7504_fb_recipe.zsh with
ROGUESQ_S7505_FC=1, LV default (L4 dd1, L15 dd8) + XC ROGUESQ_ASPECT=4:3 arm. If H-fc-load/none on both: close the heap-audit series
(m3-partition-over-live-block) in CURRENT-TRUTH and take the next ladder rung per ITERATION 3c.
