# NEXT: fold s6415_dd_grid soak (G1c phase 2, dd3/dd4 terrain missing)
HYPOTHESIS-ID: g1c-dd-phase2
s6414 result: H-chunk REFUTED (DL pool min=77 in d1b, d2 AND u3 alike, empty_b=0 everywhere; no drain). Remaining: H-pool (terrain node pool cap u16 0x80130C4C), H-cap/H-cull (window/kept count).
s6415_dd_grid = same pinned recipe + ROGUESQ_DD_GRIDLOG=1. Read scratch/agent/m6/g1_lvl1s6415_{d1b,d2,u3}/run.log `[gridlog]` lines (positive control: d1 kept>1, tracks req).
- u3 kept << req or kept == cap: H-pool (raise cap 0x80130C4C / carve arena per G1c ph2 plan).
- kept ~ req but terrain still missing: H-cull downstream (far-clip/per-node submit), probe the submit path.
- gx/gz range shrinks vs d2: window clamped (64 stride / terr dims).
