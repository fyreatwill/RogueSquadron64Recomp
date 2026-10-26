# Next: G3c(a) rescore dd3_aspect with correct dump, then vertex ramp probe if edge remains
HYPOTHESIS-ID: g3c-owner-visual

s6297: s6293 aspect scores were a decode artifact; corrected aspect edge excess -0.0026 (retail 0.0212).
1. Copy scratch/agent/soak_queue/done/s6297 recipe pattern with spec "dd3_aspect|ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_ASPECT=21:9 ROGUESQ_OSMEM_MB=12", ROGUESQ_FB_WIDTH=1024; score with tools/g3c_edge_score.py and view a late-frame PNG (sips) vs retail.
   Edge visible in dd3_aspect only -> opt-in owns it (H-ramp: vertex shade probe). Not visible -> H-bare/no defect; ask owner for a screenshot.
2. Then G3c(b) spikes reference check.
