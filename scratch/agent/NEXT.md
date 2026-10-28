# NEXT: verify dd8/dd12 are really applied, score terrain fraction, 300 s holds
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6574): px4/dd8 (2/2) and px5/dd12 (1/1) lvl1 130 s clean with the spill recipe.
Work unit: (1) grep ROGUESQ_DD_LOG output in scratch/agent/m6/s6553_dd12_px5_A for the effective multiplier and far value; if clamped to 4, find the clamp and lift it under DD_UNSAFE. (2) Run the fixed-camera terrain-fraction scorer + FB dump sheet for dd1, dd8, dd12 (FB_DUMP_EVERY=20 already armed; see s6468p_dd8_sheet). (3) Hold 300 s on lvl 1,5,10 at dd8 px4 (HOLD_S=300, LEVEL=5/10).
Outcomes: dd differs in log and terrain fraction grows => bundle recipe behind ROGUESQ_DRAW_DISTANCE; identical to dd4 => clamp is the next limit.
