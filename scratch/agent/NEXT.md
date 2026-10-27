# NEXT: G3c(a) outer-ring alpha/cull for far-edge stair-step
HYPOTHESIS-ID: g3c-owner-visual

s6357 showed sky-colour fade (AA74, 18..26 and 26..34) leaves the stair-step intact. Hypotheses:
H-recolour-wrong (edge needs transparency, not colour), H-footprint (edge cells lie beyond fade radius), H-grid (partial outer ring is the step itself; culling it moves the boundary).
1. Build arms in ONE build: cull outermost ring of cells (env), alpha-fade outermost ring, nofade control; same phase gate (PROBE_KEYS_FROM_PHASE=1) at identical VI.
2. Score with tools/g3c_horizon_score.py (jump_med / hole_med) and make a same-frame contact sheet nofade vs each arm.
3. Edge step gone in cull arm only -> H-grid; alpha arm only -> H-recolour-wrong; none -> H-footprint, raise radius.
