# NEXT: fold s6532 r5/r6 (queued), then ORIGIN work on the -128 span saturation writer
HYPOTHESIS-ID: g1c-span-reject-predicate
s6534: r1-r4 clean; SIGBUS (1 in ~9) is not reproducing, stop spending iterations on it.
1. Fold r5/r6 from SOAK-RESULTS.md (use the tag line: alive_at_end, crashlines). Any crash: read run.log backtrace; check faulting host ptr = rdram+>16MB; fix mask in apply_s6036_dd.py.
2. Then ORIGIN: pre-clamp f0/f12/f10 at 0x80042820/0x800426D8, dd1 vs dd4 (s6521/s6526 next): why do dd4 span values saturate at -128 where dd1 does not. One instrument, paired pinned run.
