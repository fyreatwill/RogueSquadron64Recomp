# NEXT: G3c(a) H-grid — height-byte fade/smoothing arm
HYPOTHESIS-ID: g3c-owner-visual

s6362: terrain Vtx positions are built by the RSP (TRI_GEN) from 25 height bytes at cell+0x44; no CPU position store exists.
Work unit: at the call site 0x8001178C in renderFlatMeshFaceGroup (funcs_4.c:7728; also renderUnlitMeshFaces 0x80011C9C), when ROGUESQ_EDGE_FADE_R2_Y is set, copy the 25 height bytes to a per-call scratch buffer (guest memory below 0x81000000), lerp toward a horizon height over the cell radius r=26..34 (reuse the radfade2 d from A6C0 or recompute from cell+0x18/0x1A vs camera), pass the scratch pointer as params[2]; also scale flat words at funcs_4.c:7501/7518. Add a +50 constant-offset control arm. Fixup-backed (tools/apply_s6311_edgefade.py style). Soak nofade/y/ycontrol with the s6359 recipe; score with tools/g3c_horizon_score.py.
- jump_med drops >0.03 -> adopt, bundle into DRAW_DISTANCE, ask owner.
- control visible but jump unchanged -> raise footprint radius past 34.
- control invisible -> hook not on drawn cells; fix before concluding.
Do the survey/edit INLINE; do not delegate and then wait (s6362 lost the stop-gate budget that way).
