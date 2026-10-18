# Next work unit: fold m6_lldb_a/b/c soak verdicts (s5455 harness) - read backtraces at stall/crash, name the writer.
HYPOTHESIS-ID: m6-mission-transition-endurance
- Files: scratch/agent/m6/s5455_lldb_{a,b,c}/{keys.log,summary,lldb_att*.log}; SOAK-RESULTS.md tail.
- keys.log "lldb interrupted at stall" + lldb_att log with `thread backtrace all` => stall located; investigate the blocked thread's wait.
- "stop reason" SIGSEGV in lldb log => crash bt; name the writer, fix root cause.
- No stall/crash in 3 runs => lengthen hold / vary LATE; if stall with no bt, fix interrupt path (lldb -b may exit on SIGINT).
