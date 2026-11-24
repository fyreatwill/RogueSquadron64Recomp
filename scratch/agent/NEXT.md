# NEXT (s7878)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 7 missions render-exact on det-tick flight frames (b17, m12, m6, m11, m3, m8, m4 pre-fork; s7877). Mission 4 (0x31=3,
Corellia) forks audio-clock at the respawn t2313; tools/s7868_det_frame_cmp.py --port-end N scores a pre-fork prefix.
Unit: 0x31=4 (mission 5, Liberation of Gerrard V = the G5a crash mission):
`env RBIN=1 zsh tools/s7849_det_pair.sh 4 scratch/s7878/v4` (screen unlocked; ~25 min), then
`python3 -I tools/s7856_det_verdict.py scratch/s7878/v4/score.txt --tag 0x31=4` and
`python3 tools/s7868_det_frame_cmp.py scratch/s7878/v4/r1/retail.bin scratch/s7878/v4/p1.bin --plant --neg scratch/s7878/v4/p2.bin`.
Outcomes: rc 0 + plant + neg PASS -> 8 missions, then 0x31=0 (mission 1). FORK -> find the fork frame (offset votes split, as
s7877: -529/-528) and rerun with --port-end <phase-7 start + fork tick>; exact prefix = covered. rc 1 inside a det-exact window
-> real render defect: localise with tools/s7869_island_probe.py. Neg FAIL with nonzero p2 diffs = weak control (record it);
neg with 0 p2 diffs = no control, the result does not count. Check the sweep-table row for 0x31=4 (s7840 hand row, 170 s?)
against the 305 s run. Delete bins after.
Parked: g3-cinematic-half-frame-phase (s7874 table).
