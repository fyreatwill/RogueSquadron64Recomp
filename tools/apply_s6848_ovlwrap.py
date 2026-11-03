#!/usr/bin/env python3
"""s6848 G1d wide-width idiom audit (scratch/s6848/wcensus.py): emitColorFillRect (0x80009B58), the RDP side of the
game's setScreenColorOverlay (0x8000A650, called only by setupMissionTransitionScreenOverlay = mission-end transition
table step 6, ROM 0x10BF64), packs the screen width 0x8011A838 as `(W & 0x3FF) << 14` into the G_FILLRECT lr.x integer
field for the top band (0x8000A1B0), the full fill (0x8000A308) and the right band (0x8000A5E4).  Retail W <= 640 always
fits; at G1d 21:9 W = 1024 the 10-bit field wraps to 0, so those bands become lr.x 0 (ul.x 0 or x1) and are lost
(rs64_g1d_rect_wrap skips ul.x 0 fills).  Fix: W -> rs64_s6848_ovl_w(W) = min(W, 1023) (fill-mode lr is inclusive, so
1023 covers the last column); identity for W <= 1023.  ROGUESQ_G1D_OVL_WRAP=0 = old.
Diagnostic: rs64_s6848_force_ovl(rdram) before frameStartReset's overlay-enable read (0x8000A7A4); env
ROGUESQ_S6848_FORCE_OVL=<vi_lo>:<vi_hi> arms the overlay (window 128,64-896,384, red) inside that VI window only.
Idempotent.  Usage: apply_s6848_ovlwrap.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
SITES = ["0x8000A1B0", "0x8000A308", "0x8000A5E4"]
DECL = "extern uint64_t rs64_s6848_ovl_w(uint64_t); extern void rs64_s6848_force_ovl(uint8_t*); /* PATCH: s6848 decl */\n"
FOLD = "    // 0x8000A7A4: lbu         $v0, -0x5774($v0)\n    ctx->r2 = MEM_BU(ctx->r2, -0X5774);\n"
FNEW = ("    // 0x8000A7A4: lbu         $v0, -0x5774($v0)\n    rs64_s6848_force_ovl(rdram); /* PATCH: s6848 forceovl */\n"
        "    ctx->r2 = MEM_BU(ctx->r2, -0X5774);\n")
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text(); t = s
    if "PATCH: s6848 ovlwrap" not in s:
        for a in SITES:
            old = "    // %s: andi        $v1, $v1, 0x3FF\n    ctx->r3 = ctx->r3 & 0X3FF;\n" % a
            if s.count(old) == 1:
                s = s.replace(old, "    // %s: andi        $v1, $v1, 0x3FF\n    ctx->r3 = rs64_s6848_ovl_w(ctx->r3) & 0X3FF; /* PATCH: s6848 ovlwrap */\n" % a, 1)
    if "PATCH: s6848 forceovl" not in s and s.count(FOLD) == 1:
        s = s.replace(FOLD, FNEW, 1)
    if s != t:
        if "PATCH: s6848 decl" not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
        p.write_text(s); n += 1
        print("s6848 ovlwrap: %s wrap=%d force=%d" % (p.name, s.count("PATCH: s6848 ovlwrap"), s.count("PATCH: s6848 forceovl")))
print("s6848 ovlwrap: %d files" % n)
