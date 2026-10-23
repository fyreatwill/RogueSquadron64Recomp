# NEXT: G1c - fold s6040_dd2r / s6040_dd3r (rewritten count-based ddclamp + pool-cap bound)
HYPOTHESIS-ID: g1c-draw-distance
Check SOAK-RESULTS rc and grep -a 'cellprobe\|CRASH' scratch/agent/m6/g1_lvl1g1cdd2r/run.log. (a) rc=0 for dd2r => clamp was the bug; run levels 5 and 10 at 2x, record frame time vs G1b baseline. (b) still tbl==0 => lldb watch on 0x80136DC4 writer (guest->host addr), compare to dd1. dd15p vec3Cross NaN still open.
