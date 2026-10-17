#!/usr/bin/env python3
"""s5078: per-PC census of instrumented stores into 0x9DE80..0x9DF00 (flight-float block holding
0x9DEAC).  Hooks rs64_m5_writer_parity (already called by every swc1/sw site the s2190 pass
instrumented); calls rs64_s5078_flight_store(pc, addr), counted in upstream_compat.cpp and printed
on each swap as a [watch-wr #n] line when ROGUESQ_WATCH_LOG=1.  Diagnostic only.  Idempotent.
ORIGIN: not a mitigation -- identifies which static store site writes the float.
Usage: apply_s5078_flight_writer_census.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
sig = ("static void rs64_m5_writer_parity(char width, uint32_t pc,\n"
       "                                   uint32_t addr, uint32_t value) {\n")
line = ("    { uint32_t s5078_p = addr & 0x1FFFFFFFu; if (s5078_p >= 0x9DE80u && s5078_p < 0x9DF00u) "
        "rs64_s5078_flight_store(pc, s5078_p); } /* PATCH: s5078 flight writer census */\n")
decl = "extern void rs64_s5078_flight_store(uint32_t, uint32_t);\n"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "PATCH: s5078" in s or s.count(sig) != 1:
        continue
    s = s.replace(sig, sig + line, 1).replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
    p.write_text(s)
    n += 1
print("s5078 flight writer census: %d files" % n)
