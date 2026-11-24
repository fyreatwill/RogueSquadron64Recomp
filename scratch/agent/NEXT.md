# NEXT (s7888)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 16 missions render-exact on det-tick flight frames (m1-m15 and b17; s7887 added m15's pre-fork prefix).
Not yet render-scored: m16 (0x31=15, H-exact timing-class s7859), bonus b16 (race, s7860 race-safe schedule), b18 (s7862).
Unit: row 15 (mission 16) with the matched schedule + render oracle, screen unlocked, ~25-40 min:
  `env APM=1 RBIN=1 zsh tools/s7849_det_pair.sh 15 scratch/s7888/v15`
  then `python3 tools/s7880_press_scene.py scratch/s7888/v15/r1/oracle.log scratch/s7888/v15/p1/run.log`,
  `python3 tools/s7856_det_verdict.py scratch/s7888/v15/score.txt --tag 0x31=15` (check its flags),
  and `python3 tools/s7868_det_frame_cmp.py scratch/s7888/v15/r1/retail.bin scratch/s7888/v15/p1.bin --neg scratch/s7888/v15/p2.bin --plant > scratch/s7888/v15/render.txt`
  (grep -v '^    N' it; the summary lines are the 'pair:' / 'control' ones).
  Rescore row 15 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins after scoring.
Competing hypotheses / outcomes: H-exact ticks + render flight exact -> 17 missions; FORK at a song end with VI/buffer parity ->
audio-clock (render the pre-fork prefix); render flight non-exact on exact ticks -> H-render port defect (owner-relevant).
Watch: port press offset drifts by run (0, -1, +8, +10, +18 VI). If a row shows a pre-flight tick fork, try the press_scene
suggested shift before calling it a defect. The bonus rows need the s7860 race-safe schedule; check s7849_det_pair.sh handles b16.
Parked: g3-cinematic-half-frame-phase (s7874 table).
