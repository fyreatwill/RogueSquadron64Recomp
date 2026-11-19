#!/usr/bin/env python3
"""s7625 G6c step 3b: tag every exit of the game's sphere/point view test transformVec3ToNpcLocalWithScale (0x8001DC34, funcs_6.c)
with the PC of the branch that took it, and report (exit, v0, camera-space xyz, view near/far) to the host at L_8001E1E8 while
the host flag rs64_vt_on is set (src/main/rs64_standins.cpp sets it around its addNpcToVisibilityBucket mips_call only).
Off = one global store per exit and one predicted-false test: retail behaviour untouched. Measurement only.
Exit map (radius path, a3 != 0): DCF4/DD0C/DD24 box-low x/y/z (< *0x8000093C), DD40/DD54/DD68 box-high x/y/z (> *0x80000940),
DD78 behind (z+r <= 0), DDA8 far (z-r >= view+0x28), DF00/DFD4 pass (v0=1, side test), DF08 side reject, DFD4 v0=1 direct.
Point path (a3 == 0): DFFC/E010/E024 box-low, E03C/E04C/E05C box-high, E06C near, E080 far, E1B4 side reject, E1E4 side result.
Idempotent; RS64_REPLAY entry after apply_s7623_standins.py. Usage: apply_s7625_viewtest_reason.py [RecompiledFuncs dir]"""
import sys, pathlib, re
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7625 vt why"
f = D / "funcs_6.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
head = "RECOMP_FUNC void transformVec3ToNpcLocalWithScale("
s = t.index(head); e = t.index("\nRECOMP_FUNC ", s + 1)
body = t[s:e].split("\n")
br = re.compile(r"//\s*0x(8001[DE][0-9A-F]{3}):\s+(b|j)\w*\s")
last = None; n = 0; out = []
for ln in body:
    m = br.search(ln)
    if m: last = m.group(1)
    if ln.strip() == "goto L_8001E1E8;":
        assert last, "no branch before goto"
        ln = ln.replace("goto L_8001E1E8;", "{ rs64_vt_pc = 0x%su; goto L_8001E1E8; } /* %s */" % (last, TAG)); n += 1
    elif ln == "L_8001E1E8:":
        out.append("    rs64_vt_pc = 0x8001E1E4u; /* %s */" % TAG)
        out.append(ln)
        out.append("    if (__builtin_expect(rs64_vt_on, 0)) rs64_vt_why(rdram, ctx, rs64_vt_pc); /* %s */" % TAG); continue
    out.append(ln)
assert n >= 20, n
decl = "/* %s decls */\nextern int rs64_vt_on; extern uint32_t rs64_vt_pc; void rs64_vt_why(uint8_t*, recomp_context*, uint32_t);\n" % TAG
t = t[:s] + decl + "\n".join(out) + t[e:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG, "exits", n)
