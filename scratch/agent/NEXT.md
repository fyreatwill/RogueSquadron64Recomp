# Next work unit: read s5453_plume_lldb_attach10 verdict (scratch/agent/soak_results/s5453_plume_lldb_attach10/summary).
HYPOTHESIS-ID: m6-mission-transition-endurance
- control=FAIL: attach did not catch injected SIGSEGV -> fall back to an in-process crash-handler backtrace loop (10 title boots).
- control=PASS and a STOP in some run: read runN.lldb bt, name the writer, fix the root cause.
- control=PASS and 10 clean boots (titles>=8): plume guard (s5446) holds; move to an M3 idiom-class audit.
- (s5452 lldb LAUNCH results are a tooling null: getcwd EPERM before main.)
