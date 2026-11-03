#!/usr/bin/env python3
"""s6843: generic RDRAM store watch.  Every rs64_m5_writer_parity site (all instrumented game stores) checks
phys - rs64_s6843_lo < rs64_s6843_len (both 0 unless ROGUESQ_STORE_WATCH=<lo>:<hi> hex phys is set) and calls
rs64_s6843_store(pc, phys, width) in src/main/main.cpp, which prints a per-swap (pc, count, lo, hi) table.
First use: name the writer of the abort-level right-to-left black wipe that sits in RDRAM fb dumps (s6843) but
not in the captured gfx RDP stream.  Diagnostic only.  Idempotent.
Usage: apply_s6843_store_watch.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
sig = ("static void rs64_m5_writer_parity(char width, uint32_t pc,\n"
       "                                   uint32_t addr, uint32_t value) {\n")
line = ("    { uint32_t s6843_p = addr & 0x1FFFFFFFu; if (s6843_p - rs64_s6843_lo < rs64_s6843_len) "
        "rs64_s6843_store(pc, s6843_p, width); } /* PATCH: s6843 store watch */\n")
decl = ("extern volatile uint32_t rs64_s6843_lo, rs64_s6843_len;\n"
        "extern void rs64_s6843_store(uint32_t, uint32_t, char);\n")
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "PATCH: s6843" in s or s.count(sig) != 1:
        continue
    s = s.replace(sig, sig + line, 1).replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
    p.write_text(s)
    n += 1
print("s6843 store watch: %d files" % n)
