# NEXT (s7857)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7856 closed 0x31=12 as H-exact (5674 ticks incl. death/respawn). 0x31=7..12 all close as retail (8 = audio-clock timing).
Unit: `zsh tools/s7856_det_sweep.sh scratch/s7857 13 14` (~70 min, serial, background). Read scratch/s7857/verdicts.txt; each
 line comes from tools/s7856_det_verdict.py. Find the level count first if unsure (19 levels 0-18 per G4; 0x31 is mission index).
Outcomes:
 - both H-exact -> record, next sweep 15 16 (then 17 18; sweep ends at the last mission).
 - FORK (sweep stops) -> hand-diagnose that value from OUTROOT/v<v>/score.txt: song-switch at VI/buffer parity = H-audio-clock
   (timing class, close); seed differs at t0/dt tick = H-pin-gap (pins.txt); record diverges with rand exact = H-new-fork (name
   the writer with an oracle --watch-write run, val= is the value BEFORE the store).
 - NO-VERDICT -> the reason is on the line (crash, no full-record ticks, p2 did not fork); fix and rerun that value.
