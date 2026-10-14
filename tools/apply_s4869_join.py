"""s4869: per-entry join in the port: result of branch 0x80091390 (kind 0 sets last_br) x counter a2 at 0x800916F0
(kind 1) x ring producer byte 0x801496F0. Prints joint histogram [br eq/ne][counter 0/1/2+] every 256 evals + first 24 rows.
Retail expectation (oracle s4867b): eq always, counter>0 (store 702/703). Control: sum of joint cells == number of kind-1 events.
Gate ROGUESQ_LOG_S4864=1. ORIGIN: read-only logging. Idempotent live-tree patch; apply after s4868."""
from pathlib import Path
p = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_24.c"
HELPER = r'''
/* PATCH: s4869 join helper */
#include <stdio.h>
#include <stdlib.h>
void rs64_s4869_ev(int kind, unsigned a, unsigned b) {
    static int enabled = -1; static int last_br = -1; static unsigned long j[2][3], n; static unsigned long dprod;
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    if (kind == 0) { last_br = (a == b); return; }
    n++; unsigned c = a < 2 ? a : 2; if (last_br >= 0) j[last_br][c]++;
    if (n <= 24) fprintf(stderr, "[s4869] ENTRY#%lu br_eq=%d counter=%u prod_byte=%u\n", n, last_br, a, b);
    if ((n & 255) == 0) fprintf(stderr, "[s4869] JOIN n=%lu ne:c0=%lu c1=%lu c2+=%lu | eq:c0=%lu c1=%lu c2+=%lu\n", n, j[0][0], j[0][1], j[0][2], j[1][0], j[1][1], j[1][2]);
    last_br = -1; fflush(stderr);
}
'''
t = p.read_text()
if "s4869" in t:
    print("already"); raise SystemExit
D = "{ /* PATCH: s4869 */ extern void rs64_s4869_ev(int, unsigned, unsigned); "
a1 = "    // 0x80091390: beq         $v1, $v0, L_800916A8\n"
assert t.count(a1) == 1
t = t.replace(a1, "    " + D + "rs64_s4869_ev(0, (unsigned)ctx->r3, (unsigned)ctx->r2); }\n" + a1, 1)
a2 = "    // 0x800916F0: beq         $a2, $zero, L_800917AC\n"
assert t.count(a2) == 1
t = t.replace(a2, "    " + D + "rs64_s4869_ev(1, (unsigned)(ctx->r6 & 0xFFFF), (unsigned)MEM_BU(-0x6910, S32(0X8015 << 16))); }\n" + a2, 1)
inc = '#include "recomp.h"\n'
t = t.replace(inc, inc + HELPER, 1)
p.write_text(t); print("patched")
