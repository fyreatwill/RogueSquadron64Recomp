"""s4873: AI-done message rate vs synth entry rate. Counts hits of L_8008EE44 (value-1 message branch in
runAiAudioStreamPlaybackLoop, funcs_23.c) and musyxSynthFrame entry 0x8009123C (funcs_24.c). Gate ROGUESQ_LOG_S4864=1.
Retail twin: oracle --watch-pc 0x8008EE44,0x8009123C. ORIGIN: read-only counters. Idempotent live-tree patch."""
from pathlib import Path
base = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
HELPER = r'''
/* PATCH: s4873 msg-rate helper */
#include <stdio.h>
#include <stdlib.h>
unsigned long rs64_s4873_n[2];
void rs64_s4873_ev(int which) {
    static int enabled = -1;
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    rs64_s4873_n[which]++;
    if (which == 1 && (rs64_s4873_n[1] & 63) == 0) { fprintf(stderr, "[s4873] SUMMARY synth_entries=%lu msgs_v1=%lu\n", rs64_s4873_n[1], rs64_s4873_n[0]); fflush(stderr); }
}
'''
def patch(fn, anchor, which):
    p = base / fn; t = p.read_text()
    if "s4873" in t: print(fn, "already"); return
    assert t.count(anchor) == 1, (fn, t.count(anchor))
    t = t.replace(anchor, anchor + "    { extern void rs64_s4873_ev(int); rs64_s4873_ev(%d); } /* PATCH: s4873 */\n" % which, 1)
    if which == 1:
        inc = '#include "recomp.h"\n'; assert inc in t
        t = t.replace(inc, inc + HELPER, 1)
    else:
        inc = '#include "recomp.h"\n'; assert inc in t
        t = t.replace(inc, inc + "extern void rs64_s4873_ev(int);\n", 1)
    p.write_text(t); print(fn, "patched")
patch("funcs_23.c", "L_8008EE44:\n", 0)
patch("funcs_24.c", "    rs64_m5_synth_parent_gate_event(0x8009123Cu, 0u, 0u, 0u, 0u, 0u, 0u, U32(ctx->r31)); /* PATCH: musyxSynthFrame parent entry 0x8009123C */\n", 1)
