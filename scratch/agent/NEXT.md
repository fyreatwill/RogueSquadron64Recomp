# NEXT: G1c phase 2 - why dd>=3 drops the near mountain (CURRENT-TRUTH item 0, s6413)
HYPOTHESIS-ID: g1c-dd3-missing-terrain
Hypotheses: H-pool (a terrain pool/arena sized for dd<=2 overflows at dd3, cells skipped), H-cull (per-cell visibility radius/LOD index wraps or clamps wrongly at dd3), H-dl (DL budget: ruled out by s6409/s6403 cap scaling, keep as control), H-scorer (s6413 single-frame/arm; re-check with several position-matched frames).
Discriminator: pose-locked (ROGUESQ_POSE_LOCK=1) lvl1 capture dd2 vs dd3 at identical pose, dump per-frame count of terrain cells submitted vs cells in radius; if submitted < expected at dd3 -> H-pool/H-cull (read the allocator failure / skip branch), if equal but pixels missing -> H-dl/ucode.
Start by reading s6413 in PORTING-STATE (grep 'Session 6413') and tools/apply_s6036_dd.py.
Closed this session: G3c(c) (s6457 soaks folded, see CURRENT-TRUTH s6458).
