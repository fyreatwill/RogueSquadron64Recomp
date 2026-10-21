# NEXT: validate the ALT_HOLD fix, then G1 mission progression with real input

s5783 showed the terrain-ceiling deaths are our own stick-up input (see CURRENT-TRUTH). Work unit: run scratch/agent/s5777_althold.sh once with the rebuilt binary (target no longer latches at pre-spawn y==0).
- H-fix-holds: `[althold] target y=<nonzero>` then err stays within db, 0 deaths over HOLD -> fix validated; then take G1: reach mission end from real input (not ROGUESQ_MISSION_WIN) and log win/advance.
- H-still-climbs: target still bogus or deaths recur -> the hold itself is wrong (stick_y sign / ship y field); drop ALT_HOLD, use no-input flight (s5783_noalt.sh, 0 deaths) as the endurance baseline.
Control: `[althold] target` line with nonzero y; compare acted counts with s5777 (58/60).
Separate open item: the idle-autopilot LOSE at ~+342 s (s5627, 2 of 7 runs) is unexplained.
HYPOTHESIS-ID: g1-mission-progression
