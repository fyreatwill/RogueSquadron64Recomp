# NEXT: G1c - fold s6036_dd1/2/3 soaks
HYPOTHESIS-ID: g1c-draw-distance
Read scratch/agent/m6/g1_lvl1g1cdd{1,2,3}/run.log: grep [dd]/[gridlog]. H-A: window w/req scales with m (dd2 w ~2x dd1 at comparable pose) and distant terrain fraction rises (compare captured framebuffers). H-B: window unchanged => another clamp downstream. Check w<=64 at dd3, crashes, frame time (G1b instrument). Then steps 1.5x/2x on levels 5 and 10 for 300 s holds.
