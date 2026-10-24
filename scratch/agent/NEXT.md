# NEXT: G1c - fold s6053_dd1_l5 / s6053_dd2_l5 (clamp-as-maxima fix)
HYPOTHESIS-ID: g1c-draw-distance
Hypothesis: s6053 fix (clamp DB4/DBC as maxima, not counts) removes the u32-wrapped window at 2x. Alternatives if not: H-bound-starve (s6048 span-table skips starve binning) or H-radius-neg (game's own min/max inverted at scaled radius).
Discriminator: in SOAK-RESULTS/logs of s6053_dd2_l5: grep [gridlog] - w/d must be <=64, kept >= dd1 kept (control s6053_dd1_l5 must be sane, kept=1+). fb capture must show more terrain than dd1. If w still wraps -> add [winlog] before/after clamp (0x800429C0) and at streamTerrainGridCellsByDistance entry in one build.
If sane: run dd2 levels 1 and 10 (FORCE_PLANET_UNLOCK=0xFF, SOAK_TIMEOUT>=900), ROGUESQ_G1B frame time vs dd1, then dd15/dd3, then ask owner to judge the look. Default stays retail.
