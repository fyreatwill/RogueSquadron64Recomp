"""s4864: data_size (OSTask+0x34) writer trace. Kinds: 0=synth-wrapper entry, 1=counter reset (0x8009106C),
2=counter incr (0x800911DC), 3=OSTask data_size store (0x80091784). Gate ROGUESQ_LOG_S4864=1.
Prints per-store rows (cap 400): value, resets/incs/synth-entries since previous store, ms since previous store;
plus a value histogram every 256 stores (positive control: histogram total must equal store count).
Compare ROGUESQ_S4562_PAUSE=0 vs 4 in the same run set. ORIGIN: read-only logging. Idempotent live-tree patch."""
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_24.c"
HELPER = r'''
/* PATCH: s4864 datasize helper */
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
void rs64_s4864_ev(int kind, unsigned val) {
    static int enabled = -1; static unsigned long ent, rst, inc, st, hist[8], last_ent, last_rst, last_inc; static double last_t;
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    if (kind == 0) { __atomic_add_fetch(&ent, 1, __ATOMIC_SEQ_CST); return; }
    if (kind == 1) { __atomic_add_fetch(&rst, 1, __ATOMIC_SEQ_CST); return; }
    if (kind == 2) { __atomic_add_fetch(&inc, 1, __ATOMIC_SEQ_CST); return; }
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); double t = ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
    unsigned long n = ++st; hist[val < 7 ? val : 7]++;
    if (n <= 400) fprintf(stderr, "[s4864] store#%lu data_size=%u d_synth=%lu d_reset=%lu d_inc=%lu dt_ms=%.1f\n", n, val, ent - last_ent, rst - last_rst, inc - last_inc, t - last_t);
    if ((n & 255) == 0) fprintf(stderr, "[s4864] HIST stores=%lu v0=%lu v1=%lu v2=%lu v3=%lu v4=%lu v5=%lu v6=%lu v7+=%lu synth=%lu resets=%lu incs=%lu\n", n, hist[0], hist[1], hist[2], hist[3], hist[4], hist[5], hist[6], hist[7], ent, rst, inc);
    last_ent = ent; last_rst = rst; last_inc = inc; last_t = t; fflush(stderr);
}
'''
t = p.read_text()
if "s4864" in t:
    print("already")
    raise SystemExit


def rep(anchor, call):
    global t
    assert t.count(anchor) == 1, (anchor, t.count(anchor))
    t = t.replace(anchor, call + anchor, 1)


D = "{ /* PATCH: s4864 */ extern void rs64_s4864_ev(int, unsigned); "
rep("    MEM_H(-0X68A0, ctx->r1) = 0;\n", "    " + D + "rs64_s4864_ev(1, 0); }\n")
rep("    MEM_H(-0X68A0, ctx->r1) = ctx->r2;\n", "    " + D + "rs64_s4864_ev(2, 0); }\n")
rep("    MEM_W(-0X6B5C, ctx->r1) = ctx->r6;\n", "    " + D + "rs64_s4864_ev(3, (unsigned)ctx->r6); }\n")
rep("    musyxSynthFrame_s4562_impl(rdram, ctx);\n", "    " + D + "rs64_s4864_ev(0, 0); }\n")
inc = '#include "recomp.h"\n'
t = t.replace(inc, inc + HELPER, 1)
p.write_text(t)
print("patched")
