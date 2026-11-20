# NEXT (s7692)
HYPOTHESIS-ID: g6c-standins-rehold-s7691

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7691 refreshed the G6c owner sheet on the parity-fixed binary (docs/owner_sheet_s7691_standins_on_off.jpg); G6c now waits on
the owner's look. Work unit: fold the queued re-holds s7691_standins_rehold_L1/L4/L5/L10/L12/L15 (STANDINS=1 dd4 owner recipe,
300 s) from SOAK-RESULTS.md: per level alive_at_end=1, crashlines=0, vi_stalls30s=0, max_gap vs s7629/s7630 (142-162 ms),
standins_on_line=1, spawns>0. If any did not run yet (idle-gated), run them in-session one at a time (screen unlocked, idle).
Outcomes: all clean -> the handover/parity code adds no crash/stall risk in owner mode (record in CURRENT-TRUTH G6c line);
any crash/stall -> backtrace it (lldb), name the writer, fix the root cause; STANDINS=0 same-level arm as control.
After that: no engineering rung open (all G-items owner-judged); take the next ladder item per ITERATION.md 3c.
One game at a time, SIGKILL only, <=2 CPU-heavy jobs.
