# NEXT: G1c - name the bad NPC pointer in px4_dd2 crash, then get px4 frames
HYPOTHESIS-ID: g1c-draw-distance
s6060: px4_dd2 crashes 5/5 in allocateAndInitCraftNpcContext (x1=0x8006bd80, si_addr 0x380000080), stack via updateActiveGridCellState -> setupNpcUpdateFunctions -> spawnNpcOfType. Logs: scratch/agent/m6/g1_lvl1g1cpx4_dd2/fail_att*.log.
Hypotheses: (A) NPC spawn table/record read for a grid cell outside the retail active window (dd2 widens it) -> garbage pointer; (B) poolx x4 malloc (1600*0x18) shifts heap so a neighbouring allocation overlaps; (C) pre-existing latent NPC bug now reachable.
Discriminator, one run: lldb/breakpoint (or a log in the fixup) on spawnNpcOfType args + cell index at crash, in arms px4_dd2 vs px1_dd2 vs px4_dd1 (same recipe). Crash in px4_dd1 -> B; only dd2 -> A.
Then: gate NPC spawn to retail-window cells (ORIGIN: writer named) and re-run px4_dd2 with `python3 tools/g1c_ddtog_fold.py scratch/agent/m6/g1_lvl1g1cpx4_dd2 4500 --hud`.
