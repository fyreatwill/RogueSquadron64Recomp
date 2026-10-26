# Next: read s6306 edgedrop soak (G3c a)
HYPOTHESIS-ID: g3c-owner-visual
Fold scratch/agent/SOAK-RESULTS.md s6306_g3c_edgedrop lines. Score fb dumps in scratch/agent/m6/s6306_g3c with tools/g3c_edge_score.py / g3c_horizon_score.py: terrain fraction + row-wise boundary roughness per arm (dd3_none vs drop100 vs drop30); grep [celltest] d2 range from the logs to sanity-check thresholds.
Outcomes: drop30 shrinks footprint -> hook controls the edge; choose threshold fading/ring and compare roughness. No change in any arm -> hook is near-ring only; move to footprint planes (0x80043918 corner vector) or vertex alpha. Then ask owner re ROGUESQ_CULL_SPIKE default (G3c b).
