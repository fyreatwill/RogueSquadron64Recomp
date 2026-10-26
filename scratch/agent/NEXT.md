# Next: G3c(a) horizon-profile scorer across arms
HYPOTHESIS-ID: g3c-owner-visual
Write tools/g3c_horizon_score.py: per column topmost terrain-coloured row in mission frames; metrics = mean |row jump| between adjacent columns above a smoothness floor, and interior sky-hole pixel count below the horizon. Positive control: dd3_aspect frame fb_0004059_w1024 (scratch/agent/m6/g1_lvl1s6297_dd3_aspect/fbd) must score high. Run on g1_lvl1s6293_{retail,dd2,dd3} and g1_lvl1s6297_{aspect,dd3_aspect}. Arm with high jumps/holes that retail lacks owns the defect -> then root-cause (cell footprint boundary / missing cell link) with a writer named.
Then G3c(b) spikes.
