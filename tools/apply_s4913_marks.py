#!/usr/bin/env python3
"""s4913: insert rs64_s4913_mark(rdram, "<fn>") at entry of the five swap-handshake functions.
Idempotent. Usage: apply_s4913_marks.py <RecompiledFuncs dir>. Same patch lives in
fixup_game_funcs_vendored.py for regens; this applies it to an already-patched tree."""
import re, sys, pathlib
base = pathlib.Path(sys.argv[1])
names = ("advanceVideoFrame", "signalFrameSyncMesgNonblock", "waitOnVideoQueue",
         "waitForPostSwapAck", "clearPostSwapPendingFlags")
decl = 'extern void rs64_s4913_mark(uint8_t* rdram, const char* tag);\n'
for p in sorted(base.glob("funcs_*.c")):
    t = p.read_text(); orig = t
    for nm in names:
        pat = r"RECOMP_FUNC void " + nm + r"\(uint8_t\* rdram, recomp_context\* ctx\) \{\n"
        if not re.search(pat, t) or f'rs64_s4913_mark(rdram, "{nm}")' in t: continue
        if decl not in t: t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + decl, 1)
        m = re.search(pat, t)
        t = t[:m.end()] + f'    rs64_s4913_mark(rdram, "{nm}"); // PATCH: s4913 ordering mark\n' + t[m.end():]
        print(p.name, nm)
    if t != orig: p.write_text(t)
