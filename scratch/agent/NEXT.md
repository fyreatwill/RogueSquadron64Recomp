# NEXT (s7952)
HYPOTHESIS-ID: run-dir-case-collision
s7951: case-only TAG collisions (macOS case-insensitive fs) now refused in scratch/agent/m6_god_common.sh via tools/agent/run_dir_guard.sh.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold any new SOAK-RESULTS lines (a verdict with run_dir_collision= is the guard firing: rename that TAG).
1. Close the class: enumerate every OTHER launcher that makes a run dir from a caller-chosen name (grep `mkdir -p` + `$TAG|$ARM|$OUTDIR|$N`
   in tools/*.sh tools/*.zsh scratch/agent/*.sh, incl. tools/g3_port_capture.sh OUTDIR and tools/s7*_arm.zsh scratch/sNNNN/<arm>).
   Classify each: routes through m6_god_common (covered) / fixed literal names (safe) / caller name (wire run_dir_guard.sh).
   Census scratch/sNNNN/* arm dirs for case-only siblings the same way (dir name vs any tag= in its files). Guard every caller-name site; planted control per new wiring.
2. If the class is closed with nothing left: ladder 3c's first non-closed rung not needing the owner, or an M3 idiom-class audit (BLOCKED not allowed, 3c).
