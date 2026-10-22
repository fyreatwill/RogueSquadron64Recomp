# NEXT: G1 - s5849: how does a real run reach the WIN arm? Log c1/c10 over time in the invuln config.
s5848: invuln (class-2 hits zeroed) keeps mission alive 722 s; control fails at c2=3 (vi 33765) then Bus error in teardown (m6/s5848c/run.log, si_addr=0x3c1b4bc0a).
Hypotheses: H1 c1 climbs with flying/shooting objectives in invuln run and reaches 21 given time; H2 c1 plateaus at 8 (needs distinct bool ids / spawn trigger not reached by autopilot); H3 c10 (6) needs kills of a specific class.
Step: add a periodic (every ~300 vi, ROGUESQ_LOG_HUDBIT) [m47c] line of getObjectiveCount(1),(2),(10) from an existing hook (apply_s5847_mask_log.py anchor, e.g. lv0_checkComplexObjectives entry); run invuln arm 720 s + positive control that the control run's c2 line still reads 3 at fail.
Secondary: backtrace the post-endMissionCleanup Bus error (lldb or CRASH stack in s5848c/run.log) and name the writer of the 0x3c1b4bc0a pointer.
HYPOTHESIS-ID: g1-mission-progression
