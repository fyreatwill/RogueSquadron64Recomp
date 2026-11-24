# NEXT (s7883)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 11 missions render-exact on det-tick flight frames (b17, m12, m6, m11, m3, m8, m4 pre-fork, m5, m1, m2, m7 s7882).
Unit: hand row 8 (mission 9, s7852 FORK audio-clock at song 03 end t3527/t3526) with the matched schedule + render oracle, screen
unlocked, ~40 min:
  `env APM=1 RBIN=1 zsh tools/s7849_det_pair.sh 8 scratch/s7883/v8`
  then `python3 tools/s7880_press_scene.py scratch/s7883/v8/r1/oracle.log scratch/s7883/v8/p1/run.log`,
  `python3 tools/s7856_det_verdict.py scratch/s7883/v8/score.txt --tag 0x31=8 --fork-class audio-clock` (check its flags),
  and `python3 tools/s7868_det_frame_cmp.py scratch/s7883/v8/r1/retail.bin scratch/s7883/v8/p1.bin --neg scratch/s7883/v8/p2.bin --plant`;
  if the fork moves the pairing offset mid-flight, re-run with `--port-end <port frame of the fork tick>` (the s7877 0x31=3 recipe).
  Rescore row 8 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins after scoring.
Outcomes: FORK audio-clock at the same tick + render rc 0 pre-fork -> 12 missions; H-exact -> fork was schedule-borne (record why);
render rc 1 -> list flight diffs (H-render: port defect, owner-relevant).
Then rows 9, then 12+ / bonus 16, 18. Note: post-flight non-exact 3598 after the paired blank is the known end-screen class (s7876, s7882).
Parked: g3-cinematic-half-frame-phase (s7874 table).
