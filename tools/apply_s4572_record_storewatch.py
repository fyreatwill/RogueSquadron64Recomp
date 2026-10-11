#!/usr/bin/env python3
"""s4572: dynamic guest-store watch on the two musyx render-record tables (tbl0/tbl1 at 0x80149708/0C, cap records of 0x88 bytes,
published from allocateSongChannelArray) plus the per-buffer cursor halfwords 0x80149710/12, and a 34-word dump of the first six
chunk-2+ records with an ASCII-word tally over all 34 words. Env ROGUESQ_LOG_S4572=1 (also needs ROGUESQ_LOG_S4299=1 for the hook
entry and ROGUESQ_LOG_S4571=1 for the record dump). Prints store PC / idx / word-offset, first 60 rows per class (vi_w>=512) and a
per-(class,PC) histogram every 20000 stores. Positive control = in-range (idx<count) stores must fire. Needs apply_s4569 + s4571b/c. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
HOOK = r'''#include <map>
#include <mutex>
static std::atomic<uint32_t> g_s4572_t0{0}, g_s4572_t1{0}, g_s4572_cap{0}, g_s4572_cnt{0};
extern "C" void rs64_s4572_publish(uint32_t t0, uint32_t t1, uint32_t cap, uint32_t cnt) {
    g_s4572_t0 = t0; g_s4572_t1 = t1; g_s4572_cap = cap; g_s4572_cnt = cnt;
    std::fprintf(stderr, "[s4572-pub] tbl0=%08X tbl1=%08X cap=%u count=%u\n", t0, t1, cap, cnt);
}
extern "C" void rs64_s4572_setcount(uint32_t cnt) { g_s4572_cnt = cnt; }
static void rs64_s4572_note(const char* kind, char w, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4572"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    const uint32_t p = addr & 0x1FFFFFFFu;
    static std::atomic<unsigned> rows[3]{}, tot[3]{}, all{0};
    static std::mutex mu; static std::map<uint64_t, unsigned> hist;
    int cls = -1; uint32_t idx = 0, off = 0, buf = 0;
    if (p >= 0x149700u && p < 0x149720u) { cls = 2; off = p - 0x149700u; }
    else {
        const uint32_t cap = g_s4572_cap, cnt = g_s4572_cnt;
        for (int b = 0; b < 2 && cls < 0; b++) {
            const uint32_t t = (b ? g_s4572_t1 : g_s4572_t0) & 0x1FFFFFFFu;
            if (t && p >= t && p < t + cap * 0x88u) { idx = (p - t) / 0x88u; off = (p - t) % 0x88u; buf = b; cls = idx < cnt ? 0 : 1; }
        }
    }
    if (cls < 0) return;
    tot[cls]++;
    { std::lock_guard<std::mutex> g(mu); hist[((uint64_t)cls << 32) | pc]++; }
    if (rs64_vi_committed_width() >= 512u && rows[cls].fetch_add(1) < 60)
        std::fprintf(stderr, "[s4572-W] %s %c cls=%s buf=%u idx=%u off=%u pc=%08X addr=%08X val=%08X vi_w=%u\n", kind, w,
                     cls == 2 ? "cursor" : cls ? "chunk2+" : "inrange", buf, idx, off, pc, addr, value, rs64_vi_committed_width());
    if ((++all % 20000u) == 0 && (all / 20000u) <= 20) {
        std::lock_guard<std::mutex> g(mu);
        std::fprintf(stderr, "[s4572-tot] stores inrange=%u chunk2+=%u cursor=%u\n", tot[0].load(), tot[1].load(), tot[2].load());
        for (auto& kv : hist) std::fprintf(stderr, "[s4572-hist] cls=%u pc=%08X n=%u\n", (unsigned)(kv.first >> 32), (unsigned)kv.first, kv.second);
    }
}
'''
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
if "rs64_s4572_note" not in t:
    a = "static void rs64_s4569_note("
    assert t.count(a) == 1
    t = t.replace(a, HOOK + a)
    b = '    rs64_s4569_note("st", width, pc, addr);\n'
    assert t.count(b) == 1
    t = t.replace(b, b + '    rs64_s4572_note("st", width, pc, addr, value);\n')
    c = "    rs64_s4569_note(w == 'L' ? \"swl\" : \"swr\", w, line, addr);\n"
    assert t.count(c) == 1
    t = t.replace(c, c + "    rs64_s4572_note(w == 'L' ? \"swl\" : \"swr\", w, line, addr, 0);\n")
    f.write_text(t)
OLDC = "(nw_p >= 0x1120A0u && nw_p < 0x1120D0u)) rs64_s4299_store_watch"
NEWC = "(nw_p >= 0x1120A0u && nw_p < 0x1120D0u) || (nw_p >= 0x149700u && nw_p < 0x149720u) || (nw_p >= 0x170000u && nw_p < 0x1A0000u)) rs64_s4299_store_watch"
n = 0
for p in sorted(RF.glob("funcs_*.c")):
    s = p.read_text()
    if OLDC in s:
        p.write_text(s.replace(OLDC, NEWC)); n += 1
print("filter patched", n)
# publish at alloc
p = RF / "funcs_23.c"; s = p.read_text()
if "s4572" not in s:
    a = "    { /* PATCH: s4571c zero render-record tables"
    assert s.count(a) == 1
    s = s.replace(a, "    { extern void rs64_s4572_publish(uint32_t,uint32_t,uint32_t,uint32_t); rs64_s4572_publish((uint32_t)MEM_W(-0X68F8, S32(0x8015 << 16)), (uint32_t)ctx->r2, (uint32_t)MEM_HU(-0X68FC, S32(0x8015 << 16)), (uint32_t)MEM_HU(-0x6900, S32(0x8015 << 16))); } /* PATCH: s4572 publish */\n" + a)
    p.write_text(s)
p = RF / "funcs_24.c"; s = p.read_text()
if "rs64_s4572_dump34" not in s:
    D = r'''extern void rs64_s4572_setcount(uint32_t);
static void rs64_s4572_dump34(uint8_t* rdram, uint32_t a3, uint32_t idx, uint32_t count) {
    if (!rs64_s4571_on()) return;
    rs64_s4572_setcount(count);
    static unsigned rows = 0, nrec[2] = {0, 0}, nasc[2] = {0, 0};
    const int c = idx >= count ? 1 : 0;
    unsigned asc = 0;
    for (int i = 0; i < 34; i++) { uint32_t w = (uint32_t)MEM_W(i * 4, (int32_t)a3); if (rs64_s4571_ascii_word(w)) asc++; }
    nrec[c]++; nasc[c] += asc;
    if ((c && rows < 6) || (asc && rows < 40)) {
        rows++;
        fprintf(stderr, "[s4572-rec] cls=%s idx=%u a3=0x%08X ascii34=%u w:", c ? "chunk2+" : "inrange", idx, a3, asc);
        for (int i = 0; i < 34; i++) fprintf(stderr, " %08X", (uint32_t)MEM_W(i * 4, (int32_t)a3));
        fprintf(stderr, "\n");
    }
    if (((nrec[0] + nrec[1]) % 4000u) == 0) fprintf(stderr, "[s4572-rtot] inrange n=%u asciirecs=%u | chunk2+ n=%u asciiwords=%u\n", nrec[0], nasc[0], nrec[1], nasc[1]);
}
'''
    sig = "\nRECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
    assert s.count(sig) == 1
    s = s.replace(sig, "\n" + D + sig[1:])
    post = "    rs64_s4571_post(rdram, s4571_a3, s4571_idx, s4571_cnt); }\n"
    assert s.count(post) == 1
    s = s.replace(post, "    rs64_s4571_post(rdram, s4571_a3, s4571_idx, s4571_cnt); rs64_s4572_dump34(rdram, s4571_a3, s4571_idx, s4571_cnt); }\n")
    p.write_text(s)
print("done")
