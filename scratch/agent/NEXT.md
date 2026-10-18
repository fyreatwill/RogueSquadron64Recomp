# Next work unit: M6 mission endurance - reuse attach recipe on the mission route, or M3 idiom audit.
HYPOTHESIS-ID: m6-mission-transition-endurance
- s5453 result: lldb attach control PASS, 0/9 title-boot SIGSEGV (run 10 truncated by 600 s cap; lower N to 8 next time).
- Next: queue a 3-run keyed mission hold (>=10 min) with the lldb attach wrapper from soak_queue/done/s5453*.sh so the
  next rc=137 stall/crash (m6_res_late_*, m6_keyed_var_a precedents) yields a real backtrace instead of a watchdog kill.
- Expected: STOP with SIGSEGV -> read bt, name writer; stall -> `process interrupt` + `bt all` at stall time.
