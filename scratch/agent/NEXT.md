# NEXT (s7652)
HYPOTHESIS-ID: closed-gate-drift

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7651 found closed census gates silently RED after later code landed. Fixed s7375/s7430/s7533/s7535. Next:
1. `python3 tools/s7651_gate_sweep.py --tsv scratch/s7652/gates.tsv` (whole list, ~20 min at 6 jobs; or --only 's73[0-9]')
   for the full 135-tool table (s7651 only saw s7031-s7360).
2. Triage the RED gates, ranked by class risk: s7339 mask16 / s7342 addr-index (DEFECT rows in s7523_slow_rdp,
   s7644_rspdma, s7389_fbld), s7344 wrap / s7345 mul / s7360 gueststr (rs64_standins.cpp), s7343 / s7346 / s7348-s7353 /
   s7359, s7316, s7090. Per site: read the gate, add a rule (prefer text anchors / function names, never absolute lines),
   or fix a real defect with a same-run control. s7360 :155 already read: bounded + opt-in.
3. Make the 12 NEEDS-ARGS tools runnable with defaults or mark them non-gates in the sweep.
Hypotheses: H-diag-all (every new red site is opt-in instrument code) vs H-live (a default-on site in rs64_standins /
controls / F6 panel code is a real UB/bound defect -> fix + control, reopen that class line).
Rules: never touch build/saves; one game at a time; SIGKILL only.
