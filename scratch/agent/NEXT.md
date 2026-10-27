# NEXT: G3c(a) fold s6363 height-fade soak
HYPOTHESIS-ID: g3c-owner-visual

Built s6363 (hook at 0x80011788, see PORTING-STATE s6363). Soak scratch/agent/soak_queue/s6363_g3c_heightfade.sh runs between iterations; results in SOAK-RESULTS.md and scratch/agent/m6/s6363_g3c/.
Fold it: (1) grep '[heightfade]' in each arm log (n>0 for y/ylow/ycontrol; src in 0x80000000..0x807FFFFF) ; (2) view a ycontrol fb vs nofade at the same frame - terrain must be visibly displaced (else hook not on drawn cells: fix first); (3) tools/g3c_horizon_score.py on each arm dir; compare jump_med.
- jump_med drops >0.03 (y or ylow) -> adopt, bundle into DRAW_DISTANCE, ask owner.
- control visible but jump unchanged -> raise footprint radius past 34 / fade source f is stale (consider per-cell d).
- control invisible -> hook not on drawn cells (try renderUnlitMeshFaces 0x80011C9C and flat words funcs_4.c:7501/7518).
If the soak has not run yet, run it by hand (one game at a time).
