# NEXT (s7886)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 14 missions render-exact on det-tick flight frames (m1-m13 and b17; s7885 added m13).
Not yet render-scored: m14 (0x31=13), m15 (14, audio-clock fork), m16 (15), bonus b16, b18.
Unit: row 13 (mission 14, s7857 H-exact with residual timing-class: watch whether the render diff tracks it) with the matched schedule + render oracle, screen unlocked, ~40 min:
  `env APM=1 RBIN=1 zsh tools/s7849_det_pair.sh 13 scratch/s7886/v13`
  then `python3 tools/s7880_press_scene.py scratch/s7886/v13/r1/oracle.log scratch/s7886/v13/p1/run.log`,
  `python3 tools/s7856_det_verdict.py scratch/s7886/v13/score.txt --tag 0x31=13` (check its flags),
  and `python3 tools/s7868_det_frame_cmp.py scratch/s7886/v13/r1/retail.bin scratch/s7886/v13/p1.bin --neg scratch/s7886/v13/p2.bin --plant > scratch/s7886/v13/render.txt`
  (grep -v '^    N' it; the summary lines are the 'pair:' / 'control' ones).
  Rescore row 13 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins after scoring.
Outcomes: H-exact + render rc 0 -> 15 missions; FORK -> classify (song end = audio-clock; else record the window, use --port-end);
render flight non-exact -> list flight diffs (H-render: port defect, owner-relevant).
Watch: port press offset drifts by run (0, -1, +10, +18 VI). If a row shows a pre-flight tick fork, try the press_scene
suggested shift before calling it a defect.
Parked: g3-cinematic-half-frame-phase (s7874 table).
