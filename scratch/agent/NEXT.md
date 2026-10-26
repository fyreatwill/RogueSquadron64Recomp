# Next: fold s6315 edgefade3 soak, calibrate grid-vs-player scale, score the fade
HYPOTHESIS-ID: g3c-owner-visual
Soak s6315_g3c_edgefade3 (arms dd3_log, dd3_fade, ret_log) writes scratch/agent/m6/g1_lvl1s6315_*/run.log.
1. From dd3_log [edgefade3] lines: is d centred on 0 with max ~78? If d is offset/huge, fix ROGUESQ_EDGE_GRIDSCALE or the player-record source (pl[1],pl[3] guess) and rerun.
2. Score dd3_fade vs dd3_log FB dumps with tools/g3c_edge_score.py: edge excess must drop, near terrain unchanged; positive control = f>0 count in [edgefade3] log and visible PNG tint.
3. Pick haze colour from the sky horizon pixels; then ask owner re ROGUESQ_CULL_SPIKE default, and send before/after PNGs.
