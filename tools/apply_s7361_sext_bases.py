#!/usr/bin/env python3
"""s7361 class AL: zero-extended MEM_x bases in injected diagnostics. MEM_x(off, base) computes
rdram + ((base + off) - 0xFFFFFFFF80000000); when base+off has C type unsigned int (a uint32_t
variable, a 0x8xxxxxxxu literal, or int32 + unsigned), the 32-bit sum is ZERO-extended and the
access lands 4 GB past rdram -- outside librecomp's 4 GB reservation (s4087: SEGV_ACCERR at
rdram+0x100128d47). Each site below is an opt-in diagnostic; the fix makes the sum signed.
The same text is emitted by the source apply scripts (s7361 edits), so a regen reproduces it;
this script fixes an already-patched live tree. Idempotent.
Usage: apply_s7361_sext_bases.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FIX = [
    ("funcs_29.c", "MEM_W(0x934u, S32(0x800B0000u))", "MEM_W(0x934, S32(0x800B0000u))"),        # s3308 stage_adv (s5546 replay re-added u)
    ("funcs_29.c", "MEM_BU(0x938u, S32(0x800B0000u))", "MEM_BU(0x938, S32(0x800B0000u))"),
    ("funcs_23.c", "MEM_W(i, (int32_t)t0) = 0; MEM_W(i, (int32_t)t1) = 0;",
                   "MEM_W((int32_t)i, (int32_t)t0) = 0; MEM_W((int32_t)i, (int32_t)t1) = 0;"),  # s4571c ROGUESQ_S4571_ZERO (WRITE)
    ("funcs_10.c", "MEM_H(0X18, s3)", "MEM_H(0X18, (int32_t)s3)"),                                  # s6311 edgefade4 log
    ("funcs_10.c", "MEM_H(0X1A, s3)", "MEM_H(0X1A, (int32_t)s3)"),
    ("funcs_10.c", "MEM_W(q * 4, 0x80138D20u)", "MEM_W(q * 4, (int32_t)0x80138D20u)"),             # s6311 edgefade5 log
    ("funcs_10.c", "MEM_W(q * 4, 0x80137DBCu)", "MEM_W(q * 4, (int32_t)0x80137DBCu)"),
    ("funcs_9.c", "MEM_W(a0, 8)", "MEM_W((int32_t)a0, 8)"),                                         # s6492b ROGUESQ_FORFACE_LOG
    ("funcs_9.c", "MEM_HU(pb, 12*i)", "MEM_HU(pb, (int32_t)(12*i))"),                               # s6480 poolcensus
    ("funcs_9.c", "MEM_HU(pb, 12*i+2)", "MEM_HU(pb, (int32_t)(12*i+2))"),
    ("funcs_9.c", "MEM_HU(pb, 12*nx+4)", "MEM_HU(pb, (int32_t)(12*nx+4))"),
]
if __name__ == "__main__":
    n = 0
    for fn, old, new in FIX:
        p = D / fn
        t = p.read_text(errors="surrogateescape")
        if t.count(new) >= 1 and old not in t:
            continue
        assert t.count(old) == 1, (fn, old, t.count(old))
        p.write_text(t.replace(old, new, 1), errors="surrogateescape"); n += 1
    print("s7361 sext bases: fixed", n, "of", len(FIX))
