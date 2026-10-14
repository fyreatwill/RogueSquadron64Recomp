"""s4867: loop-bound halfword 0x8014974E trace (extends s4864). Kinds: 10=bound writer (0x8008F20C, val=new bound,
ra=ctx->r31), 11=reset (0x8009106C, ra), 12=incr (0x800911DC, a=bound re-read from 0x8014974E, b=counter after incr).
Gate ROGUESQ_LOG_S4864=1. Prints every bound write, first 60 resets/incrs, and SUMMARY lines (bound histogram at incr,
reset-ra histogram) every 512 incrs and at reset #100.
Positive control: summed bound0..3+ at incr must equal the s4864 incs total at the same HIST line.
ORIGIN: read-only logging. Idempotent live-tree patch; apply after apply_s4864_datasize_trace.py."""
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
HELPER = r'''
/* PATCH: s4867 bound helper */
#include <stdio.h>
#include <stdlib.h>
void rs64_s4867_ev(int kind, unsigned a, unsigned b) {
    static int enabled = -1; static unsigned long cnt[3]; static unsigned long ra_hist[8]; static unsigned ra_key[8]; static unsigned long bnd[4];
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    int k = kind - 10; unsigned long n = __atomic_add_fetch(&cnt[k], 1, __ATOMIC_SEQ_CST);
    if (k == 0) { fprintf(stderr, "[s4867] WRITE_BOUND#%lu val=%u ra=0x%08x\n", n, a, b); fflush(stderr); return; }
    if (k == 1) { if (n <= 60) fprintf(stderr, "[s4867] RESET#%lu ra=0x%08x\n", n, b);
        for (int i = 0; i < 8; i++) { if (ra_key[i] == b || ra_key[i] == 0) { ra_key[i] = b; ra_hist[i]++; break; } } }
    if (k == 2) { bnd[a < 3 ? a : 3]++; if (n <= 60) fprintf(stderr, "[s4867] INCR#%lu bound=%u counter_after=%u\n", n, a, b); }
    if ((k == 2 && (n & 511) == 0) || (k == 1 && n == 100)) {
        fprintf(stderr, "[s4867] SUMMARY kind=%d n=%lu incr_bound0=%lu bound1=%lu bound2=%lu bound3+=%lu reset_ra:", kind, n, bnd[0], bnd[1], bnd[2], bnd[3]);
        for (int i = 0; i < 8 && ra_key[i]; i++) fprintf(stderr, " 0x%08x:%lu", ra_key[i], ra_hist[i]);
        fprintf(stderr, "\n");
    }
    fflush(stderr);
}
'''


def patch(fn, edits, helper=None):
    p = root / fn
    t = p.read_text()
    if "s4867" in t:
        print(fn, "already")
        return
    for anchor, call in edits:
        assert t.count(anchor) == 1, (fn, anchor, t.count(anchor))
        t = t.replace(anchor, call + anchor, 1)
    if helper:
        inc = '#include "recomp.h"\n'
        t = t.replace(inc, inc + helper, 1)
    p.write_text(t)
    print(fn, "patched")


D = "{ /* PATCH: s4867 */ extern void rs64_s4867_ev(int, unsigned, unsigned); "
patch("funcs_23.c", [("    MEM_H(-0X68B2, ctx->r1) = ctx->r3;\n",
                      "    " + D + "rs64_s4867_ev(10, (unsigned)(ctx->r3 & 0xFFFF), (unsigned)ctx->r31); }\n")])
patch("funcs_24.c", [
    ("    { /* PATCH: s4864 */ extern void rs64_s4864_ev(int, unsigned); rs64_s4864_ev(1, 0); }\n",
     "    " + D + "rs64_s4867_ev(11, 0, (unsigned)ctx->r31); }\n"),
    ("    { /* PATCH: s4864 */ extern void rs64_s4864_ev(int, unsigned); rs64_s4864_ev(2, 0); }\n",
     "    " + D + "rs64_s4867_ev(12, (unsigned)MEM_HU(-0X68B2, ctx->r1), (unsigned)(ctx->r2 & 0xFFFF)); }\n"),
], HELPER)
