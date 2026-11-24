# NEXT (s7882)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 10 missions render-exact on det-tick flight frames (b17, m12, m6, m11, m3, m8, m4 pre-fork, m5, m1, m2 s7881).
Unit: hand row 6 (mission 7, s7847, never render-scored) with the matched schedule + render oracle, screen unlocked, ~40 min:
  `env APM=1 RBIN=1 zsh tools/s7849_det_pair.sh 6 scratch/s7882/v6`
  then `python3 tools/s7880_press_scene.py scratch/s7882/v6/r1/oracle.log scratch/s7882/v6/p1/run.log` (offsets within ~5 VI,
  lag 0), `python3 tools/s7856_det_verdict.py scratch/s7882/v6/score.txt --tag 0x31=6`, and
  `python3 tools/s7868_det_frame_cmp.py scratch/s7882/v6/r1/retail.bin scratch/s7882/v6/p1.bin --neg scratch/s7882/v6/p2.bin --plant`.
  Rescore row 6 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins after scoring.
Outcomes: H-exact + render rc 0 -> 11 missions; FORK -> name the class with s7852_fork_windows; render rc 1 -> list the
flight diffs (H-render: port defect, owner-relevant).
Then rows 8 (FORK audio-clock, score pre-fork), 9, then 12+ / bonus 16, 18.
Parked: g3-cinematic-half-frame-phase (s7874 table).
