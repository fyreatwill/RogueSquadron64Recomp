# NEXT: fold s6532 r3-r6 (dd4+bypass lvl5); catch the rare SIGBUS
HYPOTHESIS-ID: g1c-span-reject-predicate
r1,r2 clean (s6533). Use m6/*s6532*/summary (alive_at_end, crashlines), not rc.
1. Any crash: read run.log backtrace; check faulting host ptr = rdram+>16MB (H-16MB unmasked ucode read); fix mask/relocation in apply_s6036_dd.py.
2. All 6 clean: rate <~1/6 -> check ~/Library/Logs/DiagnosticReports for the s6529 crash report, or move to ORIGIN work on the -128 span saturation writer (0x80042820/0x800426D8).
