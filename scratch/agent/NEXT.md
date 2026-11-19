# NEXT (s7667)
HYPOTHESIS-ID: owner-wait-standing

s7666 proved the G6b panel Save -> controls.json -> reload round trip (scratch/s7666/run.zsh, 4 arms).
At session start run `python3 tools/crash_reports.py --since 2026-11-13`: a NEW report nobody planted is a real crash and
outranks everything (G4 reopens: backtrace from the .ips, name the writer, fix the root cause).
Otherwise: an owner report first; else look for another owner-facing path that no test has exercised end to end (as s7666
found Save), e.g. a --preset/settings.txt + controls.json combination, or F6 panel open/close during a mission load.
Do NOT do census-gate housekeeping or repeat-hold soaks (G4 parked). Rules: never touch build/saves; one game at a time;
SIGKILL only; at most 2 CPU-heavy jobs; host on battery (44%) at s7666, so keep game runs short or queue them as soaks.
