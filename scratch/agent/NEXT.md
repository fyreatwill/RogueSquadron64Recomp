# NEXT: dd4 low-ground frames — per-VI pass-cell count and tris/cell (one build)
HYPOTHESIS-ID: g1c-dd8-limit
s6489: summed per-VI tris confirm low-ground dd4 frames submit ~28% fewer tris (1239 vs 1726); dd4 high frames submit ~half of dd1 tris (cross-run lead).
Do: one build adding ROGUESQ_* log in the cell-population pass loop: per VI pass-cell count, and cells-with-geometry; same dd4 and dd1 runs (positive control: dd1 count > 0). Join with ground score via tools/g1c_lowframe_tris.py.
Outcomes: low frames have fewer pass cells => H-data, find which gate rejects; equal cells but fewer tris => per-cell LOD/cull in the submit path (also explains dd4 < dd1 tris).
