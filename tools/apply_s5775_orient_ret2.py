"""s5775: which fill stores the orientation return of 2.

The only store of 2 is the sb at 0x800FF6F0. byte0/byte1 are the selected
record (s1). The return-1 store at 0x800FFA40 is the control.

A single 32-hit cap can be consumed by the spline caller (jal 0x800B0C64)
before updatePlayerCraftPhysics kills the player. Player-object hits
(a0 saved at sp+0x4F8, the same s3 the debris jal passes) are capped at 32
on their own. Other objects are capped at 16 so the log still shows them.

Gated by ROGUESQ_LOG_MTM. Shares rs64_s5773_ord/ms with [debris-call].
"""
import pathlib
import sys

TAG = "PATCH: s5775 orient ret2"

RET2_COMMENT = "    // 0x800FF6F0: sb          $t3, 0x497($sp)\n"
RET1_COMMENT = "    // 0x800FFA40: sb          $t0, 0x497($sp)\n"

HELPER = """/* """ + TAG + """ */
static int s5775_e = -1;
static unsigned s5775_p_left = 32;
static unsigned s5775_o_left = 16;
static unsigned s5775_ret1_n;
static int s5775_enabled(void) {
    if (s5775_e < 0) {
        const char* e = getenv("ROGUESQ_LOG_MTM");
        s5775_e = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    return s5775_e;
}
static void s5775_ret2(uint8_t* rdram, recomp_context* ctx) {
    unsigned obj;
    unsigned byte0;
    unsigned byte1;
    unsigned v;
    unsigned idx;
    int player;
    union { uint32_t u; float f; } pun;
    if (!s5775_enabled()) return;
    obj = (unsigned)U32(ctx->r8);
    player = (obj == 0x80137DBCu);
    if (player) {
        if (s5775_p_left == 0) return;
        s5775_p_left--;
    } else {
        if (s5775_o_left == 0) return;
        s5775_o_left--;
    }
    byte0 = (unsigned)MEM_BU(ctx->r17, 0);
    byte1 = (unsigned)MEM_BU(ctx->r17, 1);
    v = (unsigned)U32(ctx->r11);
    idx = (unsigned)U32(ctx->r12);
    pun.u = (uint32_t)MEM_W(ctx->r17, 0x24);
    {
        extern long long rs64_s5773_ms(void);
        extern unsigned long rs64_s5773_ord(void);
        fprintf(stderr, "[orient-ret] ord=%lu t=%lld kind=ret2 byte0=%u byte1=%u f24=%g v=%u idx=%u obj=0x%08X player=%d\\n",
            rs64_s5773_ord(), rs64_s5773_ms(), byte0, byte1, pun.f, v, idx, obj, player);
        fflush(stderr);
        if (player) { /* s5879: hit-record dump + candidate object slots */
            unsigned w, oi = (unsigned)MEM_HU(ctx->r17, 2);
            fprintf(stderr, "[orient-hit] ord=%lu oi=0x%04X rec:", rs64_s5773_ord(), oi);
            for (w = 0; w < 0x30; w += 4) fprintf(stderr, " %08X", (unsigned)MEM_W(ctx->r17, w));
            fprintf(stderr, "\\n[orient-hit] ctx(oi) tbl=*0x80130BB0:");
            {
                int32_t tb = (int32_t)MEM_W(0, (int32_t)0x80130BB0u);
                int32_t cp = (int32_t)MEM_W(0, tb + (int32_t)(oi * 8u));
                fprintf(stderr, " cp=%08X:", (unsigned)cp);
                if ((unsigned)cp >= 0x80000000u && (unsigned)cp < 0x80800000u)
                    for (w = 0; w < 0x40; w += 4) fprintf(stderr, " %08X", (unsigned)MEM_W(0, cp + (int32_t)w));
            }
            fprintf(stderr, "\\n");
            fflush(stderr);
        }
    }
}
static void s5775_ret1(uint8_t* rdram, recomp_context* ctx) {
    unsigned n;
    (void)rdram;
    (void)ctx;
    if (!s5775_enabled()) return;
    s5775_ret1_n++;
    n = s5775_ret1_n;
    if (!(n <= 8u || (n % 500u) == 0u)) return;
    {
        extern long long rs64_s5773_ms(void);
        extern unsigned long rs64_s5773_ord(void);
        fprintf(stderr, "[orient-ret] ord=%lu t=%lld kind=ret1 n=%u\\n",
            rs64_s5773_ord(), rs64_s5773_ms(), n);
        fflush(stderr);
    }
}
"""


def apply(text):
    if TAG in text:
        return text, 0
    if text.count(RET2_COMMENT) != 1:
        raise RuntimeError(f"ret2 comment count {text.count(RET2_COMMENT)}")
    if text.count(RET1_COMMENT) != 1:
        raise RuntimeError(f"ret1 comment count {text.count(RET1_COMMENT)}")
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
        if line == RET2_COMMENT:
            out.append(f"    s5775_ret2(rdram, ctx); /* {TAG} */\n")
            n += 1
        elif line == RET1_COMMENT:
            out.append(f"    s5775_ret1(rdram, ctx); /* {TAG} */\n")
            n += 1
    if not helper_done:
        raise RuntimeError('missing #include "funcs.h"')
    if n != 2:
        raise RuntimeError(f"inserted {n}")
    return "".join(out), n


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_43.c"
    updated, count = apply(p.read_text())
    if count:
        p.write_text(updated)
    print(f"{p}: s5775 orient ret2 x{count}")
