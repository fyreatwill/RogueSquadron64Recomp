# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race
s4980: default soaks never armed the S45xx instruments (env-gated), so their zero hits were uninterpretable. Queued scratch/agent/soak_queue/s4980_armed_mission_a.sh (loop runs it between iterations; verdict in SOAK-RESULTS.md and scratch/agent/soak_results/s4980_armed_mission_a/keys1.log).
Work unit: read that verdict line. Fields: ctl_arm (positive control, must be >=1), bad, s4579A, pidma, crash.
- ctl_arm>=1, bad=0, pidma=0, crash=0 -> A (dissolved by default fixes): close thread, pivot to the next M5 plan step (docs/M5-AUDIO-PLAN.md).
- bad>0 or pidma>0 -> B live: fix at source in a fixup script (publish voice count after base, or hold mixer lock), ORIGIN line required.
- ctl_arm=0 -> route never reaches the render entry; redesign (arm on the hangar route, or the s4577 recipe).
If the soak has not run yet (no s4980 line in SOAK-RESULTS.md), run scratch/agent/soak_queue/s4980_armed_mission_a.sh yourself (one game at a time).
