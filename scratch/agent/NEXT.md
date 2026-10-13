# Next work unit

HYPOTHESIS-ID: oracle-poke-mission-entry

s4724 result: oracle with alternating Start/A presses (scratch/agent/s4724_run.sh) reaches initMission 0x800FA250 at t=73.4 s on retail; no poke needed. The thread's entry question is closed.
Unit: extend s4724_run.sh to --secs 120 with mission-phase watches: capture VI origin/width after t=73 s (--vi-trace is already on) plus --watch-write on the port's known mission-sensitive addresses (the heap freelist 64 KB region, README control) and compare against the port's mission-phase recipe. Collect everything in one run.
Outcomes: retail mission origin/width differs from port's => points at the video path; freelist writes present on retail => a legitimate writer exists to match; both absent => port divergence is port-only.
Positive control: a whole-RDRAM watch must fire ~1.6M times per 8 s (README).
