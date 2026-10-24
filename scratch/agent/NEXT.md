# NEXT: fold s6084_g3b_cull_l2, then name the writer of pinned-Y spike tris
HYPOTHESIS-ID: g3b-spike-lines
Fold: grep -a 'culled=' scratch/agent/m6/g1_lvl2s6084g3bcull/run.log | tail -1 (>0 = control), crashlines=0 in SOAK-RESULTS, remaining [spike] count should equal culled (scan precedes cull).
Then: for swap-1867-style tris (Y pinned -170.25 / -224.25), dump the RSP vertex inputs (w<=0 / behind eye?) and bisect against docs/F5-UCODE-REFERENCE.md clip path to name the writer (H-rsp vs game-submitted). If it matches ucode clamp behaviour of real hardware => H-retail, keep cull opt-in only.
Then G1c phase 2 per ITERATION.md.
