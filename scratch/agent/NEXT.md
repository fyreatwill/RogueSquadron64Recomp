Single next work unit (s5594): fold s5592_m6_long_i and s5593_m6_long_j (loop runs them; do NOT run the game).
Commands: grep -n "s5592_m6_long_i\|s5593" scratch/agent/SOAK-RESULTS.md ; check vi_stalls30s/crashlines in logs.
Outcomes: any CRASH/stall -> lldb backtrace, name writer, root-cause fix. All clean -> pivot to second-mission route (investigate how to advance past mission-end title fall-back) or ASan arm.
HYPOTHESIS-ID: m6-mission-endurance
