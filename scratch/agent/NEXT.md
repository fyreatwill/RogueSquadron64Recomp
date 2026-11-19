# NEXT (s7654)
HYPOTHESIS-ID: closed-gate-drift

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7653: the 6 control-failing gates are green; sweep 28 RED (scratch/s7653/sweep.out). Next, in this order:
1. Write rules for s7339 s7342 s7343 s7344 s7345 s7346 s7348 s7349 s7350 s7351 s7352 s7353 from the s7652 hand triage
   (PORTING-STATE s7652 lists each site's reason). Key by text anchor / function name, never line; an anchor that matches
   nothing must FAIL (copy the s7538 STALE pattern). Add the env name read by hand. Re-run each with --controls.
2. s7588 s7596-s7616: read each verdict exit ("FIXED ...", "RESULT FAIL", "NOT CLOSED", "OPEN"). By-design report exits ->
   a NOT_GATE list in s7651_gate_sweep.py with the reason; real opens -> triage.
3. s7316 needs --ram dumps, s7573 needs game logs: mark NEEDS-INPUT in the sweep rather than RED.
4. Grep every other tool that parses the post-regen tree for `<< 16` constant regexes without `u?` (s7653 found 3).
Hypotheses: H-drift (stale key) vs H-broken (instrument blind, verdict never re-proved) vs H-live (default-on defect -> fix +
same-run control).
Rules: never touch build/saves; one game at a time; SIGKILL only.
