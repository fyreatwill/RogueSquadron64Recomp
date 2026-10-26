# Next: why does the 0x8004B644 colour write not reach the rendered terrain?
HYPOTHESIS-ID: g3c-owner-visual
s6313: x0.2 scale at 0x8004B644 epilogue gave no darkening (109.9 vs 106.3). a0 = $s3+0x10.. in buildGridCellMesh (0x8004B930), logged a0 steps 0x10, low nibble 0xC (looks like Vtx RGBA).
Hypotheses: H-overwrite (later pass stores colour into same Vtx), H-cache (mesh cells built once, hook window missed or cells reused from a cache), H-notvtx (a0 is scratch consumed by a different copy).
1. Read funcs_10.c from 0x8004BFF4 to end of buildGridCellMesh (and callers): list every sb/sw/sh via $s3-derived pointers after the jals.
2. Discriminator: same x0.2 hook plus a write-watch (log) on the a0 address from a later hook point; or scale at the point just before the DL submit. Control: scale ALL Vtx colours at submit => must darken.
3. Then implement ROGUESQ_EDGE_FADE and 3-arm dd3 soak (tools/g3c_edge_score.py).
Also ask owner re ROGUESQ_CULL_SPIKE default.
