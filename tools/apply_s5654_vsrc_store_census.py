#!/usr/bin/env python3
"""s5654: per-PC census of instrumented stores (rs64_m5_writer_parity sites) into the voice-read
source range 0x1B2C60..0x1B3600 (where s5653 saw the 0x8000/0x7FF8 rail pattern with ZERO host
writers) plus a wide positive-control range 0x1B2C60..0x29DFB8.  Calls rs64_s5654_vstore(pc, addr,
value, width), defined in src/main/main.cpp.  Diagnostic only.  Idempotent.
ORIGIN: not a mitigation -- names the static store site that writes the rail data (H-W2).
Usage: apply_s5654_vsrc_store_census.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
sig = ("static void rs64_m5_writer_parity(char width, uint32_t pc,\n"
       "                                   uint32_t addr, uint32_t value) {\n")
line = ("    { uint32_t s5654_p = addr & 0x1FFFFFFFu; if (s5654_p >= 0x1B2C60u && s5654_p < 0x29DFB8u) "
        "rs64_s5654_vstore(pc, s5654_p, value, width); } /* PATCH: s5654 vsrc store census */\n")
decl = "extern void rs64_s5654_vstore(uint32_t, uint32_t, uint32_t, char);\n"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "PATCH: s5654" in s or s.count(sig) != 1:
        continue
    s = s.replace(sig, sig + line, 1).replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
    p.write_text(s)
    n += 1
print("s5654 vsrc store census: %d files" % n)
