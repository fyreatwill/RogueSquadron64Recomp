# NEXT (s7677)
HYPOTHESIS-ID: g6c-standin-ghost-widen

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
SOAK-RESULTS lines for s7676_ghost_L2 / s7676_ghost_L5.
Unit: fold the widening depth probe. s7676 closed the L4/L1 ghost as H-gate (walkers draw only inside ~51 units, same depth band as
every subtype; the never-drawn walker stayed >= 62.2 units away).
Score: `python3 tools/s7675_ghost_score.py --selftest && python3 tools/s7675_ghost_score.py scratch/s7676_L2/log_x2.txt scratch/s7676_L5/log_x5.txt`
- rc 0 (only GATE/UNHELD/NOREF rows): H-gate holds on 4 levels; nothing to do, ghost thread stays closed.
- rc 1 (a GHOST row: held stand-in came within the subtype's max first-call depth and the real object never drew): H-hide for that
  subtype. Fix in rs64_standins.cpp: release the hold for a stand-in with real_call < 0 once its held depth is below the subtype's
  first-call depth; re-run scratch/s7672/run.zsh on that level (held blinks stay 0 for objects that do draw, no GHOST rows).
If the soaks voided and the host is idle (HID idle > 300 s, screen unlocked), run in-session: `zsh scratch/agent/soak_queue/s7676_ghost_L2.sh`.
If both fold clean: every ladder rung is closed or owner-gated (CURRENT-TRUTH Next steps 2-9, 20, 22) — take the M6 endurance
item 3b (title->mission keyed hold, log every CRASH/stall) as the next datum-producing unit rather than writing BLOCKED.
One game at a time, SIGKILL only, never touch build/saves, <=2 CPU-heavy jobs, no repeat-hold soaks.
