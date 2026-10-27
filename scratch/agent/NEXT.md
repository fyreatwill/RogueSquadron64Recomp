# NEXT: locate the downstream loss of dd3 terrain cells (G1c phase 2)
HYPOTHESIS-ID: g1c-dd-phase2
s6415 fold: supply exonerated (kept<cap everywhere, DL pool never drains). Terrain present in the cell list at dd3 but absent on screen.
Hypotheses: H-farclip (per-node distance/far-clip test in the terrain submit path rejects cells beyond retail radius, not scaled by dd); H-vtx (vertex/DL build for a cell is skipped when its tile data isn't resident/streamed - tiles streamed only within retail radius); H-ucode (cells emitted but clipped by the F5 clip/guard or ROGUESQ_UCODE_CAP).
Discriminating measurement: one instrument/one build on the pinned recipe (scratch/agent/soak_queue/done/s6415_dd_grid.sh): per frame, for the cells in the kept list, count (a) entering the per-node submit, (b) rejected by each early-out (name the branch), (c) DL words emitted, (d) RDP triangles with terrain-cell origin. Arms d1b/d2/u3 in one iteration.
- (a)>>(c) with a named early-out that depends on distance => H-farclip: scale that constant by dd.
- (c) grows but tris not => H-ucode.
- (a) grows, (b) none, (c) flat => H-vtx (tile residency).
Find the submit callee of streamTerrainGridCellsByDistance first (grep generated funcs for its caller in buildVisibleTerrainGridAroundCamera).
