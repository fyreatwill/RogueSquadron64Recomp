# Next: confirm 0x8004B644 a0 destination is terrain Vtx, then ROGUESQ_EDGE_FADE hook
HYPOTHESIS-ID: g3c-owner-visual
s6310: 0x8004B644 = point-light RGB accumulator, clamped byte stores at 0/1/2($a0), no alpha; the only colour writer among buildGridCellMesh callees.
Step 1: read callers funcs_10.c ~20600-21200 (0x8004BA3C..0x8004BF08) and name what a0 points at (Vtx +0xC? separate colour array?). Runtime check: log a0 and compare with the terrain Vtx buffer range in one run.
Step 2: if terrain, add ROGUESQ_EDGE_FADE=<cells> in tools/fixup (scale RGB toward fog colour by cell ring distance); 3-arm dd3 soak (none/fade4/fade8) scored with tools/g3c_edge_score.py; positive control fade 99 must visibly darken terrain.
Also ask owner re ROGUESQ_CULL_SPIKE default (G3c b).
