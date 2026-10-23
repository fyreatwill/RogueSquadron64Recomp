# NEXT: G1c - fold s6045_dd2lw (lldb write-watch on tbl 0x80136DC4, run by loop)
HYPOTHESIS-ID: g1c-draw-distance
Read scratch/agent/m6/s6045_dd2lw/lldb.log. Positive control: watchpoint stops at the call=129/783 table swaps must appear. Then: a stop whose new word is 0 -> its bt names the writer: fix root cause. No zero-write but SIGBUS -> re-derive x21 origin from disasm of streamTerrainGridCellsByDistance+10880 (tools/agent/disasm_at.py). If lldb never attached/no stops, the soak harness failed: check common.log.
