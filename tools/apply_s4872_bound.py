"""s4872: chunk-loop bound census in musyxSynthFrame_s4562_impl at 0x80091418 (loop setup).
Logs s4 (&0xFFFF), halfword 0x80149988 (start), halfword 0x8014974E (cap), byte 0x801496F0. Histogram of chunks=max(s4-start,0).
Retail twin: oracle --watch-pc 0x80091418 with RS64_ORACLE_PEEK=1496F0,149988,14974C (prints s4 in gpr fields). Gate ROGUESQ_LOG_S4864=1.
ORIGIN: read-only logging. Idempotent live-tree patch."""
from pathlib import Path
base = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
HELPER = r'''
/* PATCH: s4872 bound census helper */
#include <stdio.h>
#include <stdlib.h>
void rs64_s4872_ev(unsigned s4, unsigned start, unsigned cap, unsigned b6f0) {
    static int enabled = -1; static unsigned long n, h[10], s4h[18];
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    n++; s4 &= 0xFFFF; start &= 0xFFFF;
    unsigned c = s4 > start ? s4 - start : 0; h[c < 9 ? c : 9]++; s4h[s4 < 17 ? s4 : 17]++;
    if (n <= 40) fprintf(stderr, "[s4872] ENTRY#%lu s4=%u start=%u cap=%u b6f0=%u chunks=%u\n", n, s4, start, cap & 0xFFFF, b6f0 & 0xFF, c);
    if ((n & 255) == 0) { fprintf(stderr, "[s4872] SUMMARY n=%lu chunks 0:%lu 1:%lu 2:%lu 3:%lu 4:%lu 5:%lu 6:%lu 7:%lu 8:%lu 9+:%lu | s4hist", n, h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[8],h[9]);
        for (int i = 0; i < 18; i++) fprintf(stderr, " %d:%lu", i, s4h[i]); fprintf(stderr, "\n"); }
    fflush(stderr);
}
'''
p = base / "funcs_24.c"; t = p.read_text()
if "s4872" in t:
    print("already"); raise SystemExit
anchor = "    // 0x80091418: addu        $s2, $zero, $zero\n"
assert t.count(anchor) == 1, t.count(anchor)
call = ("    { extern void rs64_s4872_ev(unsigned, unsigned, unsigned, unsigned); rs64_s4872_ev((unsigned)ctx->r20, "
        "(unsigned)MEM_HU((int32_t)0x80150000, -0x6678), (unsigned)MEM_HU((int32_t)0x80150000, -0x68B2), (unsigned)MEM_BU((int32_t)0x80150000, -0x6910)); } /* PATCH: s4872 */\n")
t = t.replace(anchor, call + anchor, 1)
inc = '#include "recomp.h"\n'
assert inc in t
t = t.replace(inc, inc + HELPER, 1)
p.write_text(t); print("patched")
