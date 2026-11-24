# NEXT (s7879)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 8 missions render-exact on det-tick flight frames (b17, m12, m6, m11, m3, m8, m4 pre-fork, m5; s7878).
Unit: 0x31=0 (mission 1; sweep row is the s7831 hand row "pre seed-pin recipe"):
`env RBIN=1 zsh tools/s7849_det_pair.sh 0 scratch/s7879/v0` (screen unlocked; ~40 min wall), then
`python3 -I tools/s7856_det_verdict.py scratch/s7879/v0/score.txt --tag 0x31=0` and
`python3 tools/s7868_det_frame_cmp.py scratch/s7879/v0/r1/retail.bin scratch/s7879/v0/p1.bin --plant --neg scratch/s7879/v0/p2.bin`.
Outcomes: rc 0 + plant + neg PASS -> 9 missions; move sweep row 0 to the rescored score.txt (tools/s7862_det_sweep_table.py ROWS)
and go on to the next hand row (1 or 2, s7840). FORK -> find the fork tick and rerun the scorer with --port-end <phase-7 start + fork
tick> (s7877 recipe). rc 1 inside a det-exact window -> real render defect: localise with tools/s7869_island_probe.py.
Neg with 0 p2 diffs = no control, so the result does not count. Delete the bins after.
Parked: g3-cinematic-half-frame-phase (s7874 table).
