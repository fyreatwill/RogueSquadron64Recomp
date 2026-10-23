# NEXT: G1c - read s6023 arms (fov15/fov025/lod2/lod025) from SOAK-RESULTS.md
HYPOTHESIS-ID: g1c-draw-distance
Hypotheses: H-fov (0x80130C50 scale sets far extent), H-lod (0x9ECB0 table), H-grid (fixed grid buffer, needs build to scale int counts 0x80137A58/60), H-fade (fog).
Analyze logs in scratch/agent/soak_results/*s6023*: awk field $4 = tri, tri>=50, bin by [g1c] state. Positive control = x0.25 arm must change tri/visible; pass for x1.5/x2 = >+10% tri. If both null with working controls: build int-mode scaling for grid counts, then fog arm.
