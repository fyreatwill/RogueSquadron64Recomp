#!/usr/bin/env python3
"""s6846 G1d: 21:9 abort-level wipe ends on a soft-edge frame (a ~68 px bright strip at the far left for ~0.3 s) where
4:3/retail end on flat black.  Writer (s6846 store watch on the wipe text object): the wipe updater in initHudStruct
(0x800C19AC..0x800C1B1C) sets ox = W/2 - W*f (W = screen +0x10) and picks the string (= glyph) with
`ox <= -W/2 + 1` -> s2+0x38 (glyph 0x17F, flat block, cc 11FE23) else s2+0x3A (glyph 0x180, soft edge, cc 119623).
The +1 at 0x800C1A9C is a fixed one-pixel epsilon while the end-of-wipe residual is W*0.001 (0.512 at W 512, 1.024 at
W 1024), so only a >1000-wide screen flips back to the soft glyph.  Fix: the epsilon becomes rs64_s6846_wipe_eps(v0)
(src/main/main.cpp): 1 for W <= 640 (retail, bit-identical), ceil(W/512) above.  ROGUESQ_G1D_WIPE_EPS=0 = old.
Idempotent.  Usage: apply_s6846_wipeeps.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    // 0x800C1A9C: addiu       $v0, $v0, 0x1\n    ctx->r2 = ADD32(ctx->r2, 0X1);\n"
NEW = ("    // 0x800C1A9C: addiu       $v0, $v0, 0x1\n"
       "    ctx->r2 = ADD32(ctx->r2, rs64_s6846_wipe_eps((int32_t)ctx->r2)); /* PATCH: s6846 wipeeps */\n")
DECL = "extern int32_t rs64_s6846_wipe_eps(int32_t);\n"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "PATCH: s6846 wipeeps" in s or s.count(OLD) != 1:
        continue
    s = s.replace(OLD, NEW, 1).replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
    p.write_text(s); n += 1
print("s6846 wipeeps: %d files" % n)
