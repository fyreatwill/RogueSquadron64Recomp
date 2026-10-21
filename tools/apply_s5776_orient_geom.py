"""s5776: live angles and the three vec3s at the return-2 store.

Called on the same 0x800FF6F0 line as s5775_ret2, after that log, so this
line is the one in front of a player debris call. Player object only.
The angle registers are read, never written. Vec3s are MEM_W bit patterns.

Gated by ROGUESQ_LOG_MTM. Cap 8. Shares rs64_s5773_ord/ms.
"""
import pathlib
import sys

TAG = "PATCH: s5776 orient geom"

RET2_CALL = "    s5775_ret2(rdram, ctx); /* PATCH: s5775 orient ret2 */\n"

HELPER = """/* """ + TAG + """ */
static int s5776_e = -1;
static unsigned s5776_left = 8;
static void s5776_geom(uint8_t* rdram, recomp_context* ctx) {
    unsigned obj;
    union { uint32_t u; float f; } pun;
    float f22, f26, rx, ry, rz, o10x, o10y, o10z, o1cx, o1cy, o1cz, px, py, pz;
    if (s5776_e < 0) {
        const char* e = getenv("ROGUESQ_LOG_MTM");
        s5776_e = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!s5776_e) return;
    obj = (unsigned)U32(ctx->r8);
    if (obj != 0x80137DBCu) return;
    if (s5776_left == 0) return;
    s5776_left--;
    /* Read only. Writing f22/f26 would void the angle gate. */
    f22 = ctx->f22.fl;
    f26 = ctx->f26.fl;
    pun.u = (uint32_t)MEM_W(ctx->r17, 0x10); rx = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r17, 0x14); ry = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r17, 0x18); rz = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0x10); o10x = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0x14); o10y = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0x18); o10z = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0x1C); o1cx = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0x20); o1cy = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0x24); o1cz = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0x4); px = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0x8); py = pun.f;
    pun.u = (uint32_t)MEM_W(ctx->r8, 0xC); pz = pun.f;
    {
        extern long long rs64_s5773_ms(void);
        extern unsigned long rs64_s5773_ord(void);
        fprintf(stderr, "[orient-geom] ord=%lu t=%lld f22=%g f26=%g rx=%g ry=%g rz=%g o10x=%g o10y=%g o10z=%g o1cx=%g o1cy=%g o1cz=%g px=%g py=%g pz=%g\\n",
            rs64_s5773_ord(), rs64_s5773_ms(),
            f22, f26, rx, ry, rz, o10x, o10y, o10z, o1cx, o1cy, o1cz, px, py, pz);
        fflush(stderr);
    }
}
"""


def apply(text):
    if TAG in text:
        return text, 0
    if text.count(RET2_CALL) != 1:
        raise RuntimeError(f"s5775 ret2 call count {text.count(RET2_CALL)}")
    lines = text.splitlines(keepends=True)
    out = []
    helper_done = False
    n = 0
    for line in lines:
        if not helper_done and line == '#include "funcs.h"\n':
            out.append(line)
            out.append(HELPER if HELPER.endswith("\n") else HELPER + "\n")
            helper_done = True
            continue
        out.append(line)
        if line == RET2_CALL:
            out.append(f"    s5776_geom(rdram, ctx); /* {TAG} */\n")
            n += 1
    if not helper_done:
        raise RuntimeError('missing #include "funcs.h"')
    if n != 1:
        raise RuntimeError(f"inserted {n}")
    return "".join(out), n


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_43.c"
    updated, count = apply(p.read_text())
    if count:
        p.write_text(updated)
    print(f"{p}: s5776 orient geom x{count}")
