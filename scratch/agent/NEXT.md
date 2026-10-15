# Next work unit

HYPOTHESIS-ID: soak-mission-route-do_break-and-stall-rate

s4950 closed the crash/break half (5/5 reached mission, 0 breaks, 0 crashes). Remaining: is the late `stalled=1` in
[vi-fs-decision] lines (vi=0x00695C00, lastCimg=0) the old VI640 stall or normal mission steady state?
Hypotheses: (A) normal mission steady state (stalled=1 in all 5 runs, none diverge); (B) real stall present in all runs.
Discriminator: in scratch/agent/s4950_route_soak/run*.log, compare VI-origin transitions after the mission origin appears
(do origin= lines keep advancing past +60s? run4 had only 26 vs 45-58 for others) and check s4794 logs for what "stalled" meant.
Offline analysis only; no new game run needed first.
