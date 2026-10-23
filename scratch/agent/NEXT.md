# NEXT: G1c - fold [gridlog] arms (s6034_g1c_ret/posab/cell2, plus near4)
HYPOTHESIS-ID: g1c-draw-distance
grep '\[gridlog\]' in scratch/agent/soak_results/s6034_g1c_*.log. Control: posab must show smaller kept / d2 max than ret (else instrument void).
Outcomes: kept==cap(0x80130C4C) => H-budget: add knob raising cap AND the pool alloc (find rs_malloc for *0x80136E1C), arm 1.5x/2x/3x. kept<cap with gx/gz at terrain bounds (terr=WxH) => H-data: close G1c, ask owner. kept<cap, window<terr => find writer of 0x80132DB4/BC (window size) and scale it.
Then ROGUESQ_DRAW_DISTANCE opt-in knob per ITERATION.md G1c.
