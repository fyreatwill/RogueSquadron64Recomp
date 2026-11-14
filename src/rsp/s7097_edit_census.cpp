// s7097 (bridge-edit-census): which of the DPC bridge's edit walkers (rs64_dpc_record_submit_impl in
// src/rsp/dpc_bridge.cpp) changes which RDP command bytes, and does anything else change them?
//
// Per record_submit call [lo,hi): S0 = snapshot of [lo-G, hi+G) at entry (G = guard band, catches walkers that write
// outside the range they were handed). Before each walker the live bytes are compared with the running snapshot (a
// difference there = a write by no walker, "between"); after the walker, differences are that walker's edits and are
// folded into the snapshot. At impl exit the whole guarded window is compared again ("tail" = changed after the last
// walker; "outside" = guard-band bytes changed by any walker, attributed per walker since the guard is in the per-walker
// compare too).
// Commands are decoded at TRUE boundaries across calls (carried state: a call that continues the previous call's
// stream keeps the straddling command; otherwise resync at lo), from the entry bytes, with the RDP length table
// (texrect 16 B, triangles 32 + 64 shade + 64 tex + 16 z, rest 8 B). Each changed byte is filed under its walker, the
// enclosing command's op and its 32-bit word index inside the command; new op on header changes too.
// ROGUESQ_S7097_EDIT=1 arms; =ctl additionally, on 1 call per 4096, flips one in-range byte between walker 2 and 3 and
// restores it right after the check (must show as "between"), and flips one guard byte before the exit compare and
// restores it after (must show as "tail"). Dump: build/rs64_s7097.log every 5 s.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <vector>
#include <algorithm>
extern "C" int rs64_s7097_on = [] {
    const char* e = getenv("ROGUESQ_S7097_EDIT");
    int v = !(e && *e && *e != '0') ? 0 : (e[0] == 'c' ? 2 : 1);
    if (v) fprintf(stderr, "[s7097] bridge edit census armed%s\n", v == 2 ? " (+ctl)" : "");
    return v;
}();
namespace {
enum { NW = 11, G = 64 };
const char* kW[NW] = {"census", "title_clear", "wipe", "pillar", "rect_wrap", "pause_dim", "rect_scan", "spike", "g5b_frame", "region", "floor"};
constexpr uint32_t kEnd = 0x1000000u;
struct Cmd { uint32_t a, len; uint8_t op; };
struct WS {
    uint64_t calls_changed = 0, bytes = 0, cmds = 0, outside = 0, hdr_opchange = 0;
    uint64_t op_word[64][44] = {};
    uint64_t newop[64] = {};
    uint64_t op_from_to[8] = {};
    int nex = 0; char ex[8][200];
};
WS g_w[NW + 2];   // NW = between (no walker), NW+1 = tail (after the last walker)
uint8_t* g_rd = nullptr;
uint32_t g_lo = 0, g_hi = 0, g_glo = 0, g_ghi = 0;
std::vector<uint8_t> g_s0, g_cur; std::vector<Cmd> g_cmds;
uint32_t g_next = 0, g_sthi = 0, g_cs = 0, g_clen = 0; uint8_t g_cop = 0; bool g_valid = false;
uint64_t g_calls = 0, g_bytes = 0, g_resync = 0, g_ctl_calls = 0, g_ctl_between_hit = 0, g_ctl_tail_hit = 0, g_skipped = 0;
bool g_ctl = false; uint32_t g_ctl_a = 0, g_ctl_g = 0; int g_ctl_stage = 0;
time_t g_last = 0;
inline uint8_t byteat(const uint8_t* base, uint32_t a) { return base[a]; }   // rdram stored as native u32 words: byte a = MIPS byte a^3
inline uint8_t op_at(const uint8_t* buf, uint32_t off) { return buf[off + 3] & 0x3F; }  // header word's MSB, buf indexed like rdram
inline uint32_t cmdlen(uint8_t op) {
    if (op == 0x24 || op == 0x25) return 16;
    if (op >= 0x08 && op <= 0x0F) return 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
    return 8;
}
const Cmd* find(uint32_t a) {
    if (g_cmds.empty()) return nullptr;
    auto it = std::upper_bound(g_cmds.begin(), g_cmds.end(), a, [](uint32_t x, const Cmd& c) { return x < c.a; });
    if (it == g_cmds.begin()) return nullptr;
    --it; if (a >= it->a + it->len) return nullptr;
    return &*it;
}
uint32_t word_now(uint32_t a) { uint32_t v; memcpy(&v, g_rd + (a & ~3u), 4); return v; }
uint32_t word_snap(uint32_t a) { uint32_t v; memcpy(&v, &g_cur[(a & ~3u) - g_glo], 4); return v; }
// Compare live window with g_cur; file differences under slot w; update g_cur.
void diff(int w) {
    const uint32_t n = g_ghi - g_glo;
    if (memcmp(g_rd + g_glo, g_cur.data(), n) == 0) return;
    WS& s = g_w[w]; s.calls_changed++;
    uint32_t last_cmd = UINT32_MAX;
    for (uint32_t i = 0; i < n; i++) {
        const uint32_t a = g_glo + i;
        if (g_rd[a] == g_cur[i]) continue;
        if (g_ctl && g_ctl_stage == 1 && w == NW && a == g_ctl_a) g_ctl_between_hit++;
        if (g_ctl && g_ctl_stage == 2 && w == NW + 1 && a == g_ctl_g) g_ctl_tail_hit++;
        s.bytes++;
        const bool in = a >= g_lo && a < g_hi;
        const Cmd* c = in ? find(a) : nullptr;
        if (!in) s.outside++;
        uint8_t op = c ? c->op : 0x3F; uint32_t wi = c ? std::min<uint32_t>((a - c->a) >> 2, 43) : 43;
        if (c && c->a != last_cmd) { s.cmds++; last_cmd = c->a; }
        s.op_word[op][wi]++;
        if (c && a == c->a + 3) { s.hdr_opchange++; s.newop[g_rd[a] & 0x3F]++; }
        if (s.nex < 8 && (a & 3) == 0 + 0) { /* one example per changed word */ }
        if (s.nex < 8 && ((a & 3) == 0 || i == 0 || g_rd[a - 1] == g_cur[i - 1])) {
            snprintf(s.ex[s.nex++], 200, "call=%llu a=0x%06X %s cmd=0x%06X op=%02X len=%u word=%u old=%08X new=%08X lo=0x%06X hi=0x%06X",
                     (unsigned long long)g_calls, a, in ? "in" : "GUARD", c ? c->a : 0, op, c ? c->len : 0, wi, word_snap(a), word_now(a), g_lo, g_hi);
        }
        g_cur[i] = g_rd[a];
    }
}
void dump() {
    FILE* o = fopen("rs64_s7097.log", "w"); if (!o) return;
    fprintf(o, "s7097 mode=%d calls=%llu bytes=%llu resync=%llu skipped=%llu ctl_calls=%llu ctl_between_hit=%llu ctl_tail_hit=%llu (both must equal ctl_calls)\n",
            rs64_s7097_on, (unsigned long long)g_calls, (unsigned long long)g_bytes, (unsigned long long)g_resync, (unsigned long long)g_skipped,
            (unsigned long long)g_ctl_calls, (unsigned long long)g_ctl_between_hit, (unsigned long long)g_ctl_tail_hit);
    for (int w = 0; w < NW + 2; w++) {
        const WS& s = g_w[w];
        const char* nm = w < NW ? kW[w] : (w == NW ? "BETWEEN" : "TAIL");
        // ctl flips are subtracted from BETWEEN/TAIL in the verdict line
        fprintf(o, "W %-11s calls_changed=%llu bytes=%llu cmds=%llu outside=%llu hdr_opchange=%llu\n", nm, (unsigned long long)s.calls_changed,
                (unsigned long long)s.bytes, (unsigned long long)s.cmds, (unsigned long long)s.outside, (unsigned long long)s.hdr_opchange);
        if (!s.bytes) continue;
        fprintf(o, "  op.word:");
        for (int op = 0; op < 64; op++) for (int wi = 0; wi < 44; wi++) if (s.op_word[op][wi]) fprintf(o, " %02X.%u=%llu", op, wi, (unsigned long long)s.op_word[op][wi]);
        fprintf(o, "\n  newop:"); for (int op = 0; op < 64; op++) if (s.newop[op]) fprintf(o, " %02X=%llu", op, (unsigned long long)s.newop[op]);
        fprintf(o, "\n");
        for (int k = 0; k < s.nex; k++) fprintf(o, "  EX %s\n", s.ex[k]);
    }
    const uint64_t bu = g_w[NW].bytes - g_ctl_between_hit, tu = g_w[NW + 1].bytes - g_ctl_tail_hit;
    fprintf(o, "VERDICT unattributed_between=%llu unattributed_tail=%llu ctl=%s\n", (unsigned long long)bu, (unsigned long long)tu,
            (g_ctl_calls && g_ctl_between_hit == g_ctl_calls && g_ctl_tail_hit == g_ctl_calls) ? "pass" : (rs64_s7097_on == 2 ? "FAIL" : "off"));
    fclose(o);
}
}  // namespace
extern "C" void rs64_s7097_begin(uint32_t lo, uint32_t hi, uint8_t* rd) {
    g_rd = rd; g_lo = lo; g_hi = hi; g_ctl = false; g_ctl_stage = 0;
    if (!rd || hi <= lo || hi > kEnd || hi - lo > 0x200000u) { g_glo = g_ghi = 0; g_skipped++; g_valid = false; return; }
    g_calls++; g_bytes += hi - lo;
    // s7363 (class AN): word-align the window. word_snap(a) reads g_cur[(a & ~3) - g_glo .. +4): with an unaligned DPC start
    // (lo & 3 != 0) the first changed byte gave (a & ~3) < g_glo -> a size_t underflow read, and an unaligned g_ghi read 1-3 B past g_cur.
    g_glo = (lo >= G ? lo - G : 0) & ~3u; g_ghi = (std::min<uint32_t>(hi + G, kEnd) + 3u) & ~3u;
    g_s0.assign(rd + g_glo, rd + g_ghi); g_cur = g_s0;
    // command boundaries from the entry bytes, carried across contiguous calls
    g_cmds.clear();
    if (!(g_valid && lo == g_sthi && g_next >= lo)) { g_resync++; g_next = lo; }
    else if (g_next > lo) g_cmds.push_back({g_cs, g_clen, g_cop});   // straddling command from the previous call
    uint32_t a = g_next;
    while (a + 4 <= hi) {
        const uint8_t op = op_at(rd, a); const uint32_t len = cmdlen(op);
        g_cmds.push_back({a, len, op}); g_cs = a; g_clen = len; g_cop = op; a += len;
    }
    g_next = a; g_sthi = hi; g_valid = true;
    if (rs64_s7097_on == 2 && (g_calls & 4095u) == 4095u && hi - lo >= 16) { g_ctl = true; g_ctl_calls++; g_ctl_a = lo + 9; g_ctl_g = g_ghi > hi ? hi : 0; }
    if (g_ctl && !g_ctl_g) { g_ctl = false; g_ctl_calls--; }
}
extern "C" void rs64_s7097_pre(int w) {
    if (g_ghi <= g_glo) return;
    if (g_ctl && w == 3) { g_rd[g_ctl_a] ^= 0x5A; g_ctl_stage = 1; }
    diff(NW);
    if (g_ctl && w == 3) { g_rd[g_ctl_a] ^= 0x5A; g_cur[g_ctl_a - g_glo] = g_rd[g_ctl_a]; g_ctl_stage = 0; }
}
extern "C" void rs64_s7097_post(int w) { if (g_ghi > g_glo) diff(w); }
extern "C" void rs64_s7097_end() {
    if (g_ghi > g_glo) {
        if (g_ctl) { g_rd[g_ctl_g] ^= 0xA5; g_ctl_stage = 2; }
        diff(NW + 1);
        if (g_ctl) { g_rd[g_ctl_g] ^= 0xA5; g_ctl_stage = 0; }
    }
    g_ghi = g_glo = 0;
    time_t t = time(nullptr); if (t - g_last >= 5) { g_last = t; dump(); }
}
