#!/usr/bin/env python3
"""s4569: widen the s4299 guest store filter (generated funcs_*.c) from 0x17D000..0x17E200 to also cover the three RDRAM copies of the
odd-DMA node (0x1120B0, 0x179A64, 0x17DBC8) and print EVERY guest store hitting those windows immediately with the store PC
(env ROGUESQ_LOG_S4569=1 plus ROGUESQ_LOG_S4299=1; positive control = first store anywhere in 0x17D000..0x17E200, which the old
filter already saw). swl/swr sites get the same immediate print. Run after apply_s4299*.py. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLDC = "if (nw_p >= 0x17C000u && nw_p < 0x180000u) rs64_s4299_store_watch"
NEWC = "if ((nw_p >= 0x17C000u && nw_p < 0x180000u) || (nw_p >= 0x179A50u && nw_p < 0x179A80u) || (nw_p >= 0x1120A0u && nw_p < 0x1120D0u)) rs64_s4299_store_watch"
HOOK = r'''static void rs64_s4569_note(const char* kind, char w, uint32_t pc, uint32_t addr) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4569"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    const uint32_t p = addr & 0x1FFFFFFFu;
    const bool tgt = (p >= 0x179A58u && p < 0x179A70u) || (p >= 0x1120A8u && p < 0x1120C0u) || (p >= 0x17DBC0u && p < 0x17DBD8u);
    static std::atomic<unsigned> ctl{0}, rows{0};
    if (!tgt) { if (p >= 0x17C000u && p < 0x180000u && ctl.fetch_add(1) == 0) std::fprintf(stderr, "[s4569-control] first non-target store in 0x17C000..0x180000 %s %c pc=%08X addr=%08X vi_w=%u\n", kind, w, pc, addr, rs64_vi_committed_width()); return; }
    if (rows.fetch_add(1) > 4000) return;
    std::fprintf(stderr, "[s4569-W] %s %c pc=%08X addr=%08X vi_w=%u\n", kind, w, pc, addr, rs64_vi_committed_width());
}
'''
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
if "rs64_s4569_note" not in t:
    a = 'extern "C" void rs64_s4299_store_watch(char width, uint32_t pc, uint32_t addr, uint32_t value) {\n    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4299")'
    assert t.count(a) == 1, t.count(a)
    t = t.replace(a, HOOK + a)
    b = "    if (!on) return;\n    (void)value;\n    const uint32_t phys = addr & 0x1FFFFFFFu;\n"
    assert t.count(b) == 1, t.count(b)
    t = t.replace(b, "    if (!on) return;\n    rs64_s4569_note(\"st\", width, pc, addr);\n    (void)value;\n    const uint32_t phys = addr & 0x1FFFFFFFu;\n")
    c = "    g_s4299_swlr_total++;\n"
    assert t.count(c) == 1
    t = t.replace(c, c + "    rs64_s4569_note(w == 'L' ? \"swl\" : \"swr\", w, line, addr);\n")
    f.write_text(t)
n = 0
for p in sorted(RF.glob("funcs_*.c")):
    s = p.read_text()
    if OLDC in s:
        p.write_text(s.replace(OLDC, NEWC)); n += 1
print("patched", n)
