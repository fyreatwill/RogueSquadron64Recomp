# NEXT: G1c - read s6023 lod2/lod025 and s6024 igrid2/igrid025 from SOAK-RESULTS.md
HYPOTHESIS-ID: g1c-draw-distance
Hypotheses: H-lod (0x9ECB0 table), H-grid (int counts 0x137A58/60 + fixed buffer), H-fade (fog), H-farplane. 0x9DEAC and FOV are shrink-only (s6022, s6024).
Logs: scratch/agent/m6/g1_lvl1g1c<tag>/run.log. awk: /\[g1c\] state=/ sets state; /\[tricnt\]/ field tri=N, keep tri>=50, mean per state. Positive control = x0.25 arm must shrink >10%; pass for x2 = >+10% tri/task. x2 igrid may crash (heap overflow) - that confirms L-budget; capture the crash site.
If all null: fog arm (ROGUESQ_FORCE_FOG in flight), then locate the grid allocation (rs_malloc 200*(n/10) at 0x800480BC) and patch the count BEFORE allocation.
