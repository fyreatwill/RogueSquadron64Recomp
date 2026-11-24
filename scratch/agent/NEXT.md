# NEXT (s7889)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 17 missions render-exact on det-tick flight frames (m1-m16 and b17; s7888 added m16 with --port-start).
Not yet render-scored: bonus b16 (race, s7860 race-safe schedule, row "b16" uses scratch/s7860/v16s), b18 (s7862).
Unit: bonus 16 with the race-safe schedule + render oracle, screen unlocked, ~30-45 min. First read the s7860 entry
(`grep -n 'Session 7860' PORTING-STATE.md`) for its PP_OVR/AP_OVR (the race self-starts, schedules end at 43.5) and scale the AP
to the APM=1 timing (tools/s7880_press_scene.py on the result tells you the offsets). Then:
  `env RBIN=1 PP_OVR=... AP_OVR=... zsh tools/s7849_det_pair.sh 16 scratch/s7889/v16`   (check how s7860 selected the bonus: the
  0x31 value and BASE_EEP it used)
  `python3 tools/s7880_press_scene.py scratch/s7889/v16/r1/oracle.log scratch/s7889/v16/p1/run.log`
  `python3 tools/s7856_det_verdict.py scratch/s7889/v16/score.txt --tag b16`
  `python3 tools/s7868_det_frame_cmp.py scratch/s7889/v16/r1/retail.bin scratch/s7889/v16/p1.bin --neg scratch/s7889/v16/p2.bin --plant > .../render.txt`
  If neg FAILs with "pinned 0" in the last phase, look at the pair vote list: a second offset whose count equals retail's last-
  phase length means a cinematic shifted the pairing; rerun with `--port-start <port start of last phase>` (s7888).
  Rescore row b16 in tools/s7862_det_sweep_table.py (run it + --control), delete the bins after scoring.
Competing hypotheses / outcomes: H-exact ticks + render flight exact -> 18; FORK at a song end with VI/buffer parity ->
audio-clock (render the pre-fork prefix); render non-exact on exact ticks at the right offset -> H-render port defect.
Parked: g3-cinematic-half-frame-phase (s7874 table).
