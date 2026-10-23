# NEXT: G1(d) what triggers the ctl-arm mission end on lvl7/lvl8?
HYPOTHESIS-ID: g1-d-objective-gate
s5995: endMissionCleanup fires in ctl AND tele arms (lvl7 vi~15259); counter id=2 hit 3 (threshold) ~2600 VIs earlier but ctl ends too.
Hypotheses: H1 end is timer/scripted (independent of counters); H2 end is driven by a different counter/flag also moved in ctl (e.g. id=1 oscillations); H3 end is a player-death/fail path (requestMissionTransitionMode a0=1 mask=2).
Work unit: in a lvl7 ctl run, log backtrace + args of requestMissionTransitionMode n=3 (mend-bt already exists in run.log: read scratch/agent/m6/g1_lvl7ctl/run.log lines near 'mend] fn=clearMission') and the flags/counters dump at that instant; decide fail vs win. Positive control: n=1,2 transitions already logged.
No aim/steer work.
