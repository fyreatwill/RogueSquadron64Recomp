# NEXT: fold s6079_g4_l{2,3,4} (G4 stall hunt), then G5 or further G4
HYPOTHESIS-ID: g4-stall-hunt
G1c is closed pending owner look (docs/DRAW-DISTANCE.md). Fold SOAK-RESULTS lines for s6079_g4_l2/3/4: any rc!=0 other than 137-at-600s, any CRASH/abort, any VI stall >30 s in scratch/agent/m6/g1_lvl{2,3,4}s6079g4*/run.log. Each distinct failure: lldb backtrace, name the writer, fix root cause. If all clean, queue levels 6-9 the same way; else G5 renaming sweep (check session titles first).
