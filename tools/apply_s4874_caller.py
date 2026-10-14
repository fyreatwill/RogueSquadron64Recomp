"""s4874: per-synth-entry caller (r31) + AI-done message delta since previous entry. Gate ROGUESQ_LOG_S4864=1.
Builds on apply_s4873_msgrate.py (run it first). Retail twin: oracle exec-prev at 0x8009123C.
ORIGIN: read-only counters. Idempotent live-tree patch."""
from pathlib import Path
base = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
p = base / "funcs_24.c"; t = p.read_text()
if "s4874" in t: print("already"); raise SystemExit
old = "{ extern void rs64_s4873_ev(int); rs64_s4873_ev(1); } /* PATCH: s4873 */"
assert t.count(old) == 1
t = t.replace(old, "{ extern void rs64_s4873_ev(int); rs64_s4873_ev(1); { extern void rs64_s4874_ra(unsigned); rs64_s4874_ra(U32(ctx->r31)); } } /* PATCH: s4873 s4874 */", 1)
helper = r'''
/* PATCH: s4874 caller helper */
void rs64_s4874_ra(unsigned ra) {
    static unsigned long last_msgs, n; static unsigned ras[16]; static unsigned long cnt[16]; static int nra;
    extern unsigned long rs64_s4873_n[2];
    static int enabled = -1;
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4864"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    unsigned long d = rs64_s4873_n[0] - last_msgs; last_msgs = rs64_s4873_n[0]; n++;
    int i; for (i = 0; i < nra && ras[i] != ra; i++) {}
    if (i == nra && nra < 16) { ras[nra] = ra; cnt[nra] = 0; nra++; }
    if (i < 16) cnt[i]++;
    if (n > 200 && n <= 260) fprintf(stderr, "[s4873] ENTRY n=%lu ra=0x%08X dmsgs=%lu\n", n, ra, d);
    if ((n & 255) == 0) { for (int k = 0; k < nra; k++) fprintf(stderr, "[s4873] RA 0x%08X x%lu\n", ras[k], cnt[k]); fflush(stderr); }
}
'''
inc = "unsigned long rs64_s4873_n[2];\n"
assert inc in t or True
t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + helper, 1)
p.write_text(t); print("patched")
