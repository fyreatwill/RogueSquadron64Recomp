# Next work unit

HYPOTHESIS-ID: soak-mission-route-do_break-and-stall-rate

Re-scoped by the s4949 unblock (see UNBLOCK.md). Nothing here needs a human.

Goal: get a fresh, completed verdict on the port's crash/stall rate on the route that reaches mission entry
(~96.8s, origin 0x690400; driver in scratch/agent/s4946_flip_rate.sh). The last gated sample (s4921) ended rc=137
(timeout, no verdict) and the last completed one (s4794) showed 2/5 VI640 stalls and 1/5 startup crash.
1. Run the s4946 route driver N=5 times, ONE game run at a time, each with a hard timeout >= 150s (SIGKILL).
2. Per run record: reached mission-entry origin (yes/no, VI#), any "Encountered break at original vram" line
   (the do_break handler prints and exits, so a hit is loud), crash/abort, vi-fs stalled.
3. Positive control: the run must show the 0x690400 origin line; a run without it is route-invalid, not a pass.
4. Append the row to SOAK-RESULTS.md. If any "Encountered break" appears, map the vram to
   docs/M3-S4840-MOVZ-MOVN-REACHABILITY.md / M3-S4843 census to say whether it is a movz/movn site.
