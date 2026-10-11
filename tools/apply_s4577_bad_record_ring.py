#!/usr/bin/env python3
"""s4577: ring of the last 128 guest stores into voice records idx29/idx30 of the 0x801714D0 table (phys 0x172438..0x172548,
the bad record 0x801724C0 and its in-range-style neighbour), any PC, any width. Dumped when rs64_s4534_jal first sees the
exact ASCII a3 0x6C617465, together with the full 34-word contents of both records. Env ROGUESQ_LOG_S4577=1 (also needs
ROGUESQ_LOG_S4299=1 and ROGUESQ_LOG_S4534=1). Positive control: the idx29 neighbour rows must appear in the ring.
Diagnostic only. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
F24 = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
HOOK = r'''#include <mutex>
struct rs64_s4577_ent { uint32_t seq, pc, addr, val, vi_w; char w; };
static rs64_s4577_ent g_s4577_cb[64]; static unsigned g_s4577_ncb = 0;
static rs64_s4577_ent g_s4577_ring[128]; static unsigned g_s4577_n = 0; static std::mutex g_s4577_mu;
static void rs64_s4577_note(char w, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4577"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    const uint32_t p = addr & 0x1FFFFFFFu;
    if (p >= 0x1496F8u && p < 0x149704u) {
        std::lock_guard<std::mutex> g(g_s4577_mu);
        g_s4577_cb[g_s4577_ncb % 64] = {g_s4577_ncb, pc, addr, value, rs64_vi_committed_width(), w};
        g_s4577_ncb++;
        return;
    }
    if (p < 0x172438u || p >= 0x172548u) return;
    std::lock_guard<std::mutex> g(g_s4577_mu);
    g_s4577_ring[g_s4577_n % 128] = {g_s4577_n, pc, addr, value, rs64_vi_committed_width(), w};
    g_s4577_n++;
}
extern "C" void rs64_s4577_dump() {
    std::lock_guard<std::mutex> g(g_s4577_mu);
    std::fprintf(stderr, "[s4577-dump] total_stores=%u (ring keeps last 128)\n", g_s4577_n);
    for (unsigned i = g_s4577_ncb > 64 ? g_s4577_ncb - 64 : 0; i < g_s4577_ncb; i++) {
        const auto& e = g_s4577_cb[i % 64];
        std::fprintf(stderr, "[s4577-CB] seq=%u addr=%08X w=%c pc=%08X val=%08X vi_w=%u\n", e.seq, e.addr, e.w, e.pc, e.val, e.vi_w);
    }
    const unsigned n = g_s4577_n < 128 ? g_s4577_n : 128, start = g_s4577_n - n;
    for (unsigned i = start; i < g_s4577_n; i++) {
        const auto& e = g_s4577_ring[i % 128];
        std::fprintf(stderr, "[s4577-W] seq=%u rec=%u off=0x%02X w=%c pc=%08X val=%08X vi_w=%u\n", e.seq,
                     (unsigned)(((e.addr & 0x1FFFFFFFu) - 0x172438u) / 0x88u) + 29u, (unsigned)(((e.addr & 0x1FFFFFFFu) - 0x172438u) % 0x88u),
                     e.w, e.pc, e.val, e.vi_w);
    }
}
'''
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
if "rs64_s4577_note" not in t:
    a = "static void rs64_s4569_note("
    assert t.count(a) == 1
    t = t.replace(a, HOOK + a)
    b = '    rs64_s4569_note("st", width, pc, addr);\n'
    assert t.count(b) == 1
    t = t.replace(b, b + '    rs64_s4577_note(width, pc, addr, value);\n')
    f.write_text(t)
s = F24.read_text()
if "rs64_s4577_dump" not in s:
    m = "    if (bad) {\n        if (exact) {\n            if (exact_rows >= 4) return;"
    assert s.count(m) == 1
    INS = r'''    if (exact && exact_rows == 0) { rs64_s4577_dump(); for (int r_ = 0; r_ < 2; r_++) { uint32_t b_ = r_ ? 0x801724C0u : 0x80172438u; fprintf(stderr, "[s4577-rec] idx=%d base=%08X:", 29 + r_, b_); for (int k_ = 0; k_ < 34; k_++) fprintf(stderr, " %08X", (uint32_t)MEM_W(4 * k_, S32(b_))); fprintf(stderr, "\n"); } } /* PATCH: s4577 */
'''
    s = s.replace(m, INS + m)
    s = s.replace("/* PATCH: s4534 voice a3 callsite. Diagnostic only. */", "void rs64_s4577_dump(void);\n/* PATCH: s4534 voice a3 callsite. Diagnostic only. */", 1)
    F24.write_text(s)
print("ok")
