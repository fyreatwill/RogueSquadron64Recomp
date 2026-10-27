# Next: fit cell scale on cells that EMIT geometry, not cells visited
HYPOTHESIS-ID: g3c-owner-visual
State (s6322): flight camera pos = floats 9,11 at *(0x80138D1C)+0x28 (ptr varies; flight ptr 0x80138458). s6322 regression of VISITED AA94 cells vs cam/s is at random baseline for s=12.8 (AA94 sweeps the whole ring; visited set is not a footprint). tools/g3c_scalefit.py exists.
Hypotheses: H-scale (some s fits the EMITTING cells, residual <=3 cells) vs H-nonlinear (grid origin is not cam/s; need the build function's own grid origin args).
Measurement: in AA94 (tools/apply_s6311_edgefade.py), log cell only when the DL write pointer advanced during that cell; run lvl1 dd3 130 s with CAMLOG; rerun g3c_scalefit.py. Positive control: emitting-cell count>0 and its spread is much smaller than the full ring; wrong s stays at baseline.
If H-nonlinear: log buildVisibleTerrainGridAroundCamera args/locals (grid origin) in camlog and use those as the fade centre.
