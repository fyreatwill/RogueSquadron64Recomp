#!/usr/bin/env python3
"""s6876: name the caller of mat3x4Multiply (0x800191C4) that writes the camera rotation at 0x80138458+0x28. The store census only sees the
stores inside mat3x4Multiply, and static caller reads failed (overlays alias 0x800A9xxx, updateSplineCraftTransform writes a 0.0125 scaled
matrix). Entry hook, gated on g_rs64_store_diag, calls rs64_s6876_mm in src/main/main.cpp, which prints [camcaller] rows under
ROGUESQ_CAM_CALLER=1. Diagnostic only. Idempotent. ORIGIN: not a mitigation.
Usage: apply_s6876_camcaller.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
anchor = "    // 0x800191C4: addiu       $sp, $sp, -0x20\n"
line = ("    if (__builtin_expect(g_rs64_store_diag, 0)) rs64_s6876_mm(rdram, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)); "
        "/* PATCH: s6876 camcaller */\n")
decl = "extern void rs64_s6876_mm(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t);\n"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "PATCH: s6876" in s or s.count(anchor) != 1:
        continue
    s = s.replace(anchor, line + anchor, 1).replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
    p.write_text(s)
    n += 1
print("s6876 camcaller: %d files" % n)
