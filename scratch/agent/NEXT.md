# NEXT (s7668)
HYPOTHESIS-ID: owner-wait-standing

s7667 fixed relative ROGUESQ_CONTROLS in settings files (scratch/s7667/run.zsh, 3 arms pre/post).
At session start run `python3 tools/crash_reports.py --since 2026-11-13`: a NEW report nobody planted is a real crash and
outranks everything (G4 reopens: backtrace from the .ips, name the writer, fix the root cause).
Otherwise: an owner report first; else another owner-facing path no test has exercised end to end, e.g. F6 panel open/close
while a mission loads (ROGUESQ_BIND_PANEL_TEST driving open during the level-select -> mission transition, 0 crash, input
restored after close), or `--preset tv` fullscreen toggling (Cmd+Ctrl+F) then F6 panel layout at the new size.
Do NOT do census-gate housekeeping or repeat-hold soaks (G4 parked). Rules: never touch build/saves; one game at a time;
SIGKILL only; at most 2 CPU-heavy jobs.
