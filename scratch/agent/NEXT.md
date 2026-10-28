# NEXT: G1c phase 2 - lift the 2048-cell footprint cap, test on a bigger level
HYPOTHESIS-ID: g1c-dd-phase2
State: s6548: lvl1 terrain is 64x64, dd4 already covers it; cap=2048 at 0x80130C4C trims mid-map windows (dd6 z 64->35).
Work unit: env ROGUESQ_DD_CAP=<n> overriding cap in tools/apply_s6037_ddclamp.py (and check the pool that cap sizes, writer of 0x80130C4C); find a level with terrain dims >64 (log tw/th per level via ROGUESQ_DD_LOG) and run dd4 with cap 2048 vs 8192 pinned, compare terrain fraction. Positive control: post window area rises with cap.
Then G3c(b)/(c).
