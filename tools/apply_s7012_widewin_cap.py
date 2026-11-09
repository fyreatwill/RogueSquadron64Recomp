#!/usr/bin/env python3
"""s7012 G5e: host-side area cap for the s7009 wide terrain window (ROGUESQ_DD_WIDEWIN_CAP=<a[,b,c]>, opt-in, unset = pool cap as s7009).
With one value the window's cell budget is min(pool cap, a). With ROGUESQ_DD_WIDEWIN=tog3 the window stays wide and the budget cycles
a/b/c on (mach_absolute_time/24e6) % 3 seconds (same-run 3-phase control; [s7010-clk] anchor printed once). Only the dd>1 placement's
local `cap` is changed; guest 0x80130C4C is untouched. ORIGIN: not a mitigation, a measurement knob for the cost/edge trade.
Runs after apply_s7009_widewin in RS64_REPLAY.  Usage: apply_s7012_widewin_cap.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7012 widewin cap"
f = D / "funcs_9.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "const int ww7009 = rs64_s7009_arm(); const int32_t lim7009 = ww7009 ? rs64_s7009_n() : 64; /* PATCH: s7009 widewin */\n"
assert t.count(A) == 1, t.count(A)
t = t.replace(A, A + "                if (ww7009) { const int32_t c7012 = rs64_s7012_cap(); if (c7012 > 0 && (cap <= 0 || cap > c7012)) cap = c7012; } /* %s */\n" % TAG)
A = '#include "funcs.h"\n'
t = t.replace(A, A + "extern int rs64_s7012_cap(void); /* %s */\n" % TAG, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
