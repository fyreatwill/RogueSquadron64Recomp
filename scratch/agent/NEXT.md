# NEXT: G1c - fold s6021_g1c_r2A / r3A (tags g1_lvl1g1cr2A / r3A)
HYPOTHESIS-ID: g1c-draw-distance
Finding s6021: 0x9DEAC (=14.5) is the live footprint scalar (posAB -31% tri vs retail, posB 0x9DEB0-only inert).
Bin: cd scratch/agent/m6; grep -a '\[g1c\] state=\|\[tricnt\]' g1_lvl1g1cr2A/run.log | awk by state, tasks with tri>=50 only (same awk as s6021 ledger).
Pass (scaled tri > retail by >10%) -> L-radius: take fb-dump distant-terrain fraction, check frame time (G1b instrument), then 1.5x/2x/3x + ROGUESQ_DRAW_DISTANCE wrapper. Flat -> L-budget or clamp elsewhere; try 0x80130C50 FOV scale / LOD table 0x9ECB0.
