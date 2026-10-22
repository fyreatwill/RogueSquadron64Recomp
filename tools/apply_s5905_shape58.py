"""s5905: extend the s5904 w0 tally with the shape record's +0x58 (sub-node tree ptr) and +0x4C..+0x54 sphere words.
findSegmentObjectSphereHit (0x8006A944) goes to the fine collideSegmentAgainstObjectNodes test iff [[node]+0x58] != 0, else sphere-only hit.
Idempotent; also patches tools/apply_s5835_sphere_probe.py so a re-run keeps it."""
import pathlib
P = [pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_16.c"),
     pathlib.Path(__file__).with_name("apply_s5835_sphere_probe.py")]
subs = [
 ("static struct { uint32_t w0; unsigned all, ret; } rs5904_T[32];", "static struct { uint32_t w0; unsigned all, ret; uint32_t p58, p48, p4c, p50, p54, o58; } rs5904_T[32]; /* PATCH: s5905 */"),
 ("rs5904_T[z].w0 = w0; rs5904_nT++;", "rs5904_T[z].w0 = w0; rs5904_T[z].p58 = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x58) : 0xdeadbeef; rs5904_T[z].p48 = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x48) : 0xdeadbeef; rs5904_T[z].p4c = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x4c) : 0xdeadbeef; rs5904_T[z].p50 = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x50) : 0xdeadbeef; rs5904_T[z].p54 = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x54) : 0xdeadbeef; rs5904_T[z].o58 = (uint32_t)MEM_W(S32((int32_t)obj), 0x58); rs5904_nT++;"),
 ('" %08x={all=%u ret=%u}", rs5904_T[z].w0, rs5904_T[z].all, rs5904_T[z].ret);', '" %08x={all=%u ret=%u [w0+58]=%08x [w0+48,4c,50,54]=%08x,%08x,%08x,%08x [obj+58]=%08x}", rs5904_T[z].w0, rs5904_T[z].all, rs5904_T[z].ret, rs5904_T[z].p58, rs5904_T[z].p48, rs5904_T[z].p4c, rs5904_T[z].p50, rs5904_T[z].p54, rs5904_T[z].o58);'),
]
for p in P:
    t = p.read_text()
    if "PATCH: s5905" in t: print(p, "already"); continue
    for a, b in subs:
        assert a in t, (p, a[:40])
        t = t.replace(a, b, 1)
    p.write_text(t); print(p, "patched")
