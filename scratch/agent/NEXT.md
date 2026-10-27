# NEXT: buildGridCellMesh exit-path census (H-bgcm-gate)
HYPOTHESIS-ID: g1c-dd8-limit
Established (s6475): farclip cutoff x4 grows chain 687->930 but stripN unchanged (18.5 vs 20.0): cutoff refuted. s6474: only ~5% of buildGridCellMesh entries emit strips at dd2 and dd3.
Hypotheses: H-gate-A (state byte at cell+0x14 / 0x8004B978 gate skips cells: cell flags not set for far cells), H-gate-B (0x8004B9C0/9CC tile-variant gate), H-gate-C (cell geometry not yet mapped / empty).
Work: via apply_s6474_subcount.py add per-exit counters at each branch leading to L_8004C294 inside buildGridCellMesh (funcs_10.c ~20912+), print in [sublog]; run pinned dd2 vs dd3x4. Outcome: the exit whose count dominates and differs names the lever.
