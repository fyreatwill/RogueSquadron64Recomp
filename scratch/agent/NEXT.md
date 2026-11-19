# NEXT (s7655)
HYPOTHESIS-ID: closed-gate-drift

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7654: s7339-s7353 green via tools/census_rules.py (54 text-anchored rules, stale -> FAIL). Sweep 16 RED
(scratch/s7654/sweep.out): s7316 s7573 s7588 s7596 s7597 s7598 s7599 s7600 s7604 s7605 s7608 s7611 s7612 s7613 s7615 s7616.
1. s7588 s7596-s7616: run each, read its verdict exit ("FIXED ...", "RESULT FAIL", "NOT CLOSED", "OPEN"). By-design report
   exits -> a NOT_GATE list in tools/s7651_gate_sweep.py with the reason (keyed by tool name + the verdict text it prints;
   a tool whose verdict text changes must turn RED again). Real opens -> triage, rules keyed by text.
2. s7316 needs --ram dumps, s7573 needs game logs: mark NEEDS-INPUT in the sweep (match the tool's own message), not RED.
3. Grep every other tool that parses the post-regen tree for `<< 16` constant regexes without `u?` (s7653 found 3).
Done when the sweep is 0 RED with controls passing; then close closed-gate-drift and take the next ladder rung.
Hypotheses: H-drift (stale key) vs H-broken (instrument blind) vs H-live (default-on defect -> fix + same-run control).
Rules: never touch build/saves; one game at a time; SIGKILL only.
