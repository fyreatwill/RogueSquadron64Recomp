# Next: validate cell scale, then camera-centred edge fade
HYPOTHESIS-ID: g3c-owner-visual
State (s6321): camera world pos = floats at *(0x80138D1C)+0x4C..0x54 (x,y,z). Log ROGUESQ_G3C_CAMLOG=1 exists.
Hypotheses: H-scale12.8 (cell = pos/12.8, ring dim 64/128 wraps) vs H-other (cell scale differs).
Measurement: one run with ROGUESQ_G3C_CAMLOG=1 + ROGUESQ_EDGE_FADE_LOG=1 (AA94 cell stash [edgefade5]); offline: for each frame, circular mean of AA94 visited cells should lie within a few cells of (camX/s, camZ/s) mod dim for the s that minimises residual; positive control: wrong s (e.g. 1.0) gives uniformly worse residual. Frame-join on n ordering.
If s found: implement ROGUESQ_EDGE_FADE in AA94 using circular distance from the camera cell; verify with tools/g3c_horizon_score.py on dd3 frames.
