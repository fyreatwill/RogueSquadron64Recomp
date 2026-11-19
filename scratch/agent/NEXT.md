# NEXT (s7676)
HYPOTHESIS-ID: g6c-standin-ghost

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
SOAK-RESULTS lines for s7675_ghost_L4 / s7675_ghost_L1.
Unit: fold the walker depth probe. s7675 showed the L4 "ghost" (item 80547410, AT-PT sub 0x47) is a live walker (slot allocated,
hp 80) that never drew. Walkers (0x47 L4, 0x1F L1) first call the bucket 122-541 frames after spawn, or never; all other subtypes 0-13.
Score: `python3 tools/s7675_ghost_score.py scratch/s7675_L4/log_x4.txt scratch/s7675_L1/log_x1.txt`
- H-gate (every never-case GATE: held_dmin > the subtype's max first-call depth): walker handlers draw only inside their own
  distance, and the stand-in correctly bridges. Close the ghost thread with no code change.
- H-hide (any GHOST: the held stand-in came within first-call depth and the walker still never drew): the walker is held hidden by
  script. Fix: in rs64_standins.cpp, stop the hold for a stand-in with real_call < 0 once its held depth drops below the subtype's
  first-call depth (or simpler: walkers 0x0F/0x1F/0x47 with no real call by spawn+30 release the hold). Re-run
  scratch/s7672/run.zsh on L4 and L1: held blinks stay 0 for walkers that do draw, and no GHOST rows remain.
If the soaks voided again and the host is idle (HID idle > 300 s, screen unlocked), run them in-session: `zsh scratch/agent/soak_queue/s7675_ghost_L4.sh`.
Control: the ordinary subtypes' first-call depth (33-50 units at dd4) printed by the scorer must be present.
One game at a time, SIGKILL only, never touch build/saves, <=2 CPU-heavy jobs, no repeat-hold soaks.
