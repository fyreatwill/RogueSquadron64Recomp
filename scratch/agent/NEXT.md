# NEXT (s7764)
HYPOTHESIS-ID: owner-report-triage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner answer to docs/OWNER-REVIEW-QUEUE.md
rows, then new SOAK-RESULTS lines after the s7750 fold. Any of those outranks the unit below (arm table, discriminator, root fix;
an owner "close" -> close that row in the queue + CURRENT-TRUTH).
s7763: all 11 queue commands verified by launch echo (tools/s7763_owner_cmd_check.py --control, rc 0). Do NOT add coverage units,
crash-hunt soaks (G4 parked) or repeat holds.
Unit if nothing arrived: the in-flight toggles in the queue that s7763 could not see at startup (row 1 RUMBLE=0 / RUMBLE_SCALE,
row 8 W_CLAMP=0, row 11 DD_FARMAX=0, row 15 HORIZON_SKYFILL=0, row 20 STICK_GATE=0, row 19 M5_B40_VALUE=1): H-works vs H-broken
per toggle = the toggle changes the thing the row says on a forced level (one forced-level flight per toggle pair, same-run
toggle where the var supports it, else on/off arms back to back, sequential, SIGKILL). Discriminator per toggle: its own log
counter or frame metric differs on vs off; positive control = the default arm shows the fix's counter firing. Batch all toggles
into as few launches as possible (several toggles in one arm where they touch disjoint subsystems).
