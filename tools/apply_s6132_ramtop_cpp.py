#!/usr/bin/env python3
"""s6132 G1d: parameterise 8 MB literals in hand-written C++ (librecomp/ultramodern/src/main) by rs64_ram_top. Idempotent."""
import re, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[1]
files = ["lib/N64ModernRuntime/librecomp/src/pi.cpp", "lib/N64ModernRuntime/librecomp/src/rsp.cpp",
         "lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp", "src/main/upstream_compat.cpp",
         "src/main/rt64_render_context.cpp"]
B = r"(?<![0-9A-Fa-fx])"
subs = [(B + r"0xA0800000u?\b", "(rs64_ram_top + 0x20000000u)"),
        (B + r"0x80800000u?\b", "rs64_ram_top"),
        (B + r"0x0*800000u?\b", "(rs64_ram_top - 0x80000000u)"),
        (B + r"0x7FFFFFu?\b", "0xFFFFFFu")]
tot = 0
for f in files:
    p = root / f; s = p.read_text()
    for pat, rep in subs:
        s, k = re.subn(pat, rep, s); tot += k
    if 'uint32_t rs64_ram_top;' not in s:
        m = re.search(r'^#include[^\n]*\n(?!#include)', s, re.M)
        i = [x for x in re.finditer(r'^#include[^\n]*\n', s, re.M)][-1].end()
        s = s[:i] + 'extern "C" uint32_t rs64_ram_top; // s6132\n' + s[i:]
    p.write_text(s)
print("replaced", tot)
