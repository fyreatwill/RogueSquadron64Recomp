# NEXT: fold s5708_lvl{6,7} rows from SOAK-RESULTS.md + scratch/agent/m6/s5708_lvlN/summary. Control: `[lvsel] init a1(cursorMask)` == 1<<N and `[lvinit] initMission gCurLevel=N`.
Also: lvl4 last frame (scratch/agent/m6/s5708_lvl4/fbd) is hangar-like, not flight; step through its fbd frames to see whether it entered flight and returned, or never left briefing.
Any crashlines>0 / vi_stalls30s>0 / alive_at_end=0: capture a backtrace, name the writer, fix root cause.
HYPOTHESIS-ID: g1-level-select
