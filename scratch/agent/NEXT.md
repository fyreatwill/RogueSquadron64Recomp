# Next work unit: read s5452_plume_lldb_title20 verdict (scratch/agent/soak_results/s5452_plume_lldb_title20/summary).
HYPOTHESIS-ID: m6-mission-transition-endurance
- control=PASS and a STOP in some run: read that run's bt, name the writer, fix the root cause.
- control=PASS and 20 clean boots: plume guard (s5446) holds; move to an M3 idiom-class audit.
- control=FAIL: lldb is unusable here; replace with a 20-boot loop using the in-process crash handler backtrace.
