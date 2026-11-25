# NEXT (s7951)
HYPOTHESIS-ID: owner-handoff-regression
s7950: last NEEDS-ARGS gates (s7827/s7836) are ARGS rows S7950_DETPAIR over retained captures; sweep NEEDS-ARGS 0.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold any new SOAK-RESULTS lines.
1. Every Next-steps item is closed or waiting on the owner. Agent-testable options, pick ONE:
   a. The 3 REPORT gates (s7283 and two others, `python3 tools/s7651_gate_sweep.py --only REPORT` / grep REPORT dict): check whether any
      can gain a retained input + must-regex like s7950 did (H-gateable / H-report-only).
   b. Otherwise ladder 3c's first non-closed rung not needing the owner, or an M3 idiom-class audit (BLOCKED not allowed, 3c).
