# NEXT (s7881)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 9 missions render-exact on det-tick flight frames (b17, m12, m6, m11, m3, m8, m4 pre-fork, m5, m1 first 2895 frames).
s7880: the default port AP schedule is 1 Start press short vs retail (H-sched); `APM=1` gives the retail-matched schedule.
Mission 1 is now H-exact on all 5556 ticks (scratch/s7880/v1, no RBIN).
Unit: next hand row 1 (mission 2) with the matched schedule and the render oracle, screen unlocked, ~40 min:
  `env APM=1 RBIN=1 zsh tools/s7849_det_pair.sh 1 scratch/s7881/v1`
  then `python3 tools/s7880_press_scene.py scratch/s7881/v1/r1/oracle.log scratch/s7881/v1/p1/run.log` (offsets must be within
  ~5 VI, lag 0), `python3 tools/s7856_det_verdict.py scratch/s7881/v1/score.txt --tag 0x31=1`, and
  `python3 tools/s7868_det_frame_cmp.py scratch/s7881/v1/r1/retail.bin scratch/s7881/v1/p1.bin --neg scratch/s7881/v1/p2.bin --plant`.
Outcomes: H-exact + render rc 0 -> 10 missions render-exact, rescore sweep row 1; FORK -> name the class (audio-clock?) with
s7852_fork_windows; render rc 1 -> list the flight diffs (H-render: port defect), owner-relevant.
Then row 2. Optional: mission 1 render over ticks 2901-5556 (`APM=1 RBIN=1 ... 0 scratch/s788x/v0`).
Parked: g3-cinematic-half-frame-phase (s7874 table).
