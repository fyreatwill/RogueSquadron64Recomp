# NEXT: read s5708_lvl{1,4,6,7} rows in SOAK-RESULTS.md + scratch/agent/m6/s5708_lvlN/summary. Control: `[lvsel] init a1(cursorMask)` == 1<<N and `[lvinit] initMission gCurLevel=N`.
Any crashlines>0 / vi_stalls30s>0 / alive_at_end=0: capture a backtrace (lldb or ASan arm), name the writer, fix root cause.
Also: view a few frames from scratch/agent/m6/s5706_mask3/fbd and s5706_mask5/fbd to check lvl3/5 render as distinct, correct missions.
HYPOTHESIS-ID: g1-level-select
