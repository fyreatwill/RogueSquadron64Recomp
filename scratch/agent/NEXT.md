# NEXT: G1c - fold s6039_dd2q [corrected cellprobe]
HYPOTHESIS-ID: g1c-draw-distance
grep -a cellprobe scratch/agent/m6/g1_lvl1g1cdd2q/run.log. t0w=<w0 w1 w2 w3 w4> are the first 5 words of struct 0x80136DC0; tbl is its +4. (a) tbl==0 => find writer of 0x80136DC4 (lldb watch / grep sw via struct base), compare with dd1 run (tbl must be nonzero there: add always-on first-call print if needed); (b) tbl valid => idx*30 overrun, fix scaled-window index math. dd15p NaN in vec3Cross still open. Then requeue /tmp/s6037_dd3c.sh.
