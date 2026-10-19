Single next unit (M6 play-through endurance, directive 3b): queue >=3 soaks on the title->mission route (reuse the s5378 recipe / scratch/agent/s5525_base.sh as template) with a keyed mission hold >=10 min, logging every CRASH/abort and every stall (VI origin unchanged >30 s). Check CGSSessionScreenIsLocked first. Each distinct failure: lldb backtrace, name the writer.
Hypotheses: H1 mission hold is stable (no crash/stall in 3x10min); H2 a stall/hang appears (VI origin frozen); H3 a crash recurs with a new backtrace.
Discriminator: count of CRASH/stall events across the 3 runs with a same-run positive control (VI origin advancing before mission).
HYPOTHESIS-ID: m6-mission-endurance
