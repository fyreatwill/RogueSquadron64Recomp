# NEXT: fold s6080_g4_l7..l9 and s6081_g4_l2b/l3b (G4 stall hunt)
HYPOTHESIS-ID: g4-stall-hunt
Read SOAK-RESULTS tail plus scratch/agent/m6/g1_lvl*s608*g4*/summary and run.log CRASH/abort greps. Any failure: lldb backtrace, name writer, fix root cause. If all clean (n>=2 for l2/l3), G5 renaming sweep (check `grep -n '^## Session ' PORTING-STATE.md | tail -15` first).
