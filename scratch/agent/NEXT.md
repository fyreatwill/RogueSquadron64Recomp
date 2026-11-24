# NEXT (s7887)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 15 missions render-exact on det-tick flight frames (m1-m14 and b17; s7886 added m14).
Not yet render-scored: m15 (0x31=14, audio-clock fork s7857/s7858), m16 (15), bonus b16, b18.
Unit: row 14 (mission 15) with the matched schedule + render oracle, screen unlocked, ~25-40 min:
  `env APM=1 RBIN=1 zsh tools/s7849_det_pair.sh 14 scratch/s7887/v14`
  then `python3 tools/s7880_press_scene.py scratch/s7887/v14/r1/oracle.log scratch/s7887/v14/p1/run.log`,
  `python3 tools/s7856_det_verdict.py scratch/s7887/v14/score.txt --tag 0x31=14` (check its flags),
  and `python3 tools/s7868_det_frame_cmp.py scratch/s7887/v14/r1/retail.bin scratch/s7887/v14/p1.bin --neg scratch/s7887/v14/p2.bin --plant > scratch/s7887/v14/render.txt`
  (grep -v '^    N' it; the summary lines are the 'pair:' / 'control' ones). If the fork is mid-flight, the exact run
  should stop at the fork (as s7883); use --port-end only if it does not.
  Rescore row 14 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins after scoring.
Outcomes: FORK at a song end with VI/buffer parity -> audio-clock (as s7858), render pre-fork prefix exact -> 16 missions;
FORK elsewhere -> record the window; render flight non-exact before the fork -> H-render port defect (owner-relevant).
Watch: port press offset drifts by run (0, -1, +8, +10, +18 VI). If a row shows a pre-flight tick fork, try the press_scene
suggested shift before calling it a defect.
Parked: g3-cinematic-half-frame-phase (s7874 table).
