# NEXT: G1d owner contact sheet + 21:9 menu/hangar recheck, then G1e frame-rate
HYPOTHESIS-ID: g1d-widescreen
s6428 verify folded (s6430): logo centred, 16:9/21:9 flight fine. Remaining G1d: (1) 21:9 hangar/menu frames from scratch/agent/m6/g1_lvl1s6428_a219/fbd (w640 range) - check centring/garble; (2) build owner contact sheet 4:3/16:9/21:9 same pose (a43/a169/a219 late frames, s6429_view); (3) fix wide-arm detection in g1_level_coverage_common.zsh so 'allattempts-failed' stops being a false negative. Then G1e: measure distinct framebuffers/sec per level with the G1b instrument.
