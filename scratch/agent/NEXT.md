# Next work unit: read m6_sel_a/b/c verdicts (SOAK-RESULTS.md + scratch/agent/m6/s5450_sel_*/summary,run.log)
HYPOTHESIS-ID: m6-mission-transition-endurance
- Extract the distinct `origin=` set per run and compare with s5449. Different set => stick presses changed the mission; capture any crash/stall backtrace and fix root cause.
- Identical set to baseline => SEL_KEYS had no effect (no positive control); next try other key names in the autopilot or the plume title-boot loop (>=20 boots).
