# Next: fold s6314_g3c_edgefade2 soak; which lit-RGB writer owns terrain colour?
HYPOTHESIS-ID: g3c-owner-visual
Hypotheses: H-A6C0 (0x8004A6C0 writes terrain colour; t2 arm darkens, both darkens), H-B644-only-other-store (neither darkens => colour overwritten/baked elsewhere, e.g. 0x80049700 helper or DL-time), H-partial (both needed).
1. Read scratch/agent/SOAK-RESULTS.md tail; compare mean brightness of FB dumps in scratch/agent/m6/s6314_g3c/{base,t2,both} (use same VI phase). Control: both arm must darken more than base.
2. If t2 darkens: implement ROGUESQ_EDGE_FADE (scale by distance from camera/cell edge using x/y/z) in A6C0 and B644 hooks, run 3-arm dd3 soak with tools/g3c_edge_score.py.
3. If neither: scale colour at DL submit (Vtx copy) as control; find Vtx colour writer.
Also ask owner re ROGUESQ_CULL_SPIKE default.
