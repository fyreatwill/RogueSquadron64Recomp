# Next: opt-in outer-ring fade for the jagged far-terrain edge (G3c a)
HYPOTHESIS-ID: g3c-owner-visual
s6308: edge = frustum trapezoid far side (H-frustum; dd scales it, r2 test does not gate it). Fix candidate: ROGUESQ_EDGE_FADE=<cells> fades vertex alpha/shade of the outermost cells toward the sky/fog colour.
Step 1 (static): in funcs_9.c buildGridCellMeshForFace (13869) / funcs_10.c buildGridCellMesh (19971) find where per-vertex colour/alpha is stored; confirm with one grep-enumerated list of stores.
Step 2: add the opt-in via tools/apply_*.py + fixup (not a hand edit), 3-arm dd3 soak (none / fade 4 / fade 8) scored with tools/g3c_edge_score.py; positive control = fade 99 must visibly darken/transparent the terrain in fbd.
Also ask owner re ROGUESQ_CULL_SPIKE default (G3c b) when possible.
