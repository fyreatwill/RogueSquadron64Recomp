# NEXT (s7759)
HYPOTHESIS-ID: rdp-output-gate-hangar-reentry
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7758 closed stand-in flight coverage (L10 21:9: 24/24 flight tasks exact, gate GREEN 15/15). Remaining unscored route: the hangar
AFTER a mission abort (the G5i re-entry path, s6995), where the owner once saw a different camera. The s7756 H-state visibility
property (live == end render within 1 LSB) is gated only on FIRST-entry hangar tasks.
Unit (one game run, screen unlocked, host idle): find the s6995 abort/re-entry recipe (`grep -n 'Session 6995' PORTING-STATE.md`,
its autopilot key string), add ROGUESQ_S7751_EVERY=<N>:<max>:<from serial past the abort> so snaps land in the re-entry hangar
(verify from the window sheet + snap vi, s7758 pitfall), at the owner 21:9 recipe (ASPECT=21:9 DD=4 FPS60 STANDINS=1).
Then `python3 tools/s7757_route_replay.py <snapdir>` and `python3 tools/s7755_hstate_visibility.py <snap> --cap 1048576 --tg 1` per
re-entry hangar pair.
Hypotheses: H-same (re-entry hangar tasks are H-state like first entry and live-vs-end ge2LSB 0: add a pair to s7756 PAIRS) /
H-reentry-race (live-vs-end ge2LSB > 0 on re-entry only: a visible mid-task DL rewrite; name the writer) / H-exact (re-entry tasks
replay byte-exact from begin: the craft DL is no longer rewritten mid-task; note why).
Max 2 CPU-heavy jobs.
