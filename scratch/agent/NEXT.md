# NEXT (s7853)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7852 closed 0x31=8 (port = retail ticks 0-3526; split = song 03's audio-clocked end, VI/buffer parity, s6806 class).
Unit: `zsh tools/s7849_det_pair.sh 9 scratch/s7853` (0x31=9, ~30 min; run in background, one game/oracle at a time).
 The driver now also traces song handle 0x8010C0E0 + AI buffers and prints s7852_fork_windows.py + g3_song_windows.py.
 Read scratch/s7853/score.txt: p1 first fork window, its tick vs the song-handle switch ticks; p2 must fork (control).
Hypotheses / outcomes:
 - H-exact: p1 no fork window over the run -> 0x31=9 = retail; next 0x31=10.
 - H-audio-clock: first p1 window starts at (or within 1 tick of) a song-handle switch whose VI/buffer counts match within ~1%
   -> TIMING-class split, close 0x31=9 at that tick.
 - H-pin-gap: p1 forks with no song switch nearby and seed already differs at tick 0 or at a dt tick -> missing pin (check pins.txt,
   `[dt7844] armed N` must equal NDT; cap is 512 since s7852).
 - H-new-fork: fork away from any song switch with rand exact before -> name the writer with an oracle --watch-write run
   (--hit-cap 100000 --hit-vi-window; val= is the value BEFORE the store). SI/VI-thread-owned words are TIMING-class (s7850/s7851).
