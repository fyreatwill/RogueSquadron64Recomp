# NEXT (s7856)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7855 closed 0x31=11 as H-exact (rand, hp, songs, rumble, tick-keyed 460-w record all equal over 1539 ticks).
Unit: `zsh tools/s7849_det_pair.sh 12 scratch/s7856` (0x31=12, ~35 min; background, one game/oracle at a time).
 Read scratch/s7856/score.txt: fork windows, song windows, the s7854_tick_rec_cmp lines ("ticks with a full 460-w record" must
 be > 0, else no verdict) and the control block (must report tick 100). p2 must fork.
 Note: s7855 landed no code change; if 0x31=12 is H-exact too, consider batching 12+13 per session (one game at a time, serial)
 or adding an engineering change so the no-engineering counter does not trip.
Hypotheses / outcomes:
 - H-exact: p1 0 fork windows and tick-rec "first nonpose diff tick None" -> 0x31=12 = retail; next 0x31=13.
 - H-audio-clock: first p1 window at/within 1 tick of a song-handle switch at VI/buffer parity -> TIMING-class, close at that tick.
 - H-pin-gap: fork with seed differing at tick 0 or a dt tick -> missing pin (pins.txt, `[dt7844] armed N` = NDT).
 - H-new-fork: record diverges with rand exact before -> the first nonpose word names the field; name the writer with an oracle
   --watch-write run (--hit-cap 100000 --hit-vi-window; val= is the value BEFORE the store). SI/VI-thread words are TIMING-class.
