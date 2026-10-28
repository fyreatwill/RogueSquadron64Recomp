# NEXT: 300 s bundle-only dd4 holds on lvl 1/5/10 (+ explain "multiplier 3" at dd=4)
HYPOTHESIS-ID: g1c-dd-phase2
Context (s6578): ROGUESQ_DRAW_DISTANCE>1 now sets the pool/heap recipe itself; lvl1 130 s clean, vetoed control faults.
Work unit: queue soaks via scratch/agent/s6578_run.sh pattern (HOLD_S=300, LEVEL=5 and 10, ROGUESQ_DRAW_DISTANCE=4 only). Also grep apply_s6036_dd.py for why dd=4 logs "multiplier 3" (clamp/auto-far?). Pass: 0 crash, 0 stall. Fail: backtrace the first distinct fault.
