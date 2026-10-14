"""s4868: synth-frame branch trace (extends s4864/s4867). Retail (oracle s4867b): per 703 synth entries -> 703 builds,
703 hits of L_800916A8, 0 hits of L_800917E0, 702 data_size stores, i.e. branch 0x80091390 ALWAYS taken.
Port question: is 0x80091390 (v1=MEM_HU 0x80149988... -0x6678, v0=s4&0xFFFF) taken on every entry or only every other one?
Kinds: 0=branch eval at 0x80091390 (a=v1, b=v0), 1=L_800917E0 reached, 2=L_800916A8 reached. Gate ROGUESQ_LOG_S4864=1.
First 40 branch rows + SUMMARY (eq/ne/e0/a8 counts, distinct (v1,v0) pairs top-4) at every 256th eval.
Positive control: eq+ne == s4867 resets-ish synth entries; a8 count == eq count (taken path) -- label hit must track branch.
ORIGIN: read-only logging. Idempotent live-tree patch."""
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_24.c"
HELPER = r'''
/* PATCH: s4868 branch helper */
#include <stdio.h>
#include <stdlib.h>
void rs64_s4868_ev(int kind, unsigned a, unsigned b) {
    static int enabled = -1; static unsigned long ev, eq, ne, e0, a8; static unsigned key[4][2]; static unsigned long kc[4];
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    if (kind == 1) { __atomic_add_fetch(&e0, 1, __ATOMIC_SEQ_CST); return; }
    if (kind == 2) { __atomic_add_fetch(&a8, 1, __ATOMIC_SEQ_CST); return; }
    unsigned long n = __atomic_add_fetch(&ev, 1, __ATOMIC_SEQ_CST);
    if (a == b) eq++; else ne++;
    for (int i = 0; i < 4; i++) { if ((key[i][0] == a && key[i][1] == b) || kc[i] == 0) { key[i][0] = a; key[i][1] = b; kc[i]++; break; } }
    if (n <= 40) fprintf(stderr, "[s4868] BR#%lu v1=%u v0=%u %s\n", n, a, b, a == b ? "TAKEN" : "FALL");
    if ((n & 255) == 0 || n == 100) {
        fprintf(stderr, "[s4868] SUMMARY evals=%lu eq=%lu ne=%lu exit_800917E0=%lu reached_800916A8=%lu pairs:", n, eq, ne, e0, a8);
        for (int i = 0; i < 4 && kc[i]; i++) fprintf(stderr, " (%u,%u):%lu", key[i][0], key[i][1], kc[i]);
        fprintf(stderr, "\n"); fflush(stderr);
    }
}
'''
t = p.read_text()
if "s4868" in t:
    print("already")
    raise SystemExit
D = "{ /* PATCH: s4868 */ extern void rs64_s4868_ev(int, unsigned, unsigned); "
a1 = "    // 0x80091390: beq         $v1, $v0, L_800916A8\n"
assert t.count(a1) == 1
t = t.replace(a1, "    " + D + "rs64_s4868_ev(0, (unsigned)ctx->r3, (unsigned)ctx->r2); }\n" + a1, 1)
for lab, k in (("L_800917E0:\n", 1), ("L_800916A8:\n", 2)):
    assert t.count(lab) == 1, lab
    t = t.replace(lab, lab + "    " + D + "rs64_s4868_ev(%d, 0, 0); }\n" % k, 1)
inc = '#include "recomp.h"\n'
t = t.replace(inc, inc + HELPER, 1)
p.write_text(t)
print("patched")
