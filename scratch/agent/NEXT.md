# NEXT: G1c phase 2 - find the clamp that makes dd6 draw <= dd4
HYPOTHESIS-ID: g1c-dd-phase2
State: s6547: dd6 clean 203 s, no heap exhaustion, but cheaper (56 vs 109 ms/s) and no more terrain than dd4 (tight 0.069 vs 0.117). Something clamps footprint/work above dd4.
Hypotheses: H-ucodecap (ROGUESQ_UCODE_CAP=65536 default truncates the task), H-grid (cell grid/stride dims s6035 clamp radius), H-pool (a pool silently refuses allocs).
Work unit: same s6547 recipe at dd6 in arms: UCODE_CAP=262144 added; grep run.log for [dd]/[cap] clamp prints; in one build log the effective radius/cell-count in buildVisibleTerrainGridAroundCamera at dd4 vs dd6. Positive control: dd4 vs dd6 radius differs if unclamped.
Outcomes: radius equal -> H-grid; terrain/cost rises with cap -> H-ucodecap. Then G3c(b)/(c).
