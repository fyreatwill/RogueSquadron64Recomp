# NEXT (s7884)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 12 missions render-exact on det-tick flight frames (b17, m12, m6, m11, m3, m8, m4 pre-fork, m5, m1, m2, m7, m9 pre-fork s7883).
Unit: hand row 9 (mission 10, s7853 H-exact 5076 ticks) with the matched schedule + render oracle, screen unlocked, ~40 min:
  `env APM=1 RBIN=1 zsh tools/s7849_det_pair.sh 9 scratch/s7884/v9`
  then `python3 tools/s7880_press_scene.py scratch/s7884/v9/r1/oracle.log scratch/s7884/v9/p1/run.log`,
  `python3 tools/s7856_det_verdict.py scratch/s7884/v9/score.txt --tag 0x31=9` (check its flags),
  and `python3 tools/s7868_det_frame_cmp.py scratch/s7884/v9/r1/retail.bin scratch/s7884/v9/p1.bin --neg scratch/s7884/v9/p2.bin --plant`.
  Rescore row 9 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins after scoring.
Outcomes: H-exact + render rc 0 -> 13 missions; FORK -> classify (song end = audio-clock; else record the window);
render rc 1 -> list flight diffs (H-render: port defect, owner-relevant).
Watch: s7883 port presses ran +10 VI late (s7880-2: 0/-1). If row 9 shows a pre-flight tick fork, try the press_scene
suggested shift before calling it a defect.
Then 12+ / bonus 16, 18 (rows still hand: 2, 5, 7, 9).
Parked: g3-cinematic-half-frame-phase (s7874 table).
