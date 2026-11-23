# NEXT (s7859)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7858 closed the 0x31=14 t892 transient as a dt-pin indexing bug (fixed, tools/s7849_det_pins.py now exits 2 on a missing
tick); 0x31=14 = H-audio-clock FORK only. Continue the serial retail-flight det sweep.
Unit: `zsh tools/s7856_det_sweep.sh scratch/s7859 15 16` (serial, ~40 min; stops at first FORK; one game run at a time).
Hypotheses per value: H-exact (rand/hp/songs/record equal, residual none|timing-class) vs H-audio-clock (fork at a song-handle
switch with VI/buffer parity, closed class) vs H-new (record nonpose diff before any song switch -> name the writer with
tools/s7858_store_seq_cmp.py: oracle `--watch-write A:B --hit-vi-window lo:hi --hit-cap 100000000` + port
ROGUESQ_STORE_DIAG=1 ROGUESQ_STORE_WATCH_PTS=<16-byte pts> (tick= stamped); FIRST check the pins file has no exit-2 warning).
Positive controls: p2 must fork at t0, control flip caught at t100.
