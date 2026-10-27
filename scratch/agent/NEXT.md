# NEXT: dd4 low-ground frames — confirm fewer cells reach draw (H-data) with a per-VI pass-cell count
HYPOTHESIS-ID: g1c-dd8-limit
s6488: low-ground dd4 frames submit ~28% fewer tris, no ceiling (H-budget not indicated), single-source.
Do: (1) extend tools/g1c_lowframe_tris.py to sum [tricnt] over all tasks per VI (between consecutive fbdump/present lines); re-run on s6487 d1/d4 for a comparable dd1-vs-dd4 tri total. (2) If a cell-gate counter is cheap to add (ROGUESQ_* log in the cell-population pass loop), one build logging pass-cell count per VI, same dd4 run, join with ground score. Positive control: dd1 pass count > 0.
Outcomes: low frames have fewer pass cells => H-data, find which gate rejects (distance/visibility flag writer); equal pass cells but fewer tris => cull in the submit path.
