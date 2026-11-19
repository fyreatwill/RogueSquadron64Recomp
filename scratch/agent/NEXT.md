# NEXT (s7653)
HYPOTHESIS-ID: closed-gate-drift

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7652 full sweep: 135 gates, 83 green, 13 NEEDS-ARGS, 39 RED -> 6 fixed (s7090 s7359 s7360 s7463 s7465 s7466). Table in
scratch/s7652/sweep.out. Next, in this order:
1. Gates whose OWN control fails (an instrument we cannot trust): s7531 (controls 4/5), s7532 (live-census control FAIL on
   rt64_render_context.cpp:1682 snap[i] UNCLASSIFIED), s7538 (7/8), s7542 (7/8), s7543 (8/9), s7544 (11/13).
   Run each: `python3 tools/<tool> --controls 2>&1 | grep -iE 'control|FAIL'`. Expect line-number keys again (s7535 /
   s7359 / s7463 pattern): re-key to text anchors, an anchor that matches nothing must FAIL, never re-scope silently.
2. Write the rules for s7339 s7342 s7343-s7353 from the s7652 hand triage (PORTING-STATE s7652 lists each site's reason);
   prefer function-name / text-anchor rules, add the env name read by hand.
3. Read s7588 s7596-s7616 verdict lines: some ("FIXED ... ", "RESULT FAIL", "NOT CLOSED") may be by-design report exits;
   if so, mark them non-gates in s7651_gate_sweep.py (a small NOT_GATE list with the reason), else triage.
4. s7316 needs --ram dumps; s7573 needs game logs: mark NEEDS-INPUT in the sweep rather than RED.
Hypotheses: H-drift (failing controls are stale line/anchor keys; fix the key) vs H-broken (a control fails because the
instrument's detection regressed, so its "closed" verdict was never re-proved -> re-run the live census after the fix and
read every new row) vs H-live (a default-on site is a real defect -> fix + same-run control).
Rules: never touch build/saves; one game at a time; SIGKILL only.
