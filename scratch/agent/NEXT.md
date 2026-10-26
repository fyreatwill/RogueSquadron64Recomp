# Next: find what actually bounds the drawn terrain footprint (G3c a)
HYPOTHESIS-ID: g3c-owner-visual
s6307 showed the r2 cell test (0x800434E4) pass flip does not change drawn terrain. Candidates: H-frustum (corner vector at 0x80043918 sets the cell rectangle that buildGridCellMesh iterates), H-consumer (the pass flag is ignored/overwritten before the mesh builder), H-alt (edge is the grid layer scroll/stride, computeGridLayerScrollOffset).
Discriminator, one build: opt-in env that clamps the 0x80043918 footprint extents (scale far rows by 0.5) in one run with a phase-gated toggle; positive control = terrain_med must drop. Score with tools/g3c_edge_score.py / g3c_horizon_score.py on the fbd. If footprint shrinks -> choose fade/ring on that bound; if not -> trace the cell list consumer statically.
Also ask owner re ROGUESQ_CULL_SPIKE default (G3c b) when an owner message is possible.
