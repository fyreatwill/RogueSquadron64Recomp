# NEXT: where does buildGridCellMeshForFace (0x8004317C) drop cells at dd4 before 0x8004349C
HYPOTHESIS-ID: g1c-dd8-limit
s6491: list nonempty every call; chain empty on 41% of dd4 calls vs 5% dd1. Hypotheses: H-lod (per-cell dist^2 vs table 0x8009DE94 culls all cells; s6417), H-early (a pre-loop exit in ForFace e.g. face/visibility flag), H-variant (selectGridCellTileVariant 0x80046030 gate skips).
Do: read funcs_9.c 14633-15400 branch structure; add one build with cumulative per-exit/per-gate counters (like s6476, [forcum] at fbdump) incl. cells visited vs cells reaching 0x8004349C; rerun scratch/agent/s6491_gridcum.sh (dd1 control + dd4). Fix tools/g1c_lowframe_tris.py fb list to 0x80620000,0x80690000.
Outcomes: visited cells high but reach-349C low with one dominant exit => that exit is the gate (read its operand); visited low => early exit before the loop.
