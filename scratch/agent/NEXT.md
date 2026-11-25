# NEXT (s7949)
HYPOTHESIS-ID: owner-handoff-regression
s7948: full gate sweep 0 RED; fixed the sweep's silent ARGS fallback (cron zstd had hollowed S7925_WAITPAIR); 2 planted controls.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold any new SOAK-RESULTS lines.
1. Every Next-steps item is closed or waiting on the owner. Agent-testable options, pick ONE:
   a. NEEDS-INPUT / REPORT rows: same hollow risk as s7948 class? Check every NEEDS_INPUT tool's retained input dir for
      .zst-only survivors the tool cannot read (grep plain open() in those tools; switch to rs64_zopen). H-clean / H-hollow.
   b. Otherwise ladder 3c's first non-closed rung not needing the owner, or an M3 idiom-class audit (BLOCKED not allowed, 3c).
