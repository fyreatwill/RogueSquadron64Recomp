# NEXT: find what the CAPX=2 fault at lvl7 dd4 dereferences (H-table64 vs H-other)
HYPOTHESIS-ID: g1c-dd-phase2
State (s6587): 8 MB DL pool does not help; 4/4 crash far=0x380000022 with only 256 chunks allocated. Pool refuted.
Work unit: disassemble/read the guest function at guest pc 0x800547bc (fault store/load, a NULL list node = 0x80000000 + 0x22) and its caller; identify which table/array the node comes from and its element count (is it 64-wide / retail-sized?). Hypotheses: H-table64 (array indexed by cell row/col past its bound), H-other (node list head never built for out-of-original-footprint cells).
Discriminator: log, in one build, the index and table base at the fault site for CAPX=1 (clean) vs CAPX=2 windows within one run (s6587_run.sh toggles CAPX every 60 s). Index beyond table length only in the 2x window => H-table64.
Outcome: if confirmed, either clamp window to that table length for lvl3/7 (no gain beyond dd4) or enlarge it; if not, close lvl3/7 dd>4 as not worth it and move to G3/owner items.
