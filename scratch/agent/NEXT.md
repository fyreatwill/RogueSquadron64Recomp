# NEXT (s7372)
HYPOTHESIS-ID: tsan-mission-coverage

s7371: ROGUESQ_AUTOPILOT_CLOCK=frames landed (control PASS). The TSan m1 run reached a mission (level 16, 3 initMission,
~700 mission frames at ~1.2 frames/s); report H-clean, 4 new rows classified (tools/s7354_tsan_report.py rc 0).

Work unit (OFFLINE, no game run): the AQ runtime half (CURRENT-TRUTH item 1 / 16). Cross the s7366 static lockset
rows (scratch/s7366/lockset_rows.txt, rows_A/B.tsv) with the m1 TSan reports (scratch/s7371/m1/tsan.*): for each AQ
cross-thread container, did TSan see accesses from >=2 threads in the mission phase (after the initMission line;
log order in tsan.* vs run.log is not shared, so use the race report frames + the s7366 container names)? Classify each
AQ row as runtime-exercised-clean / not-exercised. Tool: tools/s7372_aq_runtime_cross.py.
Hypotheses: H-covered (most AQ rows have their accessor functions in m1 stacks -> AQ runtime half closes clean),
H-gap (key mission rows: present queue, workload, audio backlog trim, spill reset, never appear -> name them and plan a
w-gated TSan flight route for those paths), H-race (a cross reveals a row whose lock is missing in a TSan stack).
Positive control: a row known to race in the planted CTL (s7354_race_ctl_var) must be found by the cross tool.
If nothing an agent can do remains after this: CURRENT-TRUTH item 17.
