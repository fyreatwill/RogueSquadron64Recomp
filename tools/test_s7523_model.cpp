// s7665: offline ASan/UBSan fuzz of the s7523/s7524 finite-rate RDP model (src/rsp/s7523_slow_rdp.cpp).
// Drives random START/END/task/status/cur/DMA/pre_submit sequences against a fake 16 MB rdram and checks
// model invariants after every call. Build+run: tools/test_s7523_model.sh
#include "../src/rsp/s7523_slow_rdp.cpp"
#include <random>
#include <cassert>
static uint32_t g_fs = 0;
extern "C" uint32_t rs64_dpc_get_cumulative_fullsyncs() { return g_fs; }
static int check(const char* where, long step) {
    // invariants: every queued range's snapshot window lies inside snap; sg bytes == q bytes; offsets monotonic
    size_t qb = 0, prev = snap_base;
    for (const R& h : q) {
        if (h.hi < h.lo || h.off < prev || h.off - snap_base + (h.hi - h.lo) > snap.size()) {
            std::fprintf(stderr, "BAD %s step=%ld q lo=%06X hi=%06X off=%zu base=%zu snap=%zu\n", where, step, h.lo, h.hi, h.off, snap_base, snap.size()); return 1; }
        prev = h.off; qb += h.hi - h.lo; }
    size_t sb = 0;
    for (const S& f : sg) { if (f.hi < f.lo || f.off < snap_base || f.off - snap_base + (f.hi - f.lo) > snap.size()) {
            std::fprintf(stderr, "BAD %s step=%ld sg lo=%06X hi=%06X off=%zu base=%zu snap=%zu\n", where, step, f.lo, f.hi, f.off, snap_base, snap.size()); return 1; }
        sb += f.hi - f.lo; }
    if (sb != qb) { std::fprintf(stderr, "BAD %s step=%ld sg bytes %zu != q bytes %zu\n", where, step, sb, qb); return 1; }
    if (tch.size() != snap.size()) { std::fprintf(stderr, "BAD %s step=%ld tch %zu != snap %zu\n", where, step, tch.size(), snap.size()); return 1; }
    return 0;
}
int main(int argc, char** argv) {
    long steps = argc > 1 ? atol(argv[1]) : 2000000; unsigned seed = argc > 2 ? atoi(argv[2]) : 1;
    int plant = argc > 3 ? atoi(argv[3]) : 0;   // 1 = control: corrupt an R offset, check() must fire (rc 2); 2 = same corruption with check() off, ASan must abort inside consume()
    static std::vector<uint8_t> ram(1u << 24); std::mt19937 rng(seed);
    rs64_s7523_on = 1; g_rate = 8 + rng() % 64; g_gap = rng() % 256;
    uint32_t end = 0x100000;
    for (long i = 0; i < steps; i++) {
        unsigned op = rng() % 100; const char* w = "?";
        if (op < 20) { w = "end"; uint32_t len = (rng() % 8 == 0) ? 0 : (rng() % 0x400) * 8; if (rng() % 50 == 0) end = 0x100000 + (rng() % 0x1000) * 8;   // ring wrap
            if (end + len > 0xFFFFFF) end = 0x100000; end += len; rs64_s7523_end(end, ram.data()); }
        else if (op < 25) { w = "start"; end = 0x100000 + (rng() % 0x2000) * 8; rs64_s7523_start(end); }
        else if (op < 30) { w = "task"; rs64_s7523_task(); }
        else if (op < 55) { w = "status"; rs64_s7523_status_read(); }
        else if (op < 70) { w = "cur"; rs64_s7523_cur_read(); }
        else if (op < 72) { w = "endrd"; rs64_s7523_end_read(); }
        else if (op < 85) { w = "dma"; uint32_t d = 0x100000 + rng() % 0x20000; ram[d ^ 3] ^= 1; rs64_s7523_dma(1, rng() % 0x1000, (rng() % 4 == 0 ? 0x80000000u : 0) | d, rng() % 0x1000, rng() % 3 == 0); }
        else if (op < 88) { w = "pre"; rs64_s7523_pre_submit(); }
        else if (op < 90) { w = "fs"; ++g_fs; }
        else { w = "ramw"; ram[(0x100000 + rng() % 0x40000) ^ 3] = rng(); }
        if (plant && i >= steps / 2 && !q.empty() && q.back().hi > q.back().lo + 64 && plant != 9) { q.back().off = snap_base + snap.size() + (plant == 2 ? (size_t(1) << 32) : 4096); plant = plant == 2 ? 9 : plant; }
        if (plant != 9 && check(w, i)) return 2;
    }
    std::fprintf(stderr, "OK steps=%ld seed=%u rate=%u gap=%u consumed=%llu ranges=%llu ctl=%llu/%llu skipped=%llu\n", steps, seed, g_rate, g_gap,
                 (unsigned long long)consumed, (unsigned long long)ranges, (unsigned long long)ctl_caught, (unsigned long long)ctl_planted, (unsigned long long)skipped);
    return 0;
}
