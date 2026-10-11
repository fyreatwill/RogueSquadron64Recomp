#!/usr/bin/env python3
"""s4578: host-thread poll of the MusyX voice-count halfword (phys 0x149700) + ring of host writes (the census hook).
Prints [s4578-change] with old/new/words 0x1496F8..0x14971F and the last 16 host writes at every change, and
[s4578-HOSTWRITE-OVERLAP] for any host write overlapping 0x149700..0x149720. When new>18 also dumps the s4577 store ring.
Env ROGUESQ_LOG_S4578=1. Positive control: the allocator guest store (15->18) must appear as a poll change.
Diagnostic only. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
f = R / "src/main/main.cpp"
t = f.read_text()
if "s4578_poll" in t:
    print("already applied")
    raise SystemExit(0)
A = '''extern "C" void rs64_m5_host_write_census(uint8_t* rdram,
                                            uint32_t phys,
                                            uint32_t len,
                                            const char* api) {
'''
B = '''    if (!enabled || !rdram || len == 0u) return;
    static std::atomic<uint32_t> api_mask{0};'''
assert t.count(A) == 1 and t.count(B) == 1
NEW = r'''// s4578: host-thread poll of the MusyX voice-count halfword (phys 0x149700) plus a ring of host writes.
extern "C" void rs64_s4577_dump();
namespace {
struct S4578Hw { uint32_t seq, phys, len, vi_w; char api[24]; };
S4578Hw g_s4578_ring[16]; uint32_t g_s4578_n = 0; std::mutex g_s4578_mu;
std::atomic<uint32_t> g_s4578_total{0}, g_s4578_page{0};
std::atomic<bool> g_s4578_started{false};
bool s4578_on() {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4578"); return e && e[0] && e[0] != '0'; }();
    return on;
}
void s4578_poll(uint8_t* rdram) {
    auto hw = [&] { return (uint32_t)*(volatile uint16_t*)(rdram + (0x149700u ^ 2u)); };
    uint32_t last = hw(); uint32_t changes = 0;
    std::fprintf(stderr, "[s4578-start] initial=%u\n", last);
    for (;;) {
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        const uint32_t cur = hw();
        if (cur == last) continue;
        std::fprintf(stderr, "[s4578-change] n=%u old=%u new=%u vi_w=%u host_total=%u host_page=%u words:", changes++, last, cur,
                     rs64_vi_committed_width(), g_s4578_total.load(), g_s4578_page.load());
        for (uint32_t p = 0x1496F8u; p < 0x149720u; p += 4) std::fprintf(stderr, " %08X", *(volatile uint32_t*)(rdram + p));
        std::fprintf(stderr, "\n");
        {
            std::lock_guard<std::mutex> g(g_s4578_mu);
            const uint32_t n = g_s4578_n < 16 ? g_s4578_n : 16;
            for (uint32_t i = g_s4578_n - n; i < g_s4578_n; i++) {
                const auto& e = g_s4578_ring[i % 16];
                std::fprintf(stderr, "[s4578-hostring] seq=%u phys=%06X len=%X api=%s vi_w=%u\n", e.seq, e.phys, e.len, e.api, e.vi_w);
            }
        }
        if (cur > 18) rs64_s4577_dump();
        std::fflush(stderr);
        last = cur;
    }
}
}  // namespace
extern "C" void rs64_s4578_start(uint8_t* rdram) {
    if (!s4578_on() || !rdram) return;
    bool exp = false;
    if (!g_s4578_started.compare_exchange_strong(exp, true)) return;
    std::thread(s4578_poll, rdram).detach();
}

'''
HOOK = r'''    if (s4578_on() && rdram && len) {
        rs64_s4578_start(rdram);
        const uint32_t s_ = phys & 0x007FFFFFu;
        g_s4578_total++;
        if (s_ < 0x14A000u && s_ + len > 0x149000u) g_s4578_page++;
        {
            std::lock_guard<std::mutex> g(g_s4578_mu);
            auto& e = g_s4578_ring[g_s4578_n % 16];
            e.seq = g_s4578_n++; e.phys = s_; e.len = len; e.vi_w = rs64_vi_committed_width();
            std::snprintf(e.api, sizeof e.api, "%s", api ? api : "?");
        }
        if (s_ < 0x149720u && s_ + len > 0x149700u)
            std::fprintf(stderr, "[s4578-HOSTWRITE-OVERLAP] phys=%06X len=%X api=%s vi_w=%u\n", s_, len, api ? api : "?", rs64_vi_committed_width());
    }
'''
t = t.replace(A, NEW + A).replace(B, HOOK + B)
for inc in ("thread", "mutex", "chrono", "atomic"):
    if f"#include <{inc}>" not in t:
        t = t.replace("#include", f"#include <{inc}>\n#include", 1)
f.write_text(t)
print("ok")
