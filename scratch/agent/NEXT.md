# NEXT (s7666)
HYPOTHESIS-ID: owner-wait-standing

s7665 closed the last open DIAG crash datum (s7523 consume(), H-devbuild; tools/test_s7523_model.sh).
At session start run `python3 tools/crash_reports.py --since 2026-11-13`: a NEW report that nobody planted is a real crash
and outranks everything (G4 reopens on it: backtrace from the .ips, name the writer, fix the root cause).
Otherwise: if the owner has reported anything, take that first; else the first open 3c rung per CURRENT-TRUTH Next steps.
Do NOT do another census-gate housekeeping pass or repeat-hold soaks (G4 parked). Rules: never touch build/saves; one game at
a time; SIGKILL only; at most 2 CPU-heavy jobs; host was on battery (46%) at s7665, so queue game runs as soaks if still unplugged.
