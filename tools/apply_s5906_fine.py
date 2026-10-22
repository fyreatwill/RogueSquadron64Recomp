"""s5906: per-shape-class r2 min/max at sphere-in, and fine-test (collideSegmentAgainstObjectNodes @0x8006AB40) calls/returns, in the s5904 w0 tally.
Class key = [obj+0] with obj = s0 (a0) of findSegmentObjectSphereHit, same key as the sphere tally. Idempotent; patches funcs_16.c and tools/apply_s5835_sphere_probe.py."""
import pathlib
P = [pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_16.c"),
     pathlib.Path(__file__).with_name("apply_s5835_sphere_probe.py")]
subs = [
 ("uint32_t p58, p48, p4c, p50, p54, o58; } rs5904_T[32];", "uint32_t p58, p48, p4c, p50, p54, o58; unsigned fc, fr; float r2lo, r2hi; } rs5904_T[32]; float rs5906_r2; /* PATCH: s5906 */"),
 ("rs5904_T[z].o58 = (uint32_t)MEM_W(S32((int32_t)obj), 0x58); rs5904_nT++; } if (kind) rs5904_T[z].ret++; else rs5904_T[z].all++; }",
  "rs5904_T[z].o58 = (uint32_t)MEM_W(S32((int32_t)obj), 0x58); rs5904_T[z].r2lo = 1e30f; rs5904_T[z].r2hi = -1e30f; rs5904_nT++; } if (kind == 2) rs5904_T[z].fc++; else if (kind == 3) rs5904_T[z].fr++; else if (kind) rs5904_T[z].ret++; else { rs5904_T[z].all++; if (rs5906_r2 < rs5904_T[z].r2lo) rs5904_T[z].r2lo = rs5906_r2; if (rs5906_r2 > rs5904_T[z].r2hi) rs5904_T[z].r2hi = rs5906_r2; } }"),
 ('[obj+58]=%08x}", rs5904_T[z].w0,', '[obj+58]=%08x fine=%u/%u r2=[%g,%g]}", rs5904_T[z].w0,'),
 ("rs5904_T[z].p54, rs5904_T[z].o58);", "rs5904_T[z].p54, rs5904_T[z].o58, rs5904_T[z].fc, rs5904_T[z].fr, rs5904_T[z].r2lo, rs5904_T[z].r2hi);"),
]
for p in P:
    t = p.read_text()
    if "PATCH: s5906" in t: print(p, "already"); continue
    for a, b in subs:
        assert a in t, (p, a[:50])
        t = t.replace(a, b, 1)
    if p.name == "funcs_16.c":
        a = "    collideSegmentAgainstObjectNodes(rdram, ctx);\n        goto after_2;"
        assert t.count(a) == 1
        t = t.replace(a, "    { extern void rs5904_tally(uint8_t*, uint32_t, int); rs5904_tally(rdram, U32(ctx->r16), 2); } /* PATCH: s5906 */\n    collideSegmentAgainstObjectNodes(rdram, ctx);\n    if (ctx->r2 != 0) { extern void rs5904_tally(uint8_t*, uint32_t, int); rs5904_tally(rdram, U32(ctx->r16), 3); } /* PATCH: s5906 */\n        goto after_2;", 1)
    else:
        a = "if (sin_) { rs5856_sinobj = rs5839_obj; rs5904_tally(rdram, rs5839_obj, 0); }"
        assert a in t
        t = t.replace(a, "if (sin_) { rs5856_sinobj = rs5839_obj; rs5906_r2 = cc[3]; rs5904_tally(rdram, rs5839_obj, 0); }")
        t = t.replace("uint32_t rs5856_sinobj; /* s5904 */", "uint32_t rs5856_sinobj; /* s5904 */ extern float rs5906_r2;", 1)
    p.write_text(t); print(p, "patched")
