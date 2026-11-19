# NEXT (s7669)
HYPOTHESIS-ID: owner-wait-standing

s7668 proved the F6 panel survives a mission load + fullscreen toggle while open and fixed a stale-size squash (scratch/s7668).
At session start run `python3 tools/crash_reports.py --since 2026-11-13`: a NEW report nobody planted is a real crash and
outranks everything (G4 reopens: backtrace from the .ips, name the writer, fix the root cause).
Otherwise: an owner report first; else another owner-facing path no test has exercised end to end, e.g.
- F6 panel at a window resize (ROGUESQ_WIN_TEST_RESIZE_S to a 21:9-class size like 1512x648 with ROGUESQ_ASPECT=auto) while open:
  check `[controls-panel] stale` fires and draws resume at the right size; or
- the rumble path across a mission abort -> hangar -> restart (motor stopped at abort, no stuck rumble: [rumble] duty 0 after abort).
Hypotheses + discriminator in the session entry; same-run control arm; use tools/g1e_owner_quiet_arms.zsh arms (one game at a time).
Do NOT do census-gate housekeeping or repeat-hold soaks (G4 parked). Rules: never touch build/saves; SIGKILL only; <=2 CPU-heavy jobs.
