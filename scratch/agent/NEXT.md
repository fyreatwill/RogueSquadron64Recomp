# NEXT: fold s6579 true-dd4 soak verdicts (lvl5, lvl10; queued)
HYPOTHESIS-ID: g1c-dd-phase2
Finding s6579: "multiplier 3" at ROGUESQ_DRAW_DISTANCE=4 is the s6446 cap (dd>3 -> 3 unless ROGUESQ_DD_UNSAFE=1), apply_s6036_dd.py:7. So all prior "dd4 bundle" holds incl. s6578 ran dd3.
Work unit: read SOAK-RESULTS s6579_dd4_unsafe_lvl5/10; confirm "multiplier 4" in logs; pass = 0 crash/0 stall. If a fault, backtrace it. Then lvl1 300 s dd4, and decide whether to lift the cap (retire DD_UNSAFE).
