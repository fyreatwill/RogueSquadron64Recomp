# NEXT: G1c - fold the s6027 CELLMUL arms, then fog arm
HYPOTHESIS-ID: g1c-draw-distance
Soaks s6027_g1c_cell025 and s6027_g1c_cell2 (ROGUESQ_DD_CELLMUL, pre-alloc cell count) run between iterations; read their SOAK-RESULTS.md lines and logs. Grep `[cellmul]` to confirm the knob fired (positive control), then fold tri/task (tri>=50 mean, awk as in s6024/s6026) vs the retail baseline.
Outcomes: x0.25 drops >10% and x2 rises => H-count is the extend lever (then 1.5x/2x/3x steps, 300 s holds on lvl 1/5/10). x0.25 inert or crash/alloc failure => record, then run the ROGUESQ_FORCE_FOG in-flight arm (H-fade), then H-farplane.
