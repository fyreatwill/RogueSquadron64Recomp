# NEXT: fold s6414_dd_pool soak (G1c phase 2, dd3/dd4 terrain missing)
HYPOTHESIS-ID: g1c-dd-phase2
Read SOAK-RESULTS s6414_dd_pool and scratch/agent/m6/g1_lvl1s6414_{d1b,d2,u3}/run.log (grep the DLPOOLLOG lines, `[s6098`). Restrict to the pose-matched window (early flight, same as view/s6413/sheet2.png frames).
- u3 pool length drains toward 0 while d1b/d2 flat: H-chunk. Name the consumer (see s6097: ~33 chunks/begin dd1, ~60 dd3), fix root cause (bigger pool/arena per G1c phase 2 plan).
- pool flat in all arms, terrain still missing: H-cull/H-pool/H-cap. Next probe: terrain grid cell count + far-clip at 0x80136DC0 context per dd, from buildVisibleTerrainGridAroundCamera.
- Positive control: d1 pool length must appear (min ~77). If no lines, DLPOOLLOG did not arm: check funcs_3.c patch is built.
