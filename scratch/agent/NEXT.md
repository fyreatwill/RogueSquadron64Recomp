# NEXT: G1 - s5870: read soak s5869_hold600 (AP_TITLE_N=17 AP_HOLD=600)
Hypotheses: H31b begin n=1 (pause 0x101 at VI~4560) is a natural mission-start requester; H31c it is the still-held 2500 ms START (fire 17 released at 76.5s == mission origin onset) read in-mission.
Discriminator: grep '[flw] .*beginMissionEndTransition' in scratch/agent/m6/s5869_hold600/run.log. Absent (and initMission writers still present = control) -> H31c: make harness hold short / gate keys on mission entry, then rerun stick table 240-440 and check ROGUESQ_LOG_PLPOS position changes. Present -> H31b: find natural requester (event table 0x8010B350 chain, s5846).
If route fails (allattempts-failed) it is flaky-route, rerun once.
HYPOTHESIS-ID: g1-mission-progression
Also: backtrace Bus error far=0x3c2d5b616 / 0x37fffd040 (M6) when a run recurs it.
