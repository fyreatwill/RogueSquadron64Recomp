# NEXT (s7890)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 18 missions render-exact on det-tick frames (m1-m16, b16 race s7889, b17). Last one not render-scored: bonus 18 (Hoth, s7862,
6444 ticks H-exact, no render). The BASE_EEP bonus save is now automatic for 0x31>=16 (s7889); do NOT edit s7849_det_pair.sh mid-run.
Unit: bonus 18 + render oracle, screen unlocked (`ioreg -n Root -d1 -a | grep -A1 IOConsoleLocked`), ~45 min. Retail PP = s7862's;
the AP is the s7862 PP mapped onto the APM=1 port times (boot 15.05, then PP+4.8), the s7889 rule that worked for b16:
  `env RBIN=1 PP_OVR=19.5:start,27.5:dright,29:dright,31.5:start,43.5:start,55.5:start,67.5:start AP_OVR=6:start,11:start,11.5:w1024,15.05:start,24.3:start,32.3:right,33.8:right,36.3:start,48.3:start,60.3:start,72.3:start zsh tools/s7849_det_pair.sh 16 scratch/s7890/v18`
  Retail must give seed 43308409 / 6444 ticks (else the pick is wrong: see s7861/s7862 cursor probes). If the port picks the
  wrong level (p1 seed != 43308409 at t0), fall back to s7862's AP_OVR=6,11,11.5:w1024,19.5,31.5,39.5:right,41:right,43.5,67.5,79.5:start
  (pass ":start" on each entry) on the same r1 (the driver reuses r1/oracle.log; delete p1/p2 dirs first).
  `python3 tools/s7880_press_scene.py scratch/s7890/v18/r1/oracle.log scratch/s7890/v18/p1/run.log`
  `python3 tools/s7856_det_verdict.py scratch/s7890/v18/score.txt --tag b18`
  `python3 tools/s7868_det_frame_cmp.py scratch/s7890/v18/r1/retail.bin scratch/s7890/v18/p1.bin --neg scratch/s7890/v18/p2.bin --plant > .../render.txt`
  If the flight window has non-exact frames, check the longest exact run vs the tick count. A lead-in before tick 0 is unpinned
  (s7888/s7889), so rerun with `--port-start <start of the longest exact run>`.
  Rescore row b18 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins, zstd the big logs.
Outcomes: render exact on det-tick frames -> 19/19 (G3 det render coverage complete, close the slug); non-exact frames on exact
ticks at the right offset -> H-render port defect (bisect the first differing RDP command).
Parked: g3-cinematic-half-frame-phase (s7874 table).
