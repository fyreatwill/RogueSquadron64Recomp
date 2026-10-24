# NEXT: fold s6079_g4_l4 and s6080_g4_l6..l9 (G4 stall hunt)
HYPOTHESIS-ID: g4-stall-hunt
Read SOAK-RESULTS tail plus scratch/agent/m6/g1_lvl*s608*g4*/summary (vi_stalls30s, crashlines, alive_at_end) and run.log CRASH/abort greps. Any failure: lldb backtrace, name writer, fix root cause. If all clean, repeat L2/L3 once more (n>=2 each), then G5 renaming sweep (check session titles first).
