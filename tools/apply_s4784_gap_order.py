"""s4784: port-side ordering probe. Logs [s4784] rows for musyxNoopStub entry/gate-clear and musyxSynthFrame
entries (tid + monotonic seq) so stderr interleaving with the existing [rs_free]/[rs_malloc] rows (ROGUESQ_LOG_RS_FREE/
RS_MALLOC) shows whether the port ticks the synth between teardown free burst and re-init.
Gate: ROGUESQ_LOG_S4784=1. Control: every 256th synth tick row + total. Synth rows inside a noop window are capped at 600.
ORIGIN: read-only logging. Live-tree patch (full regen broken, REGEN WARNING s4204). Idempotent."""
from pathlib import Path

base = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
HELPER = r'''
/* PATCH: s4784 gap order helper */
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
void rs64_s4784_ev(uint8_t* rdram, int kind) {
    static int enabled = -1; static unsigned long seq, synth, post, win;
    static volatile int in_noop;
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4784"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    unsigned long sq = __atomic_add_fetch(&seq, 1, __ATOMIC_SEQ_CST);
    unsigned long tid = (unsigned long)(uintptr_t)pthread_self();
    if (kind == 0) { __atomic_store_n(&in_noop, 1, __ATOMIC_SEQ_CST); __atomic_store_n(&win, 0, __ATOMIC_SEQ_CST);
        fprintf(stderr, "[s4784] seq=%lu tid=%lx NOOP-ENTER gate=%02X synth_total=%lu\n", sq, tid, (unsigned)MEM_BU(0, S32(0x800A0F50u)), synth); }
    else if (kind == 2) { __atomic_store_n(&in_noop, 2, __ATOMIC_SEQ_CST); __atomic_store_n(&win, 0, __ATOMIC_SEQ_CST);
        fprintf(stderr, "[s4784] seq=%lu tid=%lx GATE-CLEAR synth_in_window=%lu synth_total=%lu\n", sq, tid, win, synth); }
    else { unsigned long n = __atomic_add_fetch(&synth, 1, __ATOMIC_SEQ_CST);
        if (__atomic_load_n(&in_noop, __ATOMIC_SEQ_CST) == 2) { unsigned long w = __atomic_add_fetch(&win, 1, __ATOMIC_SEQ_CST);
            if (w <= 400) fprintf(stderr, "[s4784] seq=%lu tid=%lx SYNTH-POST w=%lu\n", sq, tid, w); }
        else if (__atomic_load_n(&in_noop, __ATOMIC_SEQ_CST)) { unsigned long w = __atomic_add_fetch(&win, 1, __ATOMIC_SEQ_CST);
            if (post++ < 600) fprintf(stderr, "[s4784] seq=%lu tid=%lx SYNTH-IN-NOOP w=%lu\n", sq, tid, w); }
        else if ((n & 255) == 1) fprintf(stderr, "[s4784] seq=%lu tid=%lx SYNTH-CONTROL n=%lu\n", sq, tid, n); }
    fflush(stderr);
}
'''
DECL = "extern void rs64_s4784_ev(uint8_t*, int);"


def patch(fname, anchor, call, helper=False):
    p = base / fname
    t = p.read_text()
    if call in t:
        print("already", fname)
        return
    assert t.count(anchor) == 1, (fname, anchor, t.count(anchor))
    t = t.replace(anchor, call + anchor, 1)
    if helper and "PATCH: s4784 gap order helper" not in t:
        inc = '#include "recomp.h"\n'
        assert t.count(inc) == 1
        t = t.replace(inc, inc + HELPER, 1)
    p.write_text(t)
    print("patched", p)


patch("funcs_23.c", "    // 0x8008ED00: lui         $v0, 0x800A\n",
      "    { /* PATCH: s4784 noop-enter */ " + DECL + " rs64_s4784_ev(rdram, 0); }\n", helper=True)
patch("funcs_23.c", '        rs64_s2031_m5_gate_event(rdram, "writer", "musyxNoopStub:noop-exit", 0x8008ED48u,',
      "        { /* PATCH: s4784 gate-clear */ " + DECL + " rs64_s4784_ev(rdram, 2); }\n")
patch("funcs_24.c", "    musyxSynthFrame_s4562_impl(rdram, ctx);\n",
      "    { /* PATCH: s4784 synth */ " + DECL + " rs64_s4784_ev(rdram, 1); }\n")
