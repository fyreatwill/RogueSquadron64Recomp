# NEXT: fold remaining s6529 soaks (lvl5, dd4off lvl1 control), then name the span-saturation writer
HYPOTHESIS-ID: g1c-span-reject-predicate

1. Read SOAK-RESULTS.md for s6529_dd4_bypass_lvl5 and s6529_dd4off_lvl1; score with `python3 -I tools/g1c_fixed_score.py scratch/agent/m6/<tag>/fbd`. Opt-out arm must match s6459 lvl1 (~0.049) = toggle positive control; if it matches bypass (~0.09) the toggle is broken.
2. Make g1_level_coverage_common.zsh keep the G1B frame-time/tri lines (grep in the game's stderr) so bypass cost is measurable.
3. ORIGIN work: log pre-clamp inputs to scanConvertTriangleToSpanTable at dd4 to name the writer of -128 (H-footprint-exceeds-range vs H-wrong-scale-input).
