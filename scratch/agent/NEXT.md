# Next: G3c(a) far-edge treatment - fade/clip outermost cell ring at dd>1
HYPOTHESIS-ID: g3c-owner-visual
s6305: forced fog is flat across depth at dd3 (0.25/0.27/0.27) -> no distance ramp; edge = footprint trapezoid (with s6303 78 vs 29 cells). H-fade refuted.
Unit: in tools/fixup_*.py (find the buildGridCellMesh/cell-radius test from s6303), add opt-in (ROGUESQ_EDGE_FADE) treatment: drop or vertex-alpha-ramp the outermost N cell rings at dd>1. Build once, run dd3 fixed camera lvl1 with edge fade on/off in one queued soak (two arms), capture fb frames; compare edge stair-step visually and via row-wise terrain-boundary roughness. Positive control: ring-drop of 3 rings must visibly shrink the footprint.
Also ask owner re ROGUESQ_CULL_SPIKE default (G3c b).
