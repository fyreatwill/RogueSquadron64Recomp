# Next: find the terrain vertex colour/alpha writer for the G3c(a) edge fade
HYPOTHESIS-ID: g3c-owner-visual
s6309: buildGridCellMeshForFace stores only neighbour-link bytes (no colour). Callees of buildGridCellMesh (funcs_10.c 19971): 0x80046214, 0x80049814, 0x80049BBC, 0x80049FB8, 0x8004AA94, 0x8004B644.
Step 1 (static): in RecompiledFuncs grep each callee for sb/sh/sw stores into a vertex-sized stride (colour bytes RGBA at +0xC..0xF of 16-byte Vtx) and name the colour/alpha writer; check whether alpha is used by the terrain combiner (else fade by scaling RGB toward fog colour).
Step 2: ROGUESQ_EDGE_FADE=<cells> via tools/apply_*.py + fixup; 3-arm dd3 soak (none/fade4/fade8) scored with tools/g3c_edge_score.py; positive control fade 99 must visibly darken the terrain.
Also ask owner re ROGUESQ_CULL_SPIKE default (G3c b).
