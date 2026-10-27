# NEXT: L-lod / fog-haze lever for dd>1 (cell-population gates all closed, s6482-s6484)
HYPOTHESIS-ID: g1c-dd8-limit
H-lod: detail index at 0x80137CE4 (selectMeshLodAndSubmitForRender / setObjectDetailLevel) selects coarse/empty LOD slots for far objects/tiles, capping visible detail at dd>1.
H-fog: game haze/fog start/end not scaled with dd, so far geometry is faded/clipped by fog before the dd8 footprint matters.
H-budget: DL/vertex/tile buffer caps overflow at dd8 (s6466-s6467 dd8 lvl10 rc=1 in SOAK-RESULTS).
Work: grep PORTING-STATE/CURRENT-TRUTH for 0x80137CE4 writers/readers; one build logging per-frame detail index + fog params + DL byte count at dd1 vs dd6 vs dd8 (same run style as s6470 break_ab), phase-gated on VI. Positive control: force detail index to its max and see tri count change.
Outcome splits: index differs by dd => H-lod; fog params identical and terrain fraction saturates => H-fog; DL size near cap => H-budget.
