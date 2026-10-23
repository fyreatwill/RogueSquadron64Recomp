# NEXT: G3 - tint white-pillar stubs on the Available Craft page

HYPOTHESIS-ID: g3-render-fidelity

s5969: ROGUESQ_TINT_OM works (control green). 0x504240 tris on Select Craft are legit decals. Stub pillars live on Available Craft page (later page than scratch/agent/s5969_tint2.sh reaches).
Work unit: copy s5969_tint2.sh, extend PROBE_KEYS so frames reach Available Craft (compare s5964/r12.png), extend rt64 TINT_OM with mode 3 = tint untextured tris whose cc is shade-only and vertex colour is near white; log DL ptr. Hypotheses: H-dl wrong texture/DL upstream vs H-geom transform. Positive control: mode 1 same recipe. Outcome: stub DL source then trace in ucode DL builder.
Do not do aim/steer work.
