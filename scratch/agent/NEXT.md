# NEXT: G1c - fold s6047_dd2lw (lldb write-watch on tbl, address = x0+0x136DC4)
HYPOTHESIS-ID: g1c-draw-distance
Read scratch/agent/m6/s6047_dd2lw/lldb.log. Control: watchpoint stops at table swaps must appear (nonzero count). Then a stop whose new word is 0 -> bt names the writer: fix root cause. No stops at all -> check that the first breakpoint hit and x0 printed; if the watch is on a wrong convention, read MEM_HU macro in the recomp headers.
