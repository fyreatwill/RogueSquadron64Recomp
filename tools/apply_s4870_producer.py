"""s4870: port count of the ring-producer write 0x8008EE6C (kind 0, funcs_23) vs synth entries 0x8009123C (kind 1, funcs_24),
with sp and pthread id, and a histogram of producer writes between consecutive synth entries.
Retail expectation: 1 producer per synth entry (measured by oracle exec watch on the same PCs).
Control: producers_total == sum(hist[k]*k) + producers since last entry. Gate ROGUESQ_LOG_S4864=1.
ORIGIN: read-only logging. Idempotent live-tree patch."""
from pathlib import Path
base = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
HELPER = r'''
/* PATCH: s4870 producer/entry helper */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
void rs64_s4870_ev(int kind, unsigned sp) {
    static int enabled = -1; static unsigned long prod, ent, between, hist[5];
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    unsigned long tid = (unsigned long)(uintptr_t)pthread_self();
    if (kind == 0) { prod++; between++; if (prod <= 24) fprintf(stderr, "[s4870] PROD#%lu sp=%08x tid=%lx\n", prod, sp, tid); }
    else { ent++; hist[between < 4 ? between : 4]++; between = 0;
        if (ent <= 24) fprintf(stderr, "[s4870] ENT#%lu sp=%08x tid=%lx prod_total=%lu\n", ent, sp, tid, prod);
        if ((ent & 255) == 0) fprintf(stderr, "[s4870] SUMMARY ent=%lu prod=%lu prod_between_entries 0:%lu 1:%lu 2:%lu 3:%lu 4+:%lu\n", ent, prod, hist[0], hist[1], hist[2], hist[3], hist[4]); }
    fflush(stderr);
}
'''
def patch(fn, anchor, call, helper=False):
    p = base / fn; t = p.read_text()
    if "s4870" in t: print(fn, "already"); return
    assert t.count(anchor) == 1, (fn, t.count(anchor))
    t = t.replace(anchor, "    { extern void rs64_s4870_ev(int, unsigned); " + call + " } /* PATCH: s4870 */\n" + anchor, 1)
    inc = '#include "recomp.h"\n'; t = t.replace(inc, inc + HELPER, 1) if helper else t
    p.write_text(t); print(fn, "patched")
patch("funcs_23.c", "    // 0x8008EE6C: sb          $v0, -0x6910($at)\n", "rs64_s4870_ev(0, (unsigned)ctx->r29);", helper=True)
patch("funcs_24.c", "    // 0x8009123C: addiu       $sp, $sp, -0x40\n", "rs64_s4870_ev(1, (unsigned)ctx->r29);")
