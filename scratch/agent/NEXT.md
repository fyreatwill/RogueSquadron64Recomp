# NEXT: fold s6080_g4_l9, s6081_g4_l2b/l3b, s6082_g4_l10/l5b (G4 stall hunt)
HYPOTHESIS-ID: g4-stall-hunt
Read SOAK-RESULTS tail plus scratch/agent/m6/g1_lvl*/summary (crashlines, vi_stalls30s, alive_at_end). Any failure: lldb backtrace, name writer, fix root cause. If all clean (n>=2 for l2/l3), take G5 renaming sweep (check `grep -n '^## Session ' PORTING-STATE.md | tail -15` first) or G3 render fidelity.
