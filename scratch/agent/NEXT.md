# NEXT: G1c - scale the PRE-ALLOC cell count (allocAndInitGridCellArray $a0) and fog arm
HYPOTHESIS-ID: g1c-draw-distance
s6026: post-load rewrites of grid words are void (count latched at rs_malloc 0x800480BC). Remaining levers: H-count (incoming $a0 of allocAndInitGridCellArray / loadLevelAssets, halfword 0x80130C4C; callers pass getLevelExpansionMemoryBudget=0x800 or lhu 0x800B090C[s0]), H-fade (ROGUESQ_FORCE_FOG in flight), H-farplane.
Work unit: add an env ROGUESQ_DD_CELLMUL applied at entry of loadLevelAssets (find how existing fixup/patch hooks recompiled funcs; put in tools/fixup_*.py so it survives regen). Arms in ONE build: x0.25 (control: tri/task must drop >10% or alloc fails visibly), x2. Check heap: x2 may crash -> capture site. Measure with the tricnt fold used in s6024 (awk over run.log, tri>=50 mean). If hook cost is high, run fog arm first.
Outcomes: x0.25 shrinks & x2 grows => H-count is the extend lever; x0.25 inert => count unrelated to draw set, go fog.
