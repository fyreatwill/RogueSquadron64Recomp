# NEXT (s7950)
HYPOTHESIS-ID: owner-handoff-regression
s7949: sweep now HOLLOWs empty-output GREENs (s7283 -> REPORT) and re-scores cache hits; full uncached sweep 0 RED/0 HOLLOW.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold any new SOAK-RESULTS lines.
1. Every Next-steps item is closed or waiting on the owner. Agent-testable options, pick ONE:
   a. NEEDS-ARGS s7827/s7836 take a retained capture argv: if their captures survive (raw or .zst) give each an ARGS row with a
      must-regex so they gate instead of reading usage (H-retained / H-gone; gone -> REPORT-style note).
   b. Otherwise ladder 3c's first non-closed rung not needing the owner, or an M3 idiom-class audit (BLOCKED not allowed, 3c).
