"""s4871: port voice-walk census to compare with retail oracle.
Events (funcs_24): 0 = walk entry 0x80090E04, 1 = per-voice jal 0x8008FFAC (0x80090F00), 2 = build call 0x80091330 (a1=r5).
Histograms: a1 at the build call; per-walk voice jal count. Control: hist sums equal event counts.
Retail via oracle exec watch 0x80090E04,0x80090F00,0x80091084(v0=a1),0x80091330. Gate ROGUESQ_LOG_S4864=1.
ORIGIN: read-only logging. Idempotent live-tree patch."""
from pathlib import Path
base = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
HELPER = r'''
/* PATCH: s4871 voice census helper */
#include <stdio.h>
#include <stdlib.h>
void rs64_s4871_ev(int kind, unsigned v) {
    static int enabled = -1; static unsigned long walks, jals, builds, curjal, a1h[8], jh[8];
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    if (kind == 0) { if (walks) jh[curjal < 7 ? curjal : 7]++; walks++; curjal = 0; }
    else if (kind == 1) { jals++; curjal++; }
    else { builds++; a1h[(v & 0xFFFF) < 7 ? (v & 0xFFFF) : 7]++;
        if (builds <= 24) fprintf(stderr, "[s4871] BUILD#%lu a1=%u walks=%lu jals=%lu curjal=%lu\n", builds, v & 0xFFFF, walks, jals, curjal);
        if ((builds & 255) == 0) { fprintf(stderr, "[s4871] SUMMARY builds=%lu walks=%lu jals=%lu a1hist 0:%lu 1:%lu 2:%lu 3:%lu 4:%lu 5:%lu 6:%lu 7+:%lu jals_per_walk 0:%lu 1:%lu 2:%lu 3:%lu 4:%lu 5+:%lu\n",
            builds, walks, jals, a1h[0], a1h[1], a1h[2], a1h[3], a1h[4], a1h[5], a1h[6], a1h[7], jh[0], jh[1], jh[2], jh[3], jh[4], jh[5]+jh[6]+jh[7]); } }
    fflush(stderr);
}
'''
p = base / "funcs_24.c"; t = p.read_text()
if "s4871" in t:
    print("already"); raise SystemExit
def ins(anchor, call):
    global t
    assert t.count(anchor) == 1, (anchor, t.count(anchor))
    t = t.replace(anchor, "    { extern void rs64_s4871_ev(int, unsigned); " + call + " } /* PATCH: s4871 */\n" + anchor, 1)
ins("    // 0x80090E04: addiu       $sp, $sp, -0x50\n", "rs64_s4871_ev(0, 0);")
ins("    // 0x80090F00: jal         0x8008FFAC\n", "rs64_s4871_ev(1, 0);")
ins("    // 0x80091330: jal         0x80091034\n", "rs64_s4871_ev(2, (unsigned)ctx->r5);")
inc = '#include "recomp.h"\n'
assert inc in t
t = t.replace(inc, inc + HELPER, 1)
p.write_text(t); print("patched")
