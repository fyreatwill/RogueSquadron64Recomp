# Next work unit: replicate the 1200 s keyed mission hold twice, then add flight input
HYPOTHESIS-ID: m6-mission-endurance

s5417: one clean 1204 s hold (fbhash maxrun=320, distinct=33446). Run `zsh scratch/agent/m6_keyed_hold.sh s5418_long 1200` twice (sequentially, one game at a time, outside the 600 s soak cap; use run_in_background). Outcomes: any CRASH/stall -> lldb backtrace, name the writer, root-cause fix; all clean -> extend autopilot with in-mission flight/fire keys (autopilot passes z/start only) and hold again, since an unflown mission may skip crash paths.
