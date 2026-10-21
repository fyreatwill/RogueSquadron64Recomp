"""s5780: what is stored to the caller's sp+0x175 byte before bit 0x8.

The only writer is sb $v0,0($v1) at 0x800FFC60 in stepObjectOrientationTowardTarget:
source = lbu 0($s0), array sp+0x198 stride 0x2C, index = word sp+0x488, run
only when byte sp+0x497 != 0. The log sits at the store (r2 = source byte,
r3 = destination, r8 = flag byte). Player = saved a0 at sp+0x4F8 == 0x80137DBC.
Every player store with source != 0 is printed (cap 40); player stores with
source == 0 are printed for the first 8 (positive control: the hook fires).
Gated by ROGUESQ_LOG_MTM. Shares rs64_s5773_ord/ms with [bit8call].
"""
import pathlib
import sys

TAG = "PATCH: s5780 sp175 store"
STORE_COMMENT = "    // 0x800FFC60: sb          $v0, 0x0($v1)\n"

HELPER = """/* """ + TAG + """ */
static int s5780_e = -1;
static unsigned s5780_nz_left = 40;
static unsigned s5780_z_left = 8;
static unsigned s5780_other_left = 6;
static unsigned s5780_total;
static void s5780_store(uint8_t* rdram, recomp_context* ctx) {
    unsigned obj, src, flag, idx, dst;
    int player;
    if (s5780_e < 0) {
        const char* e = getenv("ROGUESQ_LOG_MTM");
        s5780_e = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!s5780_e) return;
    obj = (unsigned)MEM_W(ctx->r29, 0X4F8);
    src = (unsigned)(ctx->r2 & 0xFFu);
    flag = (unsigned)(ctx->r8 & 0xFFu);
    idx = (unsigned)U32(ctx->r9);
    dst = (unsigned)U32(ctx->r3);
    player = (obj == 0x80137DBCu);
    s5780_total++;
    if (player && src != 0) { if (!s5780_nz_left) return; s5780_nz_left--; }
    else if (player) { if (!s5780_z_left) return; s5780_z_left--; }
    else { if (!s5780_other_left) return; s5780_other_left--; }
    {
        extern long long rs64_s5773_ms(void);
        extern unsigned long rs64_s5773_ord(void);
        fprintf(stderr, "[sp175] ord=%lu t=%lld obj=0x%08X player=%d idx=%u src=%u flag=%u dst=0x%08X n=%u\\n",
            rs64_s5773_ord(), rs64_s5773_ms(), obj, player, idx, src, flag, dst, s5780_total);
        fflush(stderr);
    }
}
"""


def apply(text):
    if TAG in text:
        return text, 0
    if text.count(STORE_COMMENT) != 1:
        raise RuntimeError(f"store comment count {text.count(STORE_COMMENT)}")
    out = []
    helper_done = False
    n = 0
    for line in text.splitlines(keepends=True):
        if not helper_done and line == '#include "funcs.h"\n':
            out.append(line)
            out.append(HELPER)
            helper_done = True
            continue
        out.append(line)
        if line == STORE_COMMENT:
            out.append(f"    s5780_store(rdram, ctx); /* {TAG} */\n")
            n += 1
    if not helper_done:
        raise RuntimeError('missing #include "funcs.h"')
    return "".join(out), n


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_43.c"
    updated, count = apply(p.read_text())
    if count:
        p.write_text(updated)
    print(f"{p}: s5780 sp175 store x{count}")
