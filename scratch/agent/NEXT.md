# NEXT (s7277): G5c H-slow / GPU load: does load slow the game itself (not the capture), and does GPU load freeze it?
HYPOTHESIS-ID: g5c-busy-host
State: s7276: 15 and 5 `yes` spinners (load avg 30 / ~10) during a 600 s L12 owner-recipe PLAIN FS hold: 0 flight holds >= 250 ms,
control 3/3 each (H-robust for CPU load). Capture changes/s fell 44.3 -> 41.8 / 35.8, but cross-run and capture-side, so not a game rate.
Hypotheses: H-cpu-slow (game VI/frame rate drops under CPU load: steady slowdown the owner reads as "buffering"); H-gpu (GPU or
WindowServer load, which `yes` does not make, produces holds); H-none (neither: G5c parks for an owner screen recording of a freeze).
Discriminator, ONE run per arm, within-run toggle (iron rule 2): run the game with its own per-VI wall-clock log (G1b instrument,
grep CURRENT-TRUTH/PROJECT-OVERVIEW for the G1b frame-time env, e.g. the s7010-clk / [s7258] lines) and toggle 15 spinners on/off every
60 s from a wrapper that logs the toggle times; score game frames/s and VI gaps per on/off window. Second arm: same toggle with a GPU
load (e.g. a Metal/WebGL stress page in a browser, or `tools/` GPU busy loop if one exists) instead of the spinners.
Commands: extend tools/s7276_busy_host_arm.zsh with TOGGLE=60 (spinners started/killed per window, times to <TAG>.toggle), keep the
SIGSTOP controls. Check HID idle >= 120 s + screen unlocked first; pkill -x yes afterwards.
Expected: H-cpu-slow -> on-window game fps < off-window; then test the QOS_ALL opt-in (s6962-s6989) in the same toggle run.
H-gpu -> holds only in GPU-on windows; sample the process during one. H-none -> G5c parked for an owner datum.
