Single next work unit (s5632): fold s5630_snap3_{e,f} (scratch/agent/m6/<tag>/run.log; positive control >=10 [ccosnap]; fail = grep -a 'b14=2' / 'id=0x64'). Then discriminate hypothesis O (run-dependent id base: ids shift by -2 between runs, s5631) from D.
Offline: in funcs_43.c (~15494-15586) and the lv*_checkComplexObjectives functions, find where the id passed to setObjectiveBoolean comes from (level data vs computed). Name what differs by 2 between runs. If a failing run appears in e/f, compare its id set vs c/d to see whether the shift correlates with failure.
Expected: shift in failing run => O (fix = stable id source); no shift difference => D.
HYPOTHESIS-ID: m6-mission-endurance
