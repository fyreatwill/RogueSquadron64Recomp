# NEXT (s7854)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7853 closed 0x31=9 as H-exact (port = retail all 5076 ticks; record only one transient dump row).
Unit: `zsh tools/s7849_det_pair.sh 10 scratch/s7854` (0x31=10, ~30 min; background, one game/oracle at a time).
 Read scratch/s7854/score.txt: fork windows, song windows, and rec_align's `first persistent nonpose diff row` (transients are
 dump-instant noise, s7853). p2 must fork (control).
Hypotheses / outcomes:
 - H-exact: p1 0 fork windows and persistent row None -> 0x31=10 = retail; next 0x31=11.
 - H-audio-clock: first p1 window at/within 1 tick of a song-handle switch at VI/buffer parity -> TIMING-class, close at that tick.
 - H-pin-gap: fork with seed differing at tick 0 or a dt tick -> missing pin (pins.txt, `[dt7844] armed N` = NDT).
 - H-new-fork: fork away from songs with rand exact before -> name the writer with an oracle --watch-write run
   (--hit-cap 100000 --hit-vi-window; val= is the value BEFORE the store). SI/VI-thread-owned words are TIMING-class (s7850/s7851).
