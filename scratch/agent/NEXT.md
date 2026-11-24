# NEXT (s7885)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 13 missions render-exact on det-tick flight frames (m1-m12 and b17; s7884 added m10).
Not yet render-scored: m13 (0x31=12), m14 (13), m15 (14, audio-clock fork), m16 (15), bonus b16, b18.
Unit: row 12 (mission 13, s7856 H-exact) with the matched schedule + render oracle, screen unlocked, ~40 min:
  `env APM=1 RBIN=1 zsh tools/s7849_det_pair.sh 12 scratch/s7885/v12`
  then `python3 tools/s7880_press_scene.py scratch/s7885/v12/r1/oracle.log scratch/s7885/v12/p1/run.log`,
  `python3 tools/s7856_det_verdict.py scratch/s7885/v12/score.txt --tag 0x31=12` (check its flags),
  and `python3 tools/s7868_det_frame_cmp.py scratch/s7885/v12/r1/retail.bin scratch/s7885/v12/p1.bin --neg scratch/s7885/v12/p2.bin --plant > scratch/s7885/v12/render.txt`
  (grep -v '^    N' it; the summary lines are the 'pair:' / 'control' ones).
  Rescore row 12 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins after scoring.
Outcomes: H-exact + render rc 0 -> 14 missions; FORK -> classify (song end = audio-clock; else record the window, use --port-end);
render flight non-exact -> list flight diffs (H-render: port defect, owner-relevant).
Watch: port press offset drifts by run (0, -1, +10, +18 VI). If a row shows a pre-flight tick fork, try the press_scene
suggested shift before calling it a defect.
Parked: g3-cinematic-half-frame-phase (s7874 table).
