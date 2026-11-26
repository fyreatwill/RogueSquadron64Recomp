#include <unordered_map>
#include "rs64_controls_panel.h"
#include "rs64_shell_quote.h"  // s7962 class PS
#include <mach/mach_time.h>  // s6922: dump window clock
#include <execinfo.h>
#include <dlfcn.h>
#include <memory>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <mutex>
#include <string_view>
#include <vector>
#include <deque>
#include <condition_variable>
#include <thread>
#include <pthread.h>
#include <pthread/qos.h>
#include <unistd.h>  // s6993 getpid (stall self-sample)
#include <string>
extern "C" void rs64_waittab_dump(void); // s7191 (upstream_compat.cpp)

#define HLSL_CPU
#include "hle/rt64_application.h"

#include "ultramodern/ultramodern.hpp"
#include "ultramodern/renderer_context.hpp"

// Shared Application accessor for the LLE DPC bridge (src/rsp/dpc_bridge.cpp).
// The bridge needs to forward Factor 5 raw RDP byte ranges via
// processDisplayLists(isHLE=false). Set on construction, cleared on shutdown.
static std::atomic<RT64::Application*> g_rt64_app{nullptr};
// s6705 G1e async RDP consumer (see ultramodern::rdpq below); flipped on the Gfx thread by ROGUESQ_RDP_ASYNC_TOGGLE.
// s6751: ROGUESQ_RAND_TRACE=<path> logs every guest rand() call (0x80003430) from the ROGUESQ_DEBUG_WRITE poke on:
// call index, update_screen #, caller jal address, seed before the call (plus marker rows: site = probe PC, value). Hooked by tools/fixup_rand_trace.py; mirrors
// rs64_oracle --exec-trace so the two arms' call sequences can be aligned offline.
extern "C" volatile int g_rs64_rand_trace;
extern "C" volatile uint32_t rs64_vi_n_g;
extern "C" int rs64_g1d_walk_diag; extern "C" uint32_t rs64_g1d_walk_lo, rs64_g1d_walk_hi; // s6851
extern std::vector<uint32_t> g_rs64_g1d_walk, g_rs64_g1d_walk_cw;
extern "C" uint32_t rs64_rand_site;
uint32_t rs64_rand_site = 0; // jal address of the current rand call site (s6751 fixup)
volatile int g_rs64_rand_trace = 0;
extern "C" uint32_t rs64_ram_top; // s6132
extern "C" void rs64_s7751_dump(unsigned); // s7751 src/rsp/s7751_task_snap.cpp
extern "C" void rs64_s6883_freeze(unsigned); // s6883: span tables at each POSE_FREEZE
static FILE* s_rand_trace_f = nullptr;
// s7845: ROGUESQ_RAND_TRACE_MAX=<rows> overrides the 400000-row cap (shared by rand rows and marker rows).
static long rs64_rand_trace_max() {
    // magic static: thread-safe one-time init (read from the gfx thread and guest hooks)
    static const long m = [] { const char* e = std::getenv("ROGUESQ_RAND_TRACE_MAX"); return (e && atol(e) > 0) ? atol(e) : 400000L; }();
    return m;
}
// s7896: rdram base for host-side guest writes from rs64_rand_trace (set by the first rs64_xtrace_mark, VI ~14, long before any
// reseed point). Game thread only.
static const uint8_t* s_s7896_rdram = nullptr;
extern "C" volatile uint32_t rs64_s7858_tick;
extern "C" void rs64_rand_trace(uint32_t ra, uint32_t seed) {
    static long n = 0;
    if (!s_rand_trace_f || n >= rs64_rand_trace_max()) return;
    // s7896 G3 island B: ROGUESQ_RAND_RESEED="SITE:K:SEED,..." (hex SITE = the jal address logged in column 3, K = 1-based ordinal
    // of calls from that site, hex SEED) overwrites rngSeed 0x80003470 at rand entry of that call, so the call and every later one
    // return retail's values (rand: seed' = seed * 0xA8351D63, returned). SEED = retail's column-4 value (seed before the call)
    // for the same call. Row gets " reseed=OLD". Unset = byte-identical.
    static struct { uint32_t site, k, val, cnt; } rs[4];
    static int nrs = -1;
    if (nrs < 0) {
        nrs = 0;
        const char* e = std::getenv("ROGUESQ_RAND_RESEED");
        while (e && *e && nrs < 4) {
            unsigned a, k, v;
            if (sscanf(e, "%x:%u:%x", &a, &k, &v) == 3 && k > 0) rs[nrs++] = {a, k, v, 0};
            e = strchr(e, ',');
            if (e) e++;
        }
    }
    fprintf(s_rand_trace_f, "%ld %u %08x %08x", n++, rs64_vi_n_g, ra, seed);
    // s7896: ROGUESQ_RAND_REPLAY=<file> (tools/s7896_rand_replay.py: "SITE ORD SEED" hex/dec/hex per retail pre-tick rand call)
    // sets rngSeed to retail's seed-before for the ORD-th call from SITE, pre-mission-tick only (tick 0 has its own pin).
    // Calls the table lacks (port calls a site more often) keep the port seed. Row gets " replay=OLD>NEW". Unset = byte-identical.
    static std::unordered_map<uint64_t, uint32_t>* rp = nullptr;
    static std::unordered_map<uint32_t, uint32_t> rpn;
    static int rp_init = 0;
    static uint32_t rp_gap = 0;
    static std::unordered_map<uint32_t, uint32_t> rp_last, rp_bno;
    if (!rp_init) {
        rp_init = 1;
        if (const char* e = std::getenv("ROGUESQ_RAND_REPLAY")) {
            if (FILE* f = fopen(e, "r")) {
                rp = new std::unordered_map<uint64_t, uint32_t>();
                unsigned a, k, v, bo;
                // s7900: ROGUESQ_RAND_REPLAY_BURST=<gap VI> reads "SITE BURST BORD SEED" (s7896_rand_replay.py --burst GAP) and
                // keys by (site, burst, ordinal in burst): a site's calls split into bursts at silences > gap VI. Unset = s7896 keys.
                if (const char* g = std::getenv("ROGUESQ_RAND_REPLAY_BURST")) rp_gap = (uint32_t)atoi(g);
                if (rp_gap) { while (fscanf(f, "%x %u %u %x", &a, &k, &bo, &v) == 4) (*rp)[((uint64_t)a << 32) | (k << 24) | bo] = v; }
                else while (fscanf(f, "%x %u %x", &a, &k, &v) == 3) (*rp)[((uint64_t)a << 32) | k] = v;
                fclose(f);
                fprintf(stderr, "[s7896 replay] %zu retail rand rows from %s\n", rp->size(), e);
            }
        }
    }
    if (rp && rs64_s7858_tick == 0 && s_s7896_rdram) {
        uint64_t key;
        if (rp_gap) {
            auto lv = rp_last.find(ra);
            if (lv != rp_last.end() && rs64_vi_n_g - lv->second > rp_gap) { rp_bno[ra]++; rpn[ra] = 0; }
            rp_last[ra] = rs64_vi_n_g;
            // s7901: ROGUESQ_RAND_REPLAY_SKEW="SITE:BURST:DELTA,..." (hex SITE, signed DELTA) reads the table at in-burst ordinal
            // n+DELTA for that site's burst: retail's 0x800541FC burst 2 starts one 16-call frame before the port's (its first flame
            // frame uses the other parity buffer), so per-site ordinals of one parity are a frame apart. Unset = s7900 keys.
            // s7904: optional 4th field FROM ("SITE:BURST:DELTA:FROM") applies DELTA only from in-burst ordinal FROM on (tail-scoped);
            // missing FROM = 0 = whole burst, byte-identical to s7901.
            static struct { uint32_t site, burst; int delta; uint32_t from; } sk[4];
            static int nsk = -1;
            if (nsk < 0) {
                nsk = 0;
                const char* e = std::getenv("ROGUESQ_RAND_REPLAY_SKEW");
                while (e && *e && nsk < 4) {
                    unsigned a, b, fr = 0; int d;
                    if (sscanf(e, "%x:%u:%d:%u", &a, &b, &d, &fr) >= 3) sk[nsk++] = {a, b, d, fr};
                    e = strchr(e, ',');
                    if (e) e++;
                }
            }
            int64_t ord = ++rpn[ra];
            const int64_t ord0 = ord;
            for (int i = 0; i < nsk; i++) if (sk[i].site == ra && sk[i].burst == rp_bno[ra] && ord0 >= sk[i].from) ord += sk[i].delta;
            key = ord > 0 ? (((uint64_t)ra << 32) | (rp_bno[ra] << 24) | (uint32_t)ord) : 0;
        } else key = ((uint64_t)ra << 32) | ++rpn[ra];
        auto it = rp->find(key);
        if (it != rp->end()) {
            uint32_t* w = reinterpret_cast<uint32_t*>(const_cast<uint8_t*>(s_s7896_rdram) + 0x3470);
            if (*w != it->second) fprintf(s_rand_trace_f, " replay=%08x>%08x", *w, it->second);
            *w = it->second;
        }
    }
    for (int i = 0; i < nrs; i++) {
        if (rs[i].site != ra || ++rs[i].cnt != rs[i].k || !s_s7896_rdram) continue;
        uint32_t* w = reinterpret_cast<uint32_t*>(const_cast<uint8_t*>(s_s7896_rdram) + 0x3470);
        fprintf(s_rand_trace_f, " reseed=%08x>%08x", *w, rs[i].val);
        *w = rs[i].val;
    }
    fputc('\n', s_rand_trace_f);
    fflush(s_rand_trace_f); // runs end in SIGKILL
}
// s6752: marker row with guest-memory dumps, same spec as rs64_oracle RS64_XTRACE_MEM: ROGUESQ_XTRACE_MEM=
// "PC:REG:OFF:N,..." appends " m=ADDR:w0,w1,..." (N words at gpr[REG]+OFF; REG 0 = absolute) for every spec whose PC
// matches. Row: index, update_screen #, pc, $v0, dumps. Called from tools/fixup_rand_trace.py hooks.
// s7858: ordinal of 0x800FA730 mission-tick marks (= the tick index the s7854 record tools use); stamped on [swatch-pt] lines.
extern "C" volatile uint32_t rs64_s7858_tick = 0;
// s7891: ROGUESQ_RETAIL_SNAP=3 hand-off (tools/apply_s7839_snaplog.py): timeSnapshotFiller's prev==-1 path sets _reset, the next el-path
// frame consumes it and sets _free so the vd pin skips that one call. Game thread only.
extern "C" { int rs64_s7891_reset = 0; int rs64_s7891_free = 0; }
// s7895: pc of the most recent timeSnapshotFiller return mark (0x800AF374 cinematic, 0x800C6674 crawl/phase accumulator, 0x800FA730
// mission tick); ROGUESQ_SNAP3_ONLY=c unpins a post-reset frame only after the crawl mark. Game thread only, host-side store.
extern "C" { uint32_t rs64_s7895_dtpc = 0; }
extern "C" void rs64_xtrace_mark(uint32_t pc, const uint8_t* rdram, const uint64_t* gpr) {
    s_s7896_rdram = rdram;
    // s7892: a SNAP=3 reset armed by the mission load is consumed by the next el-path frame, which on m6 falls ~11 ticks INTO the
    // mission (VI 13415, forked det tick 8). Dropping a pending reset at every mission tick keeps the unpin pre-flight only.
    if (pc == 0x800FA730u) { ++rs64_s7858_tick; rs64_s7891_reset = 0; }
    if (pc == 0x800AF374u || pc == 0x800C6674u || pc == 0x800FA730u) rs64_s7895_dtpc = pc;
    // s6872: ROGUESQ_POSE_FREEZE=<x1,x2,...>:<ms> (needs RAND_TRACE) stops the mission tick for ms when the player's x first crosses
    // each rising x. +0x4C is a per-tick copy, so POSE_PIN_POSITION cannot hold the ship, but no-input flight is deterministic:
    // this gives the same pose in every arm at any frame rate, held still for a window capture. The pad thread cannot do it.
    if (pc == 0x800FA730u) {
        // s7312: an entry written <x fires on a FALLING crossing (x <= value): L12's no-input flight spawns at x=156 and flies -x first.
        // A falling entry only arms once x has been seen above it (pre-spawn the object reads pos 0,0,0, which fired <72 at once).
        static std::vector<float> fz; static std::vector<char> fzd; static int fz_ms = -1; static size_t fz_k = 0; static bool fz_up = false;
        if (fz_ms < 0) {
            fz_ms = 0;
            if (const char* g = std::getenv("ROGUESQ_POSE_FREEZE")) {
                char* e = const_cast<char*>(g);
                for (;;) { const bool dn = *e == '<'; if (dn) e++; fz.push_back(strtof(e, &e)); fzd.push_back(dn); if (*e != ',') break; e++; }
                fz_ms = (*e == ':') ? atoi(e + 1) : 4000;
            }
        }
        const uint32_t pl = *reinterpret_cast<const uint32_t*>(rdram + 0x137DBCu);
        if (fz_k < fz.size() && pl >= 0x80001000u && pl < rs64_ram_top - 0x100u && !(pl & 3)) { // s6881: spill puts the player above 8 MB in wide + dd
            float v[3];
            memcpy(v, rdram + (pl - 0x80000000u) + 0x4C, 12);
            if (fzd[fz_k] && v[0] > fz[fz_k]) fz_up = true;
            if (fzd[fz_k] ? (fz_up && v[0] <= fz[fz_k]) : v[0] >= fz[fz_k]) {
                fz_up = false;
                fprintf(stderr, "[posefreeze] k=%zu vi=%u pos=%.3f,%.3f,%.3f ms=%d\n", fz_k, rs64_vi_n_g, (double)v[0], (double)v[1], (double)v[2], fz_ms);
                rs64_s6883_freeze((unsigned)fz_k);
                fflush(stderr);
                fz_k++;
                std::this_thread::sleep_for(std::chrono::milliseconds(fz_ms));
                rs64_s7751_dump((unsigned)(fz_k - 1));  // s7751: no task runs during the freeze
            }
        }
    }
    static struct { uint32_t pc, reg, off, n; } spec[16];
    static int nspec = -1;
    if (nspec < 0) {
        nspec = 0;
        const char* e = std::getenv("ROGUESQ_XTRACE_MEM");
        while (e && *e && nspec < 16) {
            unsigned a, r, o, k;
            if (sscanf(e, "%x:%u:%x:%u", &a, &r, &o, &k) == 4 && r < 32 && k <= 64) spec[nspec++] = {a, r, o, k};
            e = strchr(e, ',');
            if (e) e++;
        }
    }
    // s6753: ROGUESQ_XTRACE_POKE="PC:REG:OFF:VALUE,..." writes VALUE at gpr[REG]+OFF before the dump (row gets
    // " pin=OLD"); same spec as rs64_oracle RS64_XTRACE_POKE. 800FA730:29:30:3d088889 pins runInMissionFrame dt.
    // s6771: optional 5th field 1 = one-shot (800FA730:0:80003470:1:1 seeds rngSeed on the first mission tick).
    static struct { uint32_t pc, reg, off, val, once, done; } poke[8];
    static int npoke = -1;
    if (npoke < 0) {
        npoke = 0;
        const char* e = std::getenv("ROGUESQ_XTRACE_POKE");
        while (e && *e && npoke < 8) {
            unsigned a, r, o, v, once = 0;
            if (sscanf(e, "%x:%u:%x:%x:%x", &a, &r, &o, &v, &once) >= 4 && r < 32) poke[npoke++] = {a, r, o, v, once, 0};
            e = strchr(e, ',');
            if (e) e++;
        }
    }
    static long n = 0;
    if (!s_rand_trace_f || n >= rs64_rand_trace_max()) return;
    fprintf(s_rand_trace_f, "%ld %u %08x %08x", n++, rs64_vi_n_g, pc, (uint32_t)gpr[2]);
    for (int i = 0; i < npoke; i++) {
        if (poke[i].pc != pc || poke[i].done) continue;
        poke[i].done = poke[i].once & 1;
        uint32_t a = (uint32_t)gpr[poke[i].reg] + poke[i].off;
        if (a < 0x80000000u || a + 4 > rs64_ram_top || (a & 3)) continue;
        uint32_t* w = reinterpret_cast<uint32_t*>(const_cast<uint8_t*>(rdram) + (a - 0x80000000u));
        fprintf(s_rand_trace_f, " pin=%08x", *w);
        // s7905: 5th-field bit 2 = add VALUE (mod 2^32) instead of storing it (3 = one-shot add); 0/1 byte-identical to s6771.
        *w = (poke[i].once & 2) ? *w + poke[i].val : poke[i].val;
    }
    for (int i = 0; i < nspec; i++) {
        if (spec[i].pc != pc) continue;
        uint32_t a = (uint32_t)gpr[spec[i].reg] + spec[i].off;
        fprintf(s_rand_trace_f, " m=%08x:", a);
        for (uint32_t k = 0; k < spec[i].n; k++) {
            uint32_t w = a + 4 * k, v = 0;
            if (w >= 0x80000000u && w + 4 <= rs64_ram_top && !(w & 3)) v = *reinterpret_cast<const uint32_t*>(rdram + (w - 0x80000000u));
            fprintf(s_rand_trace_f, k ? ",%08x" : "%08x", v);
        }
    }
    fputc('\n', s_rand_trace_f);
    fflush(s_rand_trace_f);
}
// s6816 G3: enemy-bolt rows (tools/fixup_rand_trace.py). kind 0 = per-tick bolt state within 40 units of the player
// position (0x80137DC0), kind 1 = msg-5 hit send (victim id). Row: index, update_screen #, tag, victim, bolt node, slot
// id, owner, damage, age, life, flags, pos, vel, player pos.
extern "C" void rs64_bolt_mark(const uint8_t* rdram, uint32_t node, uint32_t slot, uint32_t victim, int kind) {
    static long n = 0;
    if (!s_rand_trace_f || n >= 300000) return;
    auto in = [](uint32_t a) { return a >= 0x80000000u && a + 4 <= rs64_ram_top && !(a & 3); };
    if (!in(node) || !in(node + 0x100) || !in(slot) || !in(slot + 0x18)) return;
    auto W = [&](uint32_t a) { return *reinterpret_cast<const uint32_t*>(rdram + (a - 0x80000000u)); };
    auto F = [&](uint32_t a) { uint32_t w = W(a); float f; memcpy(&f, &w, 4); return f; };
    float p[3], v[3], q[3];
    for (int i = 0; i < 3; i++) { p[i] = F(node + 0xB4 + 4 * i); v[i] = F(node + 0xD8 + 4 * i); q[i] = F(0x80137DC0u + 4 * i); }
    float d2 = (p[0] - q[0]) * (p[0] - q[0]) + (p[1] - q[1]) * (p[1] - q[1]) + (p[2] - q[2]) * (p[2] - q[2]);
    if (kind == 0 && !(d2 < 1600.f)) return;
    uint32_t sw = W(slot + 0x14), nw = W(node + 0xF8), fw = W(node + 0xFC);
    fprintf(s_rand_trace_f, "%ld %u %08x %04x bolt=%08x id=%04x fl=%04x own=%04x dmg=%u age=%.4f life=%.4f p=%.3f,%.3f,%.3f "
            "v=%.3f,%.3f,%.3f pl=%.3f,%.3f,%.3f\n", n++, rs64_vi_n_g, kind ? 0xb0170005u : 0xb0170000u, victim, node,
            sw & 0xFFFF, sw >> 16, nw >> 16, fw >> 16, F(node + 0xF0), F(node + 0xF4), p[0], p[1], p[2], v[0], v[1], v[2],
            q[0], q[1], q[2]);
    fflush(s_rand_trace_f);
}
// s6816b: guided-projectile rows (tools/fixup_rand_trace.py). kind 0 = every missile every tick at its swept hit test,
// kind 1 = the test returned a victim. Row: index, update_screen #, tag b0170010/b0170011, victim, missile data ptr,
// slot id, target id (+0x4C), lock flag (+0x50), owner (+0x44), damage (+0x48), age (+0x40), pos (+4), vel (+0x28),
// player pos.
extern "C" void rs64_guided_mark(const uint8_t* rdram, uint32_t m, uint32_t slot, uint32_t victim, int kind) {
    static long n = 0;
    if (!s_rand_trace_f || n >= 300000) return;
    auto in = [](uint32_t a) { return a >= 0x80000000u && a + 4 <= rs64_ram_top && !(a & 3); };
    if (!in(m) || !in(m + 0x54) || !in(slot) || !in(slot + 0x18)) return;
    auto W = [&](uint32_t a) { return *reinterpret_cast<const uint32_t*>(rdram + (a - 0x80000000u)); };
    auto F = [&](uint32_t a) { uint32_t w = W(a); float f; memcpy(&f, &w, 4); return f; };
    fprintf(s_rand_trace_f, "%ld %u %08x %04x gm=%08x id=%04x tgt=%04x lk=%02x own=%04x dmg=%u age=%.4f p=%.3f,%.3f,%.3f "
            "v=%.3f,%.3f,%.3f pl=%.3f,%.3f,%.3f\n", n++, rs64_vi_n_g, kind ? 0xb0170011u : 0xb0170010u, victim, m,
            W(slot + 0x14) & 0xFFFF, W(m + 0x4C) >> 16, W(m + 0x50) >> 24, W(m + 0x44) >> 16, W(m + 0x48) >> 16, F(m + 0x40),
            F(m + 4), F(m + 8), F(m + 0xC), F(m + 0x28), F(m + 0x2C), F(m + 0x30), F(0x80137DC0u), F(0x80137DC4u), F(0x80137DC8u));
    fflush(s_rand_trace_f);
}
// s6816: player hp writer rows (tools/apply_s5798_recwatch.py hpwatch; needs the store-diag gate, ROGUESQ_STORE_DIAG=1).
// Every store to 0x80137E7C that lowers the hp float by > 5: row tag b017dd00, writer PC, function, hp before/after,
// host backtrace (recompiled function names = the guest call chain).
extern "C" void rs64_hp_mark(const uint8_t* rdram, uint32_t pc, const char* fn) {
    static float last = 0.f; static long n = 0;
    uint32_t w = *reinterpret_cast<const uint32_t*>(rdram + 0x137E7Cu); float hp; memcpy(&hp, &w, 4);
    float prev = last; last = hp;
    if (!s_rand_trace_f || n >= 20000 || !(prev - hp > 5.f)) return;
    fprintf(s_rand_trace_f, "%ld %u b017dd00 %08x fn=%s hp=%.2f,%.2f bt=", n++, rs64_vi_n_g, pc, fn ? fn : "?", prev, hp);
    void* bt[14]; int nb = backtrace(bt, 14);
    for (int b = 1; b < nb; b++) { Dl_info di; fprintf(s_rand_trace_f, "%s%s", b > 1 ? "<" : "", (dladdr(bt[b], &di) && di.dli_sname) ? di.dli_sname : "?"); }
    fputc('\n', s_rand_trace_f); fflush(s_rand_trace_f);
}
// s6820: NPC creation rows (tools/fixup_rand_trace.py spawn bt mark): tag b7000000, entry PC, $a0, host backtrace.
extern "C" void rs64_bt_mark(uint32_t pc, uint32_t a0) {
    static long n = 0;
    if (!s_rand_trace_f || n >= 20000) return;
    fprintf(s_rand_trace_f, "%ld %u b7000000 %08x a0=%08x bt=", n++, rs64_vi_n_g, pc, a0);
    void* bt[14]; int nb = backtrace(bt, 14);
    for (int b = 1; b < nb; b++) { Dl_info di; fprintf(s_rand_trace_f, "%s%s", b > 1 ? "<" : "", (dladdr(bt[b], &di) && di.dli_sname) ? di.dli_sname : "?"); }
    fputc('\n', s_rand_trace_f); fflush(s_rand_trace_f);
}
// s6781 G3: SELECT GAME slot panels (inset, left emblem) vanished at random. The menu image worker (0x800B3650) sends
// each completion as a pointer to a message on its own stack; the menu reads one message per frame (id byte +0x17).
// Retail jobs take ~60 VI so each completion is read before the next overwrites it; the port's worker finished jobs
// ~1 VI apart and the menu read the later id twice (oracle + port xtrace, s6781). tools/fixup_menu_worker.py calls
// rs64_menu_worker_sent after a successful send (records pointer + id) and rs64_menu_worker_recv after the menu's lbu
// (returns the id recorded for that pointer), so every completion arrives with its own id. ROGUESQ_MENU_WORKER_FIFO=0 = old.
static bool rs64_menu_fifo_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_MENU_WORKER_FIFO"); return !(e && *e == '0'); }(); return on; }
static std::mutex s_menu_fifo_mu;
static std::deque<std::pair<uint32_t, uint32_t>> s_menu_fifo;  // (message pointer, request id)
extern "C" void rs64_menu_worker_sent(const uint8_t* rdram, const uint64_t* gpr) {
    if (!rs64_menu_fifo_on() || (uint32_t)gpr[2] == 0) return;  // send failed (queue full): nothing was queued
    const uint32_t msg = (uint32_t)gpr[29] + 0x10;               // worker stack message, request id word at +0x14
    const uint32_t id = *reinterpret_cast<const uint32_t*>(rdram + (msg + 0x14 - 0x80000000u));  // full request counter
    std::lock_guard<std::mutex> lk(s_menu_fifo_mu);
    // Request ids come from a counter that initBackdropLoaderWorker resets to 1 (0x800B3EC8) and only grows: an id not
    // above the last recorded one means a new worker instance, so drop completions a torn-down menu never read.
    if (!s_menu_fifo.empty() && id <= s_menu_fifo.back().second) s_menu_fifo.clear();
    if (s_menu_fifo.size() >= 64) s_menu_fifo.pop_front();
    s_menu_fifo.emplace_back(msg, id);
}
extern "C" uint64_t rs64_menu_worker_recv(uint32_t msg, uint32_t v0) {
    if (!rs64_menu_fifo_on()) return v0;
    std::lock_guard<std::mutex> lk(s_menu_fifo_mu);
    if (s_menu_fifo.empty() || s_menu_fifo.front().first != msg) return v0;  // not a recorded completion: guest value
    const uint32_t id = s_menu_fifo.front().second & 0xFFu;  // the menu reads the low byte (+0x17)
    s_menu_fifo.pop_front();
    static int s_fixed = 0;
    if (id != (v0 & 0xFFu) && s_fixed++ < 16)
        fprintf(stderr, "[s6781-worker] completion id %u restored (stack slot already rewritten to %u)\n", id, v0 & 0xFFu);
    return id;
}

extern "C" int rs64_rdp_async_on;
int rs64_rdp_async_on = [] { const char *e = std::getenv("ROGUESQ_RDP_ASYNC"); return (e && *e && *e != '0') ? 1 : 0; }();
namespace RT64 { extern volatile int g_s4280_n; } // rt64_rdp.cpp s4280 cimg events
namespace ultramodern { void rs64_rdpq_drain(); void rs64_rdpq_task_enter(); void rs64_rdpq_task_exit(); void rs64_scr_note(double drain_ms, double pre_ms, double up_ms); bool rs64_rdpq_screen_ready(); void rs64_rdpq_screen_job(); }
// s6884 G1e: update_screen split for [g1e-aq]: Gfx-thread wait in the drain, the diagnostics between, app->updateScreen.
static double rs64_scr_t0 = 0, rs64_scr_t1 = 0; // Gfx thread only
static inline double rs64_scr_now() { return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
extern "C" uint32_t rs64_phase_ord(void);

// Host-side observations only; no rendering decision depends on them.
static std::atomic<uint32_t> g_rs64_g1d_join_phase{UINT32_MAX};
static std::atomic<uint32_t> g_rs64_g1d_join_lo{0};
static std::atomic<uint32_t> g_rs64_g1d_join_hi{0};
static std::atomic<uint32_t> g_rs64_g1d_join_ci_w{0};
static std::atomic<uint32_t> g_rs64_g1d_join_ci_a{0};
static std::atomic<uint32_t> g_rs64_g1d_join_cis{0};

struct Rs64G1dCiObservation {
    uint32_t width;
    uint32_t address;
    uint32_t lo;
    uint32_t hi;
};
static std::mutex g_rs64_g1d_ci_mutex;
static std::vector<Rs64G1dCiObservation> g_rs64_g1d_ci_frame;

extern "C" void rs64_g1d_join_swap(uint32_t frame, uint32_t fb,
                                     uint32_t vi_width, uint32_t vi_origin) {
    static int enabled = -1;
    static uint32_t last_phase = UINT32_MAX;
    static uint32_t phase_rows = 0;
    if (enabled < 0) {
        const char* route = std::getenv("ROGUESQ_LOG_RDP_ROUTE");
        const char* dump = std::getenv("ROGUESQ_FB_DUMP_VI");
        enabled = ((route && *route && *route != '0') ||
                   (dump && *dump && *dump != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t phase = rs64_phase_ord();
    if (phase != last_phase) { last_phase = phase; phase_rows = 0; }
    if (phase_rows++ < 160) {
        std::vector<Rs64G1dCiObservation> cis;
        {
            std::lock_guard<std::mutex> lock(g_rs64_g1d_ci_mutex);
            cis.swap(g_rs64_g1d_ci_frame);
        }
        std::fprintf(stderr,
            "[g1d-join] phase=%u frame=%u fb=0x%06X vi_w=%u vi_o=0x%06X "
            "rdp_lo=0x%06X rdp_hi=0x%06X ci_n=%u last_ci_w=%u last_ci_a=0x%06X\n",
            phase, frame, fb & 0xFFFFFFu, vi_width, vi_origin & 0xFFFFFFu,
            g_rs64_g1d_join_lo.load(), g_rs64_g1d_join_hi.load(),
            g_rs64_g1d_join_cis.load(), g_rs64_g1d_join_ci_w.load(),
            g_rs64_g1d_join_ci_a.load());
        std::fprintf(stderr, "[g1d-frame-ci] phase=%u frame=%u n=%zu", phase, frame, cis.size());
        for (const auto& ci : cis) {
            std::fprintf(stderr, " %u@0x%06X[0x%06X-0x%06X]",
                         ci.width, ci.address, ci.lo, ci.hi);
        }
        std::fputc('\n', stderr);
        std::fflush(stderr);
    }
}

extern "C" uint64_t rs64_dpc_get_last_submit_serial();
extern "C" bool rs64_dpc_take_synthetic_consumer(uint64_t *serial);
extern "C" uint32_t rs64_e9prov_current_task();
extern "C" uint32_t rs64_e9prov_current_root_dl();
extern "C" uint32_t rs64_e9prov_current_scope();
extern "C" volatile uint32_t g_rs64_last_guest_pc;
extern uint32_t g_rsp_dpc_start;
extern uint32_t g_rsp_dpc_end;
extern "C" int rs64_is_hangar_vi(void);
extern "C" void rs64_s4899_vi(uint32_t vi, uint32_t width);
extern "C" void rs64_s4597_target_store(char width, uint32_t pc, uint32_t addr, uint32_t value);
extern "C" void rs64_m5_b40_route_title_transition(void);
extern "C" void rs64_m5_route_fingerprint_phase(uint32_t width,
                                                  uint32_t origin);
extern "C" void rs64_m5_route_fingerprint_snapshot(uint32_t width,
                                                     uint32_t origin);
extern "C" void rs64_vi_boundary_log(const char* edge, uint32_t requested_fb,
                                      uint32_t committed_origin, uint32_t width);
extern "C" uint32_t rs64_vi_boundary_screen_request(void);
extern "C" uint32_t rs64_m5_host_send_begin(uint32_t data_ptr);
extern "C" void rs64_m5_host_edge(const char* edge, uint32_t task_seq,
                                    uint32_t data_ptr, uint32_t mq,
                                    uint32_t source, uint32_t sent,
                                    int32_t valid_count, int32_t msg_count);

// Interval-scoped diagnostics (session 25).
//
// The RT64-side censuses (ROGUESQ_LOG_FLOOR and friends) keep their `seen` set
// and print budget in run-lifetime statics, so whichever phase runs first
// consumes the whole budget and every later phase reports nothing. That is the
// same trap session 18 hit with "first N" counters, and it is why the hangar
// floor band has never actually been attributed: the census fires during boot
// and the title screen and is exhausted long before the hangar starts at ~55s.
//
// Publishing a counter that ticks on every VI-width change lets those censuses
// reset per phase, and lets each line say which phase it belongs to instead of
// relying on log-line interleave after the fact.
static std::atomic<uint32_t> g_rs64_phase_ord{0};
extern "C" void rs64_bump_phase_ord(void) {
    g_rs64_phase_ord.fetch_add(1, std::memory_order_relaxed);
}
extern "C" { volatile uint32_t rs64_vi_n_g = 0; } // s5816
extern "C" { extern volatile uint32_t rs64_vimode_n_g; extern volatile uint64_t rs64_vimode_us_g; extern volatile int32_t rs64_run_tok_g; } // s6808 (upstream_compat.cpp, ultramodern threads.cpp)
extern "C" uint32_t rs64_phase_ord(void) {
    return g_rs64_phase_ord.load(std::memory_order_relaxed);
}
extern "C" void rs64_m5_selector_ai_call_latch_join(uint32_t width,
                                                       uint32_t origin,
                                                       uint32_t phase);

// Shared wall-clock epoch (s234) so guest-side diagnostics (funcs_*.c PATCH
// blocks, via extern "C" declaration) can emit timestamps directly
// comparable to the [phase] line below and to host-side hold_NN.png capture
// timing — one clock, not a second independently-skewed one per diagnostic.
static const std::chrono::steady_clock::time_point g_rs64_t0 = std::chrono::steady_clock::now();
extern "C" double rs64_elapsed_seconds(void) {
    return std::chrono::duration<double>(std::chrono::steady_clock::now() - g_rs64_t0).count();
}

extern "C" void rs64_dpc_get_cumulative_histogram(uint32_t out[64]);
extern "C" uint32_t rs64_dpc_get_cumulative_fullsyncs();
extern "C" void rs64_cine_dump_if_stuck(void);
extern "C" void rs64_cine_progress_log(void);
// LLE GFX entry — runs the RSP recompile (factor5_boot + factor5_ucode)
// against this task's data. Defined in main.cpp. OSTask comes from
// ultramodern/ultra64.h (already included via ultramodern.hpp).
extern "C" int rs64_run_lle_gfx(uint8_t* rdram, const OSTask* task);
extern "C" int rs64_tl_on; extern "C" void rs64_tl(uint32_t code, uint32_t arg); // s6711 G1e timeline (mesgqueue.cpp)

// s4267: per-second phase aggregates (ROGUESQ_S4267=1). Phases: 0 pipeline wait, 1 tex-upload wait (fb), 2 fb uploaders+gfx worker wait,
// 3 drawdata/transforms uploaders+worker+tex wait, 4 RT64 State::fullSync total, 5 processDisplayLists (RDP submit), 6 rs64_run_lle_gfx, 7 send_dl total.
#include <chrono>
#include <mutex>
#include <string>
#include <atomic>
extern "C" uint32_t rs64_ram_top; // s6132
extern std::atomic<uint64_t> g_rs64_rt64_tri_accepted, g_rs64_rt64_rect_accepted;
volatile uint32_t g_rs64_g1cf_tasks = 0, g_rs64_g1cf_dsize = 0;  // s6070 g1cf: gfx tasks / dl bytes since last VI
extern "C" { volatile int g_rs64_dd_blk = 0; }
extern "C" int g_rs64_s7239_wm;  // s7240: WIDEWIN_MERGE phase at the last face group (1 = merging), tags [g1cf]
extern "C" int g_rs64_s7233_wr;  // s7233: WIDEWIN_R in force at the last stream call (0 = none), tags [g1cf]  // s6070: set by the s6036 dd patch (funcs_9.c): 1 = dd multiplier active this call
static struct G1cf { uint32_t subs = 0, bytes = 0, tri = 0, maxlen = 0, lastlen = 0; uint64_t rt0 = 0, rr0 = 0;
    // s7232: per-triangle bbox vs the current RDP scissor: tin (bbox meets scissor), tout (fully outside), tzero (no scanline:
    // y span < 1 line), area = bbox-clipped px, bin[8] = tin by bbox-centre x across the scissor width; vout = classifier control
    // (same tris against a virtual scissor shifted one full width right: every tri must land out unless it spans past the right edge).
    uint32_t tin = 0, tout = 0, tzero = 0, vout = 0, bin[8] = {}; double area = 0; } s_g1cf;  // s6070
static float s_g1cf_sc[4] = {0, 0, 320, 240};  // s7232 scissor xh, yh, xl, yl (px), carried across VIs
extern "C" void rs64_g1d_tb2(const char* tag);

namespace s4267 {
static const bool on = [] { const char* e = std::getenv("ROGUESQ_S4267"); return e && *e && *e != '0'; }();
static std::mutex m;
static const auto t0 = std::chrono::steady_clock::now();
struct A { uint64_t n = 0; double sum = 0, mx = 0; };
static A agg[36];
static int last_sec = -1;
static std::atomic<int> s7385_r2r{-1}, s7385_ntog{0}; // s7385: renderToRAM value / toggle count, tagged on each [s4267] line
static void flush_locked(int sec) {
    static const char* nm[36] = {"pipeline","texwait","fbwait","ddwait","fullSync","procDL","lleRun","sendDl","fsFlush","fsSubmitFb","fsMisc","fsValidate","fsUpload","fsRspPipe","fsRender","fsEvict","fsProj","fsAdvance","fsTail","fsRsz","fsTiles","fsRenderSync","fsEvictOnly","fsPostEvict","fsScript","fsUpdScreen","ctlSleep","usUpload","usCopyHash","usAdvance","usPre","usRest","usResize","usMemcpy","usHash","pad"};
    std::string o;
    char b[96];
    for (int i = 0; i < 35; ++i) {
        std::snprintf(b, sizeof b, " %s=%llu/%.0fms/max%.0f", nm[i], (unsigned long long)agg[i].n, agg[i].sum, agg[i].mx);
        o += b; agg[i] = A{};
    }
    std::fprintf(stderr, "[s4267] t=%d%s r2r=%d ntog=%d\n", sec, o.c_str(), s7385_r2r.load(), s7385_ntog.load());
}
struct T {
    int p; std::chrono::steady_clock::time_point a = std::chrono::steady_clock::now();
    explicit T(int ph) : p(ph) {}
    ~T();
};
}
extern "C" void rs64_s4267_acc(int phase, double ms) {
    if (!s4267::on) return;
    std::lock_guard<std::mutex> lk(s4267::m);
    const int sec = (int)std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - s4267::t0).count();
    if (s4267::last_sec >= 0 && sec != s4267::last_sec) s4267::flush_locked(s4267::last_sec);
    s4267::last_sec = sec;
    auto& a = s4267::agg[phase]; a.n++; a.sum += ms; if (ms > a.mx) a.mx = ms;
}
s4267::T::~T() { if (on) rs64_s4267_acc(p, std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - a).count()); }

// RDP/RSP register state owned by this file
static uint8_t DMEM[0x1000];
static uint8_t IMEM[0x1000];

static unsigned int MI_INTR_REG      = 0;
static unsigned int DPC_START_REG    = 0;
static unsigned int DPC_END_REG      = 0;
static unsigned int DPC_CURRENT_REG  = 0;
static unsigned int DPC_STATUS_REG   = 0;
static unsigned int DPC_CLOCK_REG    = 0;
static unsigned int DPC_BUFBUSY_REG  = 0;
static unsigned int DPC_PIPEBUSY_REG = 0;
static unsigned int DPC_TMEM_REG     = 0;

static void dummy_check_interrupts() {}

static ultramodern::renderer::SetupResult map_result(RT64::Application::SetupResult r) {
    switch (r) {
    case RT64::Application::SetupResult::Success:                  return ultramodern::renderer::SetupResult::Success;
    case RT64::Application::SetupResult::DynamicLibrariesNotFound: return ultramodern::renderer::SetupResult::DynamicLibrariesNotFound;
    case RT64::Application::SetupResult::InvalidGraphicsAPI:       return ultramodern::renderer::SetupResult::InvalidGraphicsAPI;
    case RT64::Application::SetupResult::GraphicsAPINotFound:      return ultramodern::renderer::SetupResult::GraphicsAPINotFound;
    case RT64::Application::SetupResult::GraphicsDeviceNotFound:   return ultramodern::renderer::SetupResult::GraphicsDeviceNotFound;
    }
    return ultramodern::renderer::SetupResult::GraphicsDeviceNotFound;
}

// ---------------------------------------------------------------------------
// RT64Context — wraps RT64::Application as a RendererContext
// ---------------------------------------------------------------------------
namespace recomp {

class RT64Context : public ultramodern::renderer::RendererContext {
public:
    std::unique_ptr<RT64::Application> app;
    static inline std::atomic<bool> s_hle_disabled{false};

    RT64Context(uint8_t* rdram, ultramodern::renderer::WindowHandle window_handle, bool debug) {
        static unsigned char dummy_rom_header[0x40] = {};

        RT64::Application::Core appCore{};
#if defined(_WIN32)
        appCore.window = window_handle.window;
#elif defined(__linux__) || defined(__ANDROID__)
        appCore.window = window_handle;
#elif defined(__APPLE__)
        appCore.window.window = window_handle.window;
        appCore.window.view   = window_handle.view;
#endif

        appCore.checkInterrupts = dummy_check_interrupts;
        appCore.HEADER  = dummy_rom_header;
        appCore.RDRAM   = rdram;
        appCore.DMEM    = DMEM;
        appCore.IMEM    = IMEM;

        appCore.MI_INTR_REG     = &MI_INTR_REG;
        appCore.DPC_START_REG   = &DPC_START_REG;
        appCore.DPC_END_REG     = &DPC_END_REG;
        appCore.DPC_CURRENT_REG = &DPC_CURRENT_REG;
        appCore.DPC_STATUS_REG  = &DPC_STATUS_REG;
        appCore.DPC_CLOCK_REG   = &DPC_CLOCK_REG;
        appCore.DPC_BUFBUSY_REG = &DPC_BUFBUSY_REG;
        appCore.DPC_PIPEBUSY_REG= &DPC_PIPEBUSY_REG;
        appCore.DPC_TMEM_REG    = &DPC_TMEM_REG;

        ultramodern::renderer::ViRegs* vi = ultramodern::renderer::get_vi_regs();
        appCore.VI_STATUS_REG         = &vi->VI_STATUS_REG;
        appCore.VI_ORIGIN_REG         = &vi->VI_ORIGIN_REG;
        appCore.VI_WIDTH_REG          = &vi->VI_WIDTH_REG;
        appCore.VI_INTR_REG           = &vi->VI_INTR_REG;
        appCore.VI_V_CURRENT_LINE_REG = &vi->VI_V_CURRENT_LINE_REG;
        appCore.VI_TIMING_REG         = &vi->VI_TIMING_REG;
        appCore.VI_V_SYNC_REG         = &vi->VI_V_SYNC_REG;
        appCore.VI_H_SYNC_REG         = &vi->VI_H_SYNC_REG;
        appCore.VI_LEAP_REG           = &vi->VI_LEAP_REG;
        appCore.VI_H_START_REG        = &vi->VI_H_START_REG;
        appCore.VI_V_START_REG        = &vi->VI_V_START_REG;
        appCore.VI_V_BURST_REG        = &vi->VI_V_BURST_REG;
        appCore.VI_X_SCALE_REG        = &vi->VI_X_SCALE_REG;
        appCore.VI_Y_SCALE_REG        = &vi->VI_Y_SCALE_REG;

        RT64::ApplicationConfiguration appConfig;
        appConfig.useConfigurationFile = false;
        appConfig.detectDataPath = false;

        app = std::make_unique<RT64::Application>(appCore, appConfig);
        // Dev mode default: ON for Debug builds (so F1 inspector is available),
        // OFF for Release. Override either way with ROGUESQ_HLE_DEV_MODE=0/1.
        // The inspector can be unstable with our HLE flow under load — fall
        // back to ROGUESQ_HLE_DEV_MODE=0 if it locks up an investigation.
#ifdef _DEBUG
        bool dev_mode_on = true;
#else
        bool dev_mode_on = false;
#endif
        if (const char* v = std::getenv("ROGUESQ_HLE_DEV_MODE")) {
            dev_mode_on = (v[0] && v[0] != '0');
        }
        app->userConfig.developerMode = debug || dev_mode_on;
        app->userConfig.displayBuffering = RT64::UserConfiguration::DisplayBuffering::Triple;
        // G1d (s6103): ROGUESQ_ASPECT=orig|expand|<w>:<h> selects RT64 output aspect. Opt-in; unset = retail (Original).
        // s6928: ROGUESQ_VI_SHAPE sizes the picture from VI geometry in the presenter, so the target keeps the fb's own shape; a Manual
        // aspect here would pillar the content inside the target (652x444 at 16:9 came out 0.826 of the window both ways).
        const char* vshape = std::getenv("ROGUESQ_VI_SHAPE");
        const bool vi_shape = vshape && *vshape && *vshape != '0';
        if (const char* as = vi_shape ? nullptr : std::getenv("ROGUESQ_ASPECT")) {
            using AR = RT64::UserConfiguration::AspectRatio;
            if (!strcmp(as, "expand") || !strcmp(as, "auto")) { app->userConfig.aspectRatio = AR::Expand; app->userConfig.extAspectRatio = AR::Expand; }
            else if (const char* c = strchr(as, ':')) { double w = atof(as), h = atof(c + 1); if (w > 0 && h > 0) { app->userConfig.aspectRatio = AR::Manual; app->userConfig.aspectTarget = w / h; } }
            fprintf(stderr, "[g1d] ROGUESQ_ASPECT=%s applied\n", as);
        }
        // s6793: RT64 reads resolutionMultiplier only in Resolution::Manual; the default WindowIntegerScale ignored it,
        // so ROGUESQ_RESMULT was a no-op (rm1/rm2 window shots pixel-identical). Unset keeps the window-derived scale.
        if (const char* rm = std::getenv("ROGUESQ_RESMULT")) {
            double m = std::atof(rm);
            if (m > 0.0) { app->userConfig.resolution = RT64::UserConfiguration::Resolution::Manual; app->userConfig.resolutionMultiplier = m; }
            fprintf(stderr, "[resmult] ROGUESQ_RESMULT=%s -> Manual x%.2f\n", rm, m);
        }

        // PresentEarly ON by default. Our cinematic stays on a single VI fb
        // address; without PresentEarly, RT64's updateScreen only pushes a
        // present when VI changes or RDRAM at VI_ORIGIN changes — neither
        // happens for HLE single-buffer flow, so rendered fbPairs never
        // reach the swapchain. PresentEarly pushes presents directly from
        // fullSync. Opt out via ROGUESQ_HLE_PRESENT_EARLY=0.
        bool present_early = true;
        if (const char* v = std::getenv("ROGUESQ_HLE_PRESENT_EARLY")) {
            present_early = (v[0] && v[0] != '0');
        }
        if (present_early) {
            app->enhancementConfig.presentation.mode =
                RT64::EnhancementConfiguration::Presentation::Mode::PresentEarly;
        }

        // 2026-05-10: Apply Zelda64Recomp's RT64 enhancement-config settings.
        // Without these, RT64's textureLOD selection and gbi branching take
        // different paths that cause our texture lookups to sample stale or
        // empty TMEM regions → glyph texrects render invisibly.
        //
        // forceBranch=true: forces gbi depth branches, preventing LODs from
        // kicking in for textures that don't have proper mipmap chains.
        //
        // textureLOD.scale=true: scales LODs based on output resolution so
        // higher-res rendering doesn't bias toward LOD 0 unnecessarily.
        app->enhancementConfig.f3dex.forceBranch = true;
        app->enhancementConfig.textureLOD.scale = true;
        // Diagnostic: ROGUESQ_GFX_API=vulkan forces Vulkan instead of the
        // default D3D12 (Automatic on Windows). Lets us isolate whether crashes
        // are DX12-specific or apply to both backends.
        if (const char* api = std::getenv("ROGUESQ_GFX_API")) {
            if (std::string_view(api) == "vulkan") {
                app->userConfig.graphicsAPI = RT64::UserConfiguration::GraphicsAPI::Vulkan;
                fprintf(stderr, "[RT64] graphics API forced to Vulkan via ROGUESQ_GFX_API\n");
            } else if (std::string_view(api) == "d3d12") {
                app->userConfig.graphicsAPI = RT64::UserConfiguration::GraphicsAPI::D3D12;
                fprintf(stderr, "[RT64] graphics API forced to D3D12 via ROGUESQ_GFX_API\n");
            }
        }

        uint32_t thread_id = 0;
#ifdef _WIN32
        thread_id = window_handle.thread_id;
#endif
#ifdef __APPLE__
        rs64_panel_install_hooks();  // s7620 G6b step 3: F6 Controls panel (RT64 post-VI draw hook, Metal)
#endif
        setup_result = map_result(app->setup(thread_id));
        if (setup_result != ultramodern::renderer::SetupResult::Success) {
            fprintf(stderr, "[RT64] setup failed: %d\n", (int)setup_result);
            app = nullptr;
        }
        else {
            // Propagate construction-time enhancementConfig changes (e.g.
            // PresentEarly) into RT64's internal state. setup() initializes
            // before these are read, so without this call the changes stay
            // dormant.
            app->updateEnhancementConfig();
            // ROGUESQ_NO_GPU_COPY=1 — force framebuffer.copyWithGPU off so
            // texture loads that overlap a tracked color image fall back to
            // RDRAM instead of a GPU tile-copy. Hangar-floor A/B: the
            // remaining orange/black band looks like a mis-mapped FB sample.
            if (const char *v = std::getenv("ROGUESQ_NO_GPU_COPY")) {
                if (v[0] && v[0] != '0') {
                    app->emulatorConfig.framebuffer.copyWithGPU = false;
                    app->updateEmulatorConfig();
                    fprintf(stderr, "[RT64] framebuffer.copyWithGPU forced OFF via ROGUESQ_NO_GPU_COPY\n");
                }
            }
            // s7385 ROGUESQ_RENDER_TO_RAM=0 (opt-in; unset = RT64 default on): turn off the Gfx-thread renderToRDRAM
            // pass in State::fullSync (RSP processor + FramebufferRenderer submitRasterScene + RDRAM writeback +
            // hashTracking). s7384 measured every raster scene drawn twice per frame (Gfx thread + RT64 Workload).
            // A/B: does the game ever read the rendered framebuffer back from RDRAM?
            if (const char *v = std::getenv("ROGUESQ_RENDER_TO_RAM")) {
                if (v[0] == '0') {
                    app->emulatorConfig.framebuffer.renderToRAM = false;
                    app->updateEmulatorConfig();
                    fprintf(stderr, "[s7385] framebuffer.renderToRAM forced OFF via ROGUESQ_RENDER_TO_RAM=0\n");
                }
            }
            fprintf(stderr, "[RT64] enhancementConfig: presentMode=%d forceBranch=%d textureLOD.scale=%d copyWithGPU=%d\n",
                    (int)app->enhancementConfig.presentation.mode,
                    (int)app->enhancementConfig.f3dex.forceBranch,
                    (int)app->enhancementConfig.textureLOD.scale,
                    (int)app->emulatorConfig.framebuffer.copyWithGPU);
            fflush(stderr);
        }
        if (app && app->appWindow) {
            // Diagnostic: dump the post-setup state of RT64's window/filter
            // so we know whether F1-F4 keypresses can reach the inspector.
            fprintf(stderr,
                "[RT64] post-setup: sdlWindow=%p sdlEventFilterInstalled=%d windowHook=%p developerMode=%d usesWindowMessageFilter=%d\n",
                (void*)app->appWindow->sdlWindow,
                (int)app->appWindow->sdlEventFilterInstalled,
#ifdef _WIN32
                (void*)app->appWindow->windowHook,
#else
                (void*)nullptr,
#endif
                (int)app->userConfig.developerMode,
                (int)app->usesWindowMessageFilter());
            fflush(stderr);
        }
        g_rt64_app.store(app.get());
    }

    bool valid() override {
        return app != nullptr;
    }

    bool update_config(const ultramodern::renderer::GraphicsConfig&,
                       const ultramodern::renderer::GraphicsConfig&) override {
        return true;
    }

    void enable_instant_present() override {
        // PresentEarly is set at construction (see ctor); this host hook
        // would re-apply it, but constructor-time setup is sufficient.
        // Respects ROGUESQ_HLE_PRESENT_EARLY=0 opt-out.
        if (app) {
            bool present_early = true;
            if (const char* v = std::getenv("ROGUESQ_HLE_PRESENT_EARLY")) {
                present_early = (v[0] && v[0] != '0');
            }
            if (present_early) {
                app->enhancementConfig.presentation.mode =
                    RT64::EnhancementConfiguration::Presentation::Mode::PresentEarly;
                app->updateEnhancementConfig();
            }
        }
    }

    void send_dl(const OSTask* task) override {
        s4267::T s4267_total(7);
        struct RdpqScope { RdpqScope() { ultramodern::rs64_rdpq_task_enter(); } ~RdpqScope() { ultramodern::rs64_rdpq_task_exit(); } } rdpq_scope; // s6705
        const uint32_t m5_task_seq = rs64_m5_host_send_begin(
            static_cast<uint32_t>(task->t.data_ptr));
        {   // s7766 input latency: ROGUESQ_S7766_INLAT=1 -> one [inlat-dl] row per gfx task hand-off with the camera heading
            // floats the game thread left in RAM when it submitted this display list (0x80138D20+0x2C elements 0 and 2, the
            // [g3c] cam= matrix), so tools/s7766_inlat.py can tag each task with the state it renders. n = task ordinal here.
            static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7766_INLAT"); return e && *e == '1'; }();
            static uint64_t n = 0;
            if (on && app) {
                const uint8_t* rd = app->core.RDRAM; float c0 = 0.0f, c2 = 0.0f;
                // RDRAM is non-null whenever app is (set at init; the dump path below derefs it unconditionally). No
                // null test here: s7465 census read one as "RDRAM may be null" and flagged the dump path's rdram[] at :823.
                memcpy(&c0, rd + 0x138D20 + 0x2C, 4); memcpy(&c2, rd + 0x138D20 + 0x2C + 8, 4);
                fprintf(stderr, "[inlat-dl] m=%llu n=%llu dl=%08X c0=%.9g c2=%.9g\n", (unsigned long long)mach_absolute_time(),
                        (unsigned long long)n, (unsigned)task->t.data_ptr, (double)c0, (double)c2);
            }
            n++;
        }
        // ROGUESQ_LLE_FORCE=1: route this GFX task through the LLE RSP
        // recompile path INSTEAD of HLE. factor5_gfx_runner reproduces what
        // real-hardware RSP would do — runs boot+main ucode against DMEM,
        // emits RDP byte stream via mtc0 DPC_END writes, src/rsp/dpc_bridge.cpp
        // forwards those bytes to RT64 via processDisplayLists(isHLE=false).
        // This is the path needed for Factor 5's op 0x02 (vertex transform)
        // to actually emit triangles — HLE drops it.
        static int s_lle_force = -1;
        if (s_lle_force < 0) {
            // s6738: default ON (unset = 1, =0 = old HLE default). Every qualification soak ran LLE_FORCE/UNGATED/SOLO=1,
            // but a plain launch (the owner's command) took HLE for all non-hangar tasks: the boot intro cinematic drew a
            // white screen (plain 0/71 scene captures vs 61/64 with the three flags).
            const char* v = std::getenv("ROGUESQ_LLE_FORCE");
            s_lle_force = (v && *v) ? (v[0] != '0') : 1;
            if (s_lle_force) {
                fprintf(stderr, "[lle-force] LLE path enabled for M_GFXTASK; "
                                "HLE send_dl will skip processDisplayLists\n");
                fflush(stderr);
            }
        }
        // s1890: rs64_is_hangar_vi() reads shared VI regs from the render
        // thread every M_GFXTASK, unconditionally, since the s1856/s1872
        // hangar-gate work (post-s844). ROGUESQ_SKIP_HANGAR_PROBE=1 disables
        // that read to test whether it is implicated in the s1888/s1889
        // VI-1024 reachability regression.
        static int s_skip_hangar_probe = -1;
        if (s_skip_hangar_probe < 0) {
            const char* v = std::getenv("ROGUESQ_SKIP_HANGAR_PROBE");
            s_skip_hangar_probe = (v && *v && v[0] != '0') ? 1 : 0;
        }
        const bool in_hangar = s_skip_hangar_probe ? false : (rs64_is_hangar_vi() != 0);
        // Hangar LLE does not require LLE_FORCE. Attribution LLE never
        // leaves VI 640 (s1856, s1872), so the hangar census uses HLE
        // through the frontend and switches to LLE-solo only at hangar
        // origins 0x006ab400 / 0x006ab800.
        if (app && (s_lle_force || in_hangar)) {
            // Gate LLE to attribution-shape DLs only. Cinematic-phase tasks
            // hit Unhandled jump target in factor5_ucode_recompiled and
            // corrupt RT64's deferred state (which then asserts 4-bit
            // readback downstream). Attribution DL signature: data_ptr =
            // 0x80720108 for task #1, 0x80720318 for task #2 of the same
            // phase (observed). Both live in the 0x80720000 page. Restrict
            // LLE to data_ptr in that page so cinematic tasks bypass it.
            //
            // ROGUESQ_LLE_UNGATED=1 disables this gate (debug/regression).
            const uint32_t dlp = (uint32_t)task->t.data_ptr;
            static int s_lle_ungated = -1;
            if (s_lle_ungated < 0) {
                const char* v = std::getenv("ROGUESQ_LLE_UNGATED");
                s_lle_ungated = (v && *v) ? (v[0] != '0') : 1;  // s6738: default ON
            }
            const bool in_attribution_page = ((dlp & 0xFFFF0000u) == 0x80720000u);
            static int s_lle_hangar_only = -1;
            if (s_lle_hangar_only < 0) {
                const char* v = std::getenv("ROGUESQ_LLE_HANGAR_ONLY");
                s_lle_hangar_only = (v && *v && v[0] != '0') ? 1 : 0;
            }
            const bool lle_this = s_lle_ungated
                || in_hangar
                || (s_lle_force && in_attribution_page && !s_lle_hangar_only);
            if (lle_this) {
                static int s_n = 0;
                int n = ++s_n;
                int r;
                { s4267::T s4267_run(6); r = rs64_run_lle_gfx(app->core.RDRAM, task); }
                if (rs64_tl_on) rs64_tl(7, (uint32_t)r); // s6711 RSP ucode exit (events.cpp timeline)
                if (n <= 8 || (n & 31) == 0) {
                    const char *gate = in_attribution_page ? "attr"
                        : (in_hangar ? "hangar" : "ungated");
                    fprintf(stderr, "[lle send_dl #%d] gate=%s exit=%d task->ucode=0x%08X dl=0x%08X\n",
                            n, gate,
                            r, (unsigned)task->t.ucode, dlp);
                    fflush(stderr);
                }
                // ROGUESQ_LLE_SOLO=1 skips the HLE fallthrough below. By default
                // we run HLE in parallel so HLE's green fillRect-override marker
                // stays visible alongside whatever LLE produces.
                static int s_lle_solo = -1;
                if (s_lle_solo < 0) {
                    const char* v = std::getenv("ROGUESQ_LLE_SOLO");
                    s_lle_solo = (v && *v) ? (v[0] != '0') : 1;  // s6738: default ON
                }
                if (s_lle_solo || in_hangar) {
                    rs64_m5_host_edge("send-return", m5_task_seq,
                                      static_cast<uint32_t>(task->t.data_ptr),
                                      0, 0, 1, -1, -1);
                    return;
                }
                // Fall through to HLE below.
            } else {
                // Cinematic / N64-logo / other tasks: HLE only. Skip LLE.
                static int s_skip_count = 0;
                int sn = ++s_skip_count;
                if (sn <= 4 || (sn & 127) == 0) {
                    fprintf(stderr, "[lle send_dl skip #%d] non-attribution DL dl=0x%08X (LLE bypassed)\n",
                            sn, dlp);
                    fflush(stderr);
                }
            }
        }

        // Standard HLE pipeline (matches Zelda64Recompiled / Starfox64Recomp).
        // RT64's GBI database now includes the Factor 5 ucode signatures (see
        // lib/rt64/src/gbi/rt64_gbi_f3dfactor5.cpp), so loadUCodeGBI matches
        // and dispatches commands via the F3DFACTOR5 handlers.
        //
        // Mask 0x3FFFFFF strips the KSEG0 bits to get the physical RDRAM
        // offset that processDisplayLists expects.
        // ROGUESQ_LOG_OPCODE_HIST=1: per-call opcode histogram of the first
        // 256 DL commands at task->t.data_ptr. Lets us compare which
        // F3DFACTOR5 opcodes fire during attribution vs N64-logo phase to
        // test the "some opcode carries attribution-glyph semantics but is
        // currently no-op'd in our HLE" hypothesis.
        if (app) {
            // ROGUESQ_DUMP_UCODE=path — dump task ucode (IMEM) + ucode_data
            // (DMEM-bound segment) to disk on the first call so the F3DFACTOR5
            // ucode can be disassembled offline to decode op 0x02 semantics.
            static int s_dumped_ucode = 0;
            if (!s_dumped_ucode) {
                const char* dump_path = std::getenv("ROGUESQ_DUMP_UCODE");
                if (dump_path && *dump_path) {
                    s_dumped_ucode = 1;
                    const uint32_t ucode_phys = (uint32_t)task->t.ucode & 0x3FFFFFF;
                    const uint32_t udata_phys = (uint32_t)task->t.ucode_data & 0x3FFFFFF;
                    const uint32_t udata_size = task->t.ucode_data_size ? task->t.ucode_data_size : 0x800;
                    uint8_t* rdram = app->core.RDRAM;
                    // Standard RSP ucode IMEM is 4KB. Dump 8KB to be safe.
                    char ipath[512], dpath[512];
                    snprintf(ipath, sizeof ipath, "%s.imem.bin", dump_path);
                    snprintf(dpath, sizeof dpath, "%s.dmem.bin", dump_path);
                    FILE* f = fopen(ipath, "wb");
                    if (f) {
                        uint8_t buf[0x2000];
                        for (uint32_t i = 0; i < sizeof(buf); ++i) {
                            uint32_t off = ucode_phys + i;
                            buf[i] = (off < (rs64_ram_top - 0x80000000u)) ? rdram[off ^ 3] : 0;
                        }
                        fwrite(buf, 1, sizeof(buf), f);
                        fclose(f);
                        fprintf(stderr, "[dump-ucode] wrote IMEM %u bytes to %s (src=0x%08X)\n",
                                (unsigned)sizeof(buf), ipath, ucode_phys);
                    }
                    f = fopen(dpath, "wb");
                    if (f) {
                        std::vector<uint8_t> buf(udata_size);
                        for (uint32_t i = 0; i < udata_size; ++i) {
                            uint32_t off = udata_phys + i;
                            buf[i] = (off < (rs64_ram_top - 0x80000000u)) ? rdram[off ^ 3] : 0;
                        }
                        fwrite(buf.data(), 1, udata_size, f);
                        fclose(f);
                        fprintf(stderr, "[dump-ucode] wrote DMEM %u bytes to %s (src=0x%08X)\n",
                                udata_size, dpath, udata_phys);
                    }
                    fflush(stderr);
                }
            }
            // ROGUESQ_DUMP_VTXDATA=path — dump 64 KB starting at RAM
            // 0x80700000 and 0x80710000 on the first send_dl call. These
            // are the addresses op 0x01 references in attribution DLs
            // (alternating between consecutive submissions). Offline
            // decode reveals what vertex / asset data the F3DFACTOR5
            // ucode reads to drive op 0x02's matrix-vertex pipeline.
            static int s_dumped_vtx = 0;
            if (!s_dumped_vtx) {
                const char* dump_path = std::getenv("ROGUESQ_DUMP_VTXDATA");
                if (dump_path && *dump_path) {
                    s_dumped_vtx = 1;
                    uint8_t* rdram = app->core.RDRAM;
                    // Extended dump set: add the .data segment region around
                    // the state-setup sub-DL (0x80037658) to search for
                    // static vertex arrays.
                    for (uint32_t base : { 0x00700000u, 0x00710000u, 0x00037000u }) {
                        char path[512];
                        snprintf(path, sizeof path, "%s.0x%08X.bin", dump_path, base);
                        FILE* f = fopen(path, "wb");
                        if (f) {
                            uint8_t buf[0x10000];
                            for (uint32_t i = 0; i < sizeof(buf); ++i) {
                                uint32_t off = base + i;
                                buf[i] = (off < (rs64_ram_top - 0x80000000u)) ? rdram[off ^ 3] : 0;
                            }
                            fwrite(buf, 1, sizeof(buf), f);
                            fclose(f);
                            fprintf(stderr, "[dump-vtxdata] wrote 64 KB to %s\n", path);
                        }
                    }
                    fflush(stderr);
                }
            }
            static int s_op_hist = -1;
            if (s_op_hist < 0) {
                const char* v = std::getenv("ROGUESQ_LOG_OPCODE_HIST");
                s_op_hist = (v && *v && v[0] != '0') ? 1 : 0;
            }
            if (s_op_hist) {
                static int s_oh_count = 0;
                int ohn = ++s_oh_count;
                const uint32_t dl_phys = (uint32_t)task->t.data_ptr & 0x3FFFFFF;
                uint8_t* rdram = app->core.RDRAM;
                uint32_t hist[256] = {0};
                uint32_t total = 0;
                // Walk up to 256 8-byte commands (or stop on G_ENDDL=0xDF or
                // a zeroed slot). Follow at most 2 G_DL jumps so we get a
                // representative sample even when Factor 5 chains via G_DL.
                uint32_t addr = dl_phys;
                uint32_t stack[16];
                int sp = 0;
                int jumps_left = 16;
                // Track first 8 instances of each "interesting" no-op'd
                // opcode so we can see if their payloads encode something
                // meaningful (like a DMA src/dst pair).
                uint64_t op02_payloads[8] = {0};
                int op02_count = 0;
                uint64_t op80_payloads[8] = {0};
                int op80_count = 0;
                for (int i = 0; i < 1024; ++i) {
                    if (addr + 8u > (rs64_ram_top - 0x80000000u)) break;
                    uint8_t op = rdram[addr ^ 3];
                    hist[op]++;
                    total++;
                    if (op == 0x02 && op02_count < 8) {
                        uint64_t w = 0;
                        for (int k = 0; k < 8; ++k) {
                            w = (w << 8) | rdram[(addr + k) ^ 3];
                        }
                        op02_payloads[op02_count++] = w;
                    }
                    if (op == 0x80 && op80_count < 8) {
                        uint64_t w = 0;
                        for (int k = 0; k < 8; ++k) {
                            w = (w << 8) | rdram[(addr + k) ^ 3];
                        }
                        op80_payloads[op80_count++] = w;
                    }
                    // F3D-style G_ENDDL = 0xB8 (Factor 5 uses F3D's 0xB8,
                    // not F3DEX2's 0xDF). Pop on B8.
                    if (op == 0xB8) {
                        if (sp > 0) { addr = stack[--sp]; continue; }
                        break;
                    }
                    if (op == 0xDF) break;
                    // F3D G_DL = 0x06, F3DEX2 G_DL = 0xDE.
                    // 0x06 in Factor 5: branch=byte1 (0=push, 1=branch).
                    if ((op == 0x06 || op == 0xDE) && jumps_left > 0) {
                        uint8_t branch = rdram[(addr + 1) ^ 3];
                        uint32_t w1 = 0;
                        for (int k = 0; k < 4; ++k) {
                            w1 = (w1 << 8) | rdram[(addr + 4 + k) ^ 3];
                        }
                        uint32_t target = w1 & 0x3FFFFFF;
                        if (branch == 0) {  // G_DL push: save return addr
                            if (sp < 16) stack[sp++] = addr + 8;
                        }
                        addr = target;
                        jumps_left--;
                        continue;
                    }
                    addr += 8;
                }
                // Dump full DL bytes for the first call so we can hand-decode
                // the attribution DL structure.
                if (ohn == 1) {
                    uint32_t a = dl_phys;
                    int dump_stack_sp = 0;
                    uint32_t dump_stack[16];
                    int dump_jumps = 16;
                    fprintf(stderr, "[opcode-hist #1 FULL DL DUMP] start=0x%08X\n", dl_phys);
                    for (int i = 0; i < 256; ++i) {
                        if (a + 8u > (rs64_ram_top - 0x80000000u)) break;
                        uint64_t w = 0;
                        for (int k = 0; k < 8; ++k) {
                            w = (w << 8) | rdram[(a + k) ^ 3];
                        }
                        uint8_t op = rdram[a ^ 3];
                        fprintf(stderr, "  %08X: %016llX  op=%02X\n",
                                a, (unsigned long long)w, op);
                        if (op == 0xB8) {
                            if (dump_stack_sp > 0) { a = dump_stack[--dump_stack_sp]; continue; }
                            break;
                        }
                        if (op == 0xDF) break;
                        if ((op == 0x06 || op == 0xDE) && dump_jumps > 0) {
                            uint8_t branch = rdram[(a + 1) ^ 3];
                            uint32_t w1 = 0;
                            for (int k = 0; k < 4; ++k) {
                                w1 = (w1 << 8) | rdram[(a + 4 + k) ^ 3];
                            }
                            uint32_t target = w1 & 0x3FFFFFF;
                            if (branch == 0) {
                                if (dump_stack_sp < 16) dump_stack[dump_stack_sp++] = a + 8;
                            }
                            a = target;
                            dump_jumps--;
                            continue;
                        }
                        a += 8;
                    }
                    fflush(stderr);
                }
                fprintf(stderr, "[opcode-hist #%d] dl=0x%08X total=%u", ohn, dl_phys, total);
                for (int op = 0; op < 256; ++op) {
                    if (hist[op]) {
                        fprintf(stderr, " %02X=%u", op, hist[op]);
                    }
                }
                fprintf(stderr, "\n");
                if (op02_count > 0) {
                    fprintf(stderr, "[opcode-hist #%d op02 payloads]", ohn);
                    for (int k = 0; k < op02_count; ++k) {
                        fprintf(stderr, " %016llX", (unsigned long long)op02_payloads[k]);
                    }
                    fprintf(stderr, "\n");
                }
                if (op80_count > 0) {
                    fprintf(stderr, "[opcode-hist #%d op80 payloads]", ohn);
                    for (int k = 0; k < op80_count; ++k) {
                        fprintf(stderr, " %016llX", (unsigned long long)op80_payloads[k]);
                    }
                    fprintf(stderr, "\n");
                }
                fflush(stderr);
            }
        }
        if (app) {
            static int s_count = 0;
            static uint32_t s_last_ucode = 0;
            static uint32_t s_last_data = 0;
            int n = ++s_count;
            const bool ucode_changed = (task->t.ucode != s_last_ucode) || (task->t.ucode_data != s_last_data);
            if (n <= 8 || (n & 63) == 0 || ucode_changed) {
                // Capture workload state pre- and post-DL so we can see
                // fbPair growth and presentEarly matcher activity.
                int wq_wc_pre = app->workloadQueue ? (int)app->workloadQueue->writeCursor : -1;
                int pq_wc_pre = app->presentQueue ? (int)app->presentQueue->writeCursor : -1;
                fprintf(stderr,
                    "[hle send_dl #%d]%s type=%u ucode=0x%08X data=0x%08X dl=0x%08X size=%u wq=%d pq=%d\n",
                    n, ucode_changed ? " [UCODE-CHANGE]" : "",
                    (unsigned)task->t.type, (unsigned)task->t.ucode,
                    (unsigned)task->t.ucode_data, (unsigned)task->t.data_ptr,
                    (unsigned)task->t.data_size,
                    wq_wc_pre, pq_wc_pre);
                fflush(stderr);
            }
            s_last_ucode = task->t.ucode;
            s_last_data = task->t.ucode_data;
            if (s_hle_disabled.load(std::memory_order_relaxed)) {
                rs64_m5_host_edge("send-return", m5_task_seq,
                                  static_cast<uint32_t>(task->t.data_ptr),
                                  0, 0, 1, -1, -1);
                return;
            }
            app->state->rsp->reset();
            app->interpreter->loadUCodeGBI(
                task->t.ucode & 0x3FFFFFF,
                task->t.ucode_data & 0x3FFFFFF,
                true);
#ifdef _WIN32
            static std::atomic<int> s_seh_streak{0};
            __try {
                int wq_wc_pre = app->workloadQueue ? (int)app->workloadQueue->writeCursor : -1;
                int pq_wc_pre = app->presentQueue ? (int)app->presentQueue->writeCursor : -1;
                app->processDisplayLists(app->core.RDRAM,
                                         task->t.data_ptr & 0x3FFFFFF,
                                         0,
                                         /*isHLE*/ true);
                s_seh_streak.store(0, std::memory_order_relaxed);
                // Post-DL: see if workload + present cursors moved. Track
                // distinct transition patterns so we can spot when pq
                // *should* be advancing but isn't.
                if (n <= 8 || (n & 63) == 0) {
                    int wq_wc_post = app->workloadQueue ? (int)app->workloadQueue->writeCursor : -1;
                    int pq_wc_post = app->presentQueue ? (int)app->presentQueue->writeCursor : -1;
                    int wc = app->workloadQueue ? (int)app->workloadQueue->writeCursor : 0;
                    auto& wl = app->workloadQueue->workloads[wc];
                    auto& wlPrev = app->workloadQueue->workloads[(wc + app->workloadQueue->workloads.size() - 1) % app->workloadQueue->workloads.size()];
                    fprintf(stderr,
                        "[hle send_dl #%d post] wq=%d->%d pq=%d->%d nextFbPairs=%u prevFbPairs=%u\n",
                        n, wq_wc_pre, wq_wc_post, pq_wc_pre, pq_wc_post,
                        (unsigned)wl.fbPairCount, (unsigned)wlPrev.fbPairCount);
                    fflush(stderr);
                }

                // Default ON: needed for stability in cinematic phase (workload's
                // fbPairCount grows unbounded without flushing). Disable via
                // ROGUESQ_HLE_AUTO_FULLSYNC=0 to investigate cases where it might
                // double-fire and overwrite a present.
                static bool s_auto_fullsync = []() {
                    const char* v = std::getenv("ROGUESQ_HLE_AUTO_FULLSYNC");
                    if (v && v[0]) return v[0] != '0';
                    return true;
                }();
                if (app->state) {
                    // Conditional fullSync. Factor 5's cinematic DLs emit fullSync
                    // mid-DL but the post-fullSync workload accumulates fbPairs
                    // unbounded (60→229+ in one DL) without committing, eventually
                    // tripping RT64's internal limits. We flush when the current
                    // workload has uncommitted work; the gate skips the case where
                    // Factor 5's natural fullSync already advanced the cursor
                    // (next workload starts empty so needs_flush=false).
                    // Override OFF via ROGUESQ_HLE_AUTO_FULLSYNC=0 (default ON).
                    if (s_auto_fullsync) {
                        int wc = app->state->ext.workloadQueue->writeCursor;
                        auto& wl = app->state->ext.workloadQueue->workloads[wc];
                        const bool needs_flush = (wl.fbPairCount > wl.fbPairSubmitted) ||
                                                 (app->state->drawCall.triangleCount > 0);
                        if (needs_flush) {
                            app->state->dlCpuProfiler.start();
                            app->state->fullSync();
                            app->state->dlCpuProfiler.end();
                        }
                    }
                }
            }
            __except (EXCEPTION_EXECUTE_HANDLER) {
                // Log and try to keep going. The previous behavior latched
                // s_hle_disabled on first SEH and killed all subsequent
                // rendering — too aggressive: transient boot AVs would
                // permanently kill the screen. Only latch-off if SEHs
                // hit 3 IN A ROW with no successful submission between.
                int streak = s_seh_streak.fetch_add(1, std::memory_order_relaxed) + 1;
                fprintf(stderr, "[hle send_dl] SEH streak=%d in processDisplayLists "
                                "ucode=0x%08X data=0x%08X dl=0x%08X%s\n",
                                streak,
                                (unsigned)task->t.ucode, (unsigned)task->t.ucode_data,
                                (unsigned)task->t.data_ptr,
                                streak >= 3 ? " — HLE submission DISABLED" : "");
                fflush(stderr);
                if (streak >= 3) {
                    s_hle_disabled.store(true, std::memory_order_relaxed);
                }
                if (app && app->state) {
                    app->state->dlCpuProfiler.startedTimestamp = RT64::Timestamp{};
                }
            }
#else
            app->processDisplayLists(app->core.RDRAM,
                                     task->t.data_ptr & 0x3FFFFFF,
                                     0,
                                     /*isHLE*/ true);
#endif
            rs64_m5_host_edge("send-return", m5_task_seq,
                              static_cast<uint32_t>(task->t.data_ptr),
                              0, 0, 1, -1, -1);
        }
    }

    void update_screen() override {
        rs64_scr_t0 = rs64_scr_now();
        // s6884: ROGUESQ_RDP_SCREEN_JOB=1 queues updateScreen FIFO on the RDP worker instead of waiting for the task's tail here.
        const bool screen_job = ultramodern::rs64_rdpq_screen_ready();
        if (!screen_job) ultramodern::rs64_rdpq_drain(); // s6705: no-op unless ROGUESQ_RDP_ASYNC queued ranges outside a task
        rs64_scr_t1 = rs64_scr_now();
        if (app) {
            ultramodern::renderer::ViRegs* boundary_vi =
                ultramodern::renderer::get_vi_regs();
            rs64_vi_boundary_log("screen", rs64_vi_boundary_screen_request(),
                                 boundary_vi->VI_ORIGIN_REG,
                                 boundary_vi->VI_WIDTH_REG);

            // Always log first 4 + every 64th update_screen so we can tell
            // whether VI events are firing at all. The visual-output question
            // depends entirely on this being called regularly.
            static int s_n = 0;
            static bool s_filter_logged = false;
            ++s_n;
            { rs64_s4899_vi((uint32_t)s_n, ultramodern::renderer::get_vi_regs()->VI_WIDTH_REG); } // s4899
            rs64_vi_n_g = (uint32_t)s_n; // s5816 VI counter for guest-side diagnostics
            {
                // s6808 G3: ROGUESQ_VI_WALL=<file>: one row per update_screen (wall s, VI #, VI width, osViSetMode calls,
                // cumulative host us so far, run-token holder pri<<16|OSId) to put the title AI feed gaps on a wall clock.
                static FILE* s_vw = [] { const char* e = std::getenv("ROGUESQ_VI_WALL"); return (e && *e) ? fopen(e, "w") : nullptr; }();
                if (s_vw) {
                    fprintf(s_vw, "%.4f %d %u %u %llu %x\n", rs64_elapsed_seconds(), s_n,
                            ultramodern::renderer::get_vi_regs()->VI_WIDTH_REG, rs64_vimode_n_g,
                            (unsigned long long)rs64_vimode_us_g, (unsigned)rs64_run_tok_g);
                    fflush(s_vw);
                }
            }

            {
                // s6835 boot freeze: s6814 a30_s2 stopped RDP frames right after partitionFramebufferMemory(640,480),
                // i.e. inside advanceVideoFrame's drain loop (0x80018264: waitOnVideoQueue, scan arbiter states
                // 0x80128EAA[count 0x80128EAD] for 3/4, repeat). When fullsyncs stall for STALL_VI VIs, dump the
                // arbiter block, the two queues that loop blocks on (video 0x80128CF0, frame-sync 0x80128D10) and the retrace
                // thread's VI event queue 0x80114388, twice
                // (at 1x and 2x STALL_VI) to tell a stuck slot from a moving one. Passive, default on, silent unless
                // stalled. ROGUESQ_STALL_DUMP=0 off; ROGUESQ_STALL_DUMP_VI=<n> threshold (600); ROGUESQ_STALL_DUMP_TEST=<vi>
                // forces one dump at that VI (positive control for the dump path).
                static int s_sd = -1, s_sd_vi = 600, s_sd_test = 0;
                if (s_sd < 0) {
                    const char* e = std::getenv("ROGUESQ_STALL_DUMP"); s_sd = !(e && *e == '0');
                    if ((e = std::getenv("ROGUESQ_STALL_DUMP_VI")) && *e) s_sd_vi = std::max(1, atoi(e));
                    if ((e = std::getenv("ROGUESQ_STALL_DUMP_TEST")) && *e) s_sd_test = atoi(e);
                }
                static uint32_t s_sd_fs = 0; static int s_sd_since = 0, s_sd_n = 0;
                uint32_t fsnow = rs64_dpc_get_cumulative_fullsyncs();
                if (fsnow != s_sd_fs) { s_sd_fs = fsnow; s_sd_since = s_n; }
                int stalled = s_n - s_sd_since;
                bool test = s_sd_test > 0 && s_n == s_sd_test;
                if (s_sd && app->core.RDRAM && (test || (s_sd_n < 8 && (stalled == s_sd_vi || stalled == 2 * s_sd_vi)))) {
                    const uint8_t* R = app->core.RDRAM;
                    auto b = [R](uint32_t a) { return (unsigned)R[(a & 0x7FFFFF) ^ 3]; };
                    auto w = [R](uint32_t a) { uint32_t v; memcpy(&v, R + (a & 0x7FFFFC), 4); return (unsigned)v; };
                    ++s_sd_n;
                    fprintf(stderr, "[stall-dump] vi=%d stalled_vi=%d fs=%u test=%d t=%.1f origin=0x%06X count=%u states=%u,%u,%u,%u "
                            "fb=%08X,%08X,%08X,%08X e90=%08X e94=%08X vflag(80037808)=%u\n",
                            s_n, stalled, fsnow, test ? 1 : 0, rs64_elapsed_seconds(),
                            ultramodern::renderer::get_vi_regs()->VI_ORIGIN_REG & 0xFFFFFF, b(0x80128EAD),
                            b(0x80128EAA), b(0x80128EAB), b(0x80128EAC), b(0x80128EAE),
                            w(0x80128E98), w(0x80128E9C), w(0x80128EA0), w(0x80128EA4), w(0x80128E90), w(0x80128E94),
                            b(0x80037808));
                    // OSMesgQueue: mtqueue, fullqueue, validCount, first, msgCount, msg
                    for (uint32_t q : {0x80128CF0u, 0x80128D10u, 0x80114388u}) // video, frame-sync mutex, retrace thread VI events
                        fprintf(stderr, "[stall-dump] queue %08X mtq=%08X fullq=%08X valid=%d first=%d count=%d msg=%08X\n", q,
                                w(q), w(q + 4), (int)w(q + 8), (int)w(q + 12), (int)w(q + 16), w(q + 20));
                    for (uint32_t a = 0x80128E80u; a < 0x80128EE0u; a += 32)
                        fprintf(stderr, "[stall-dump] %08X: %08X %08X %08X %08X %08X %08X %08X %08X\n", a, w(a), w(a + 4),
                                w(a + 8), w(a + 12), w(a + 16), w(a + 20), w(a + 24), w(a + 28));
                    rs64_waittab_dump(); // s7191: per-thread waits + CF0 ring
                    // s6993: the first live capture (s6993s L4, 16:9 boot fade) showed the retrace thread blocked on a FULL
                    // send to 0x80128CF0 while no thread waits on any of the three queues and vflag=0, so the game thread
                    // sits in some other wait. Self-sample once per stall (first dump only) so the next recurrence names
                    // every thread's host stack: `sample <pid> 3` into ROGUESQ_STALL_SAMPLE_DIR (default cwd), detached so
                    // the VI thread is not held. ROGUESQ_STALL_SAMPLE=0 disables. Summarise with tools/sample_game_threads.py.
                    static bool s_sd_sampled = false;
                    static const bool s_sd_sample_on = [] { const char* e = std::getenv("ROGUESQ_STALL_SAMPLE"); return !(e && *e == '0'); }();
                    if (s_sd_sample_on && !s_sd_sampled) {
                        s_sd_sampled = true;
                        const char* dir = std::getenv("ROGUESQ_STALL_SAMPLE_DIR");
                        char fn[96]; std::snprintf(fn, sizeof(fn), "/rs64_stall_%d_vi%d.sample.txt", (int)getpid(), s_n);
                        // s7962: shell-quoted dir (an apostrophe in it broke the old '%s'); no fixed-size cmd buffer.
                        const std::string cmd = "/usr/bin/sample " + std::to_string((int)getpid()) + " 3 -file " +
                            rs64_shell_quote(std::string((dir && *dir) ? dir : ".") + fn) + " >/dev/null 2>&1";
                        fprintf(stderr, "[stall-dump] self-sample: %s\n", cmd.c_str());
                        std::thread([c = cmd] { int rc = std::system(c.c_str());
                            fprintf(stderr, "[stall-dump] self-sample done rc=%d\n", rc); fflush(stderr); }).detach();
                    }
                    fflush(stderr);
                }
            }

            // Watchdog moved to its own thread (rs64_cine_start_watchdog_thread)
            // because the gfx_thread can itself be deadlocked on the same mutex
            // chain that's hanging the game thread.

            // Host-side buffer-arbiter state-machine driver. Under HLE, the game's
            // bufferArbiterProducerMark blocks on a recv that's supposed to be
            // signaled by viRetraceHandlerThread; if that signal misses (timing),
            // slot states stagnate in 0/1/2 and func_8000BF60's scan loop spins
            // waiting for state 3 or 4. We auto-advance any slot in state 2 → 3
            // (CONSUMED), state 3 → 4 (PRESENTED), state 4 → 5 (DISPLAYED),
            // state 5 → 0 (FREE). This mimics what viRetraceHandlerThread would
            // naturally do over multiple ticks but condenses it into one
            // update_screen pass. Gated by ROGUESQ_FORCE_BUFFER_PROGRESS=1.
            static const bool s_force_buffer = [](){
                const char *v = std::getenv("ROGUESQ_FORCE_BUFFER_PROGRESS");
                return v && v[0] && v[0] != '0';
            }();
            if (s_force_buffer && app->core.RDRAM) {
                // Slot state array at 0x80128EAA[N]; count byte at 0x80128EAD.
                // Conservative driver: only advance the retrace-thread's
                // transitions (4 PRESENTED → 5 DISPLAYED → 0 FREE).
                // Producer-mark's transitions (2→3 and X→4) are left to fire
                // naturally via bufferArbiterProducerMark — bypassing those
                // would cause ultramodern sync invariants to break (saw an AV
                // in ultramodern's mesgqueue/threads area on the aggressive
                // version of this driver at iter 1255).
                const uint32_t STATE_BASE = 0x128EAA;
                const uint32_t COUNT_ADDR = 0x128EAD;
                if (COUNT_ADDR < (rs64_ram_top - 0x80000000u)) {
                    uint8_t total = app->core.RDRAM[COUNT_ADDR ^ 3];
                    if (total > 0 && total <= 8) {
                        for (uint8_t i = 0; i < total; i++) {
                            uint32_t addr = STATE_BASE + i;
                            if (addr >= (rs64_ram_top - 0x80000000u)) continue;
                            uint8_t state = app->core.RDRAM[addr ^ 3];
                            switch (state) {
                                case 4: app->core.RDRAM[addr ^ 3] = 5; break;  // PRESENTED → DISPLAYED
                                case 5: app->core.RDRAM[addr ^ 3] = 0; break;  // DISPLAYED → FREE
                                default: break;  // leave 0/1/2/3 to game code
                            }
                        }
                    }
                }
            }

            // Game-state poller: read engine globals via RDRAM and log changes.
            // Tells us whether the game is actually progressing past boot, even
            // when the screen is black. Enable via ROGUESQ_LOG_GAMESTATE=1.
            static const bool s_log_gs = [](){
                const char *v = std::getenv("ROGUESQ_LOG_GAMESTATE");
                return v && v[0] && v[0] != '0';
            }();
            if (s_log_gs && app->core.RDRAM && (s_n & 63) == 0) {
                // Globals from docs/game-architecture.md. RDRAM is little-endian
                // word-swap relative to MIPS BE — use byte index ^ 3.
                auto rb = [&](uint32_t addr) -> uint8_t {
                    if (addr >= (rs64_ram_top - 0x80000000u)) return 0;
                    return app->core.RDRAM[addr ^ 3];
                };
                auto rw = [&](uint32_t addr) -> uint32_t {
                    return (uint32_t(rb(addr)) << 24) | (uint32_t(rb(addr+1)) << 16) |
                           (uint32_t(rb(addr+2)) <<  8) |  uint32_t(rb(addr+3));
                };
                uint8_t curLevel = rb(0x130B70);
                uint8_t curCraft = rb(0x130B41);
                uint32_t cineStatePtr = rw(0x0B0934);
                uint8_t cineStage = rb(0x0B0938);
                uint32_t curCutsceneFile = rw(0x0B1904);
                uint8_t unk20 = rb(0x130B60);  // gGameSettings+0x20 (menu sub-state)
                uint8_t unk21 = rb(0x130B61);  // gGameSettings+0x21 (cinematic sub-state)
                uint8_t unk22 = rb(0x130B62);  // gGameSettings+0x22 (mission sub-state)

                static uint8_t s_last_level = 0xFF, s_last_craft = 0xFF;
                static uint32_t s_last_cineState = 0xFFFFFFFF;
                static uint8_t s_last_cineStage = 0xFF;
                static uint32_t s_last_cutscene = 0xFFFFFFFF;
                static uint8_t s_last_u20 = 0xFF, s_last_u21 = 0xFF, s_last_u22 = 0xFF;
                bool changed = (curLevel != s_last_level) || (curCraft != s_last_craft) ||
                               (cineStatePtr != s_last_cineState) || (cineStage != s_last_cineStage) ||
                               (curCutsceneFile != s_last_cutscene) ||
                               (unk20 != s_last_u20) || (unk21 != s_last_u21) || (unk22 != s_last_u22);
                if (changed || (s_n & 511) == 0) {
                    fprintf(stderr,
                        "[gamestate vi=#%d] level=%u craft=%u u20=%u u21=%u u22=%u cineState=0x%08X cineStage=%u cutscene=0x%08X%s\n",
                        s_n, curLevel, curCraft, unk20, unk21, unk22,
                        cineStatePtr, cineStage, curCutsceneFile,
                        changed ? " [CHANGED]" : "");
                    // Dump first 32 bytes of cutscene struct (filename field). Helps confirm WHICH cutscene.
                    if (curCutsceneFile >= 0x80000000 && curCutsceneFile < rs64_ram_top) {
                        uint32_t off = curCutsceneFile - 0x80000000;
                        fprintf(stderr, "  cutscene-filename: \"");
                        for (int i = 0; i < 32 && (off + i) < (rs64_ram_top - 0x80000000u); i++) {
                            uint8_t b = app->core.RDRAM[(off + i) ^ 3];
                            if (b >= 0x20 && b < 0x7F) fputc(b, stderr);
                            else if (b == 0) break;
                            else fputc('?', stderr);
                        }
                        fprintf(stderr, "\"\n");
                    }
                    fflush(stderr);
                    s_last_level = curLevel;
                    s_last_craft = curCraft;
                    s_last_cineState = cineStatePtr;
                    s_last_cineStage = cineStage;
                    s_last_cutscene = curCutsceneFile;
                    s_last_u20 = unk20;
                    s_last_u21 = unk21;
                    s_last_u22 = unk22;
                }
            }
            // Log once when the SDL filter actually installs.
            if (!s_filter_logged && app->appWindow && app->appWindow->sdlEventFilterInstalled) {
                fprintf(stderr,
                    "[RT64] sdlEventFilter NOW installed at update_screen #%d (sdlWindow=%p)\n",
                    s_n, (void*)app->appWindow->sdlWindow);
                fflush(stderr);
                s_filter_logged = true;
            }
            // Phase marker. The game's phases are distinguishable by VI width
            // (512 = hangar, 1024 = the hi-res tiled phase before it), and
            // session 17 wasted several captures because run-to-run timing
            // varies by tens of seconds — the Factor 5 logo landed at 18s in
            // one run and 44s in another, so fixed capture windows kept
            // missing the phase they were aimed at. This fires the instant the
            // width changes, so a capture harness can gate on the phase itself
            // rather than on elapsed time.
            {
                static uint32_t s_last_width = 0xFFFFFFFF;
                ultramodern::renderer::ViRegs* pvi = ultramodern::renderer::get_vi_regs();
                const uint32_t w = pvi->VI_WIDTH_REG;
                const bool s_dw_switch = (w != s_last_width);  // s7820: ROGUESQ_DEBUG_WRITE default = fire on a switch only
                if (w != s_last_width) {
                    const double el = rs64_elapsed_seconds();
                    fprintf(stderr,
                        "[phase] vi_width=%u (was %u) origin=0x%08X at %.1fs update_screen #%d\n",
                        w, s_last_width == 0xFFFFFFFF ? 0u : s_last_width,
                        pvi->VI_ORIGIN_REG, el, s_n);
                    fflush(stderr);
                    s_last_width = w;
                    // Publish the phase change so RT64-side censuses can scope
                    // themselves to one phase (see rs64_phase_ord below).
                    rs64_m5_route_fingerprint_phase(w, pvi->VI_ORIGIN_REG);
                    rs64_bump_phase_ord();
                    rs64_m5_selector_ai_call_latch_join(
                        w, pvi->VI_ORIGIN_REG & 0x00FFFFFFu, rs64_phase_ord());
                    if (w == 640u && (pvi->VI_ORIGIN_REG & 0x00FFFFFFu) == 0x006A2900u) {
                        rs64_s4597_target_store('C', 0xFFFFFFFFu, 0x8017C000u, 0u);
                    }
                    if (w == 1024u && (pvi->VI_ORIGIN_REG & 0x00FFFFFFu) == 0x00790400u) {
                        rs64_m5_b40_route_title_transition();
                    }
                }
                // s6750: ROGUESQ_DEBUG_WRITE=VADDR:VALUE:WIDTH:ARM_S writes one aligned guest word on the
                // first switch to WIDTH at or after ARM_S seconds; mirrors rs64_oracle --debug-write so both arms can be put
                // in the same state (e.g. rngSeed 0x80003470 at the mission intro). s7820: a 5th field ":in"
                // (VADDR:VALUE:WIDTH:ARM_S:in) fires on the first update_screen showing WIDTH at or after ARM_S even with no
                // switch, so ARM_S can sit inside a phase (without it an ARM_S past the switch never fires).
                static const char* s_dw = std::getenv("ROGUESQ_DEBUG_WRITE");
                static bool s_dw_done = false;
                // s7845: ROGUESQ_RAND_TRACE_BOOT=1 (with ROGUESQ_RAND_TRACE, no DEBUG_WRITE) opens the rand trace at the
                // first update_screen with no poke, mirroring rs64_oracle --exec-trace "from boot if none", so the two
                // arms' unpoked rand streams (seed carried in from boot/menus) can be compared.
                static bool s_rt_boot_done = false;
                if (!s_rt_boot_done) {
                    s_rt_boot_done = true;
                    const char* rt = std::getenv("ROGUESQ_RAND_TRACE");
                    const char* rb = std::getenv("ROGUESQ_RAND_TRACE_BOOT");
                    if (rt && rb && *rb == '1' && !s_dw && !s_rand_trace_f) {
                        s_rand_trace_f = fopen(rt, "w");
                        g_rs64_rand_trace = s_rand_trace_f != nullptr;
                        fprintf(stderr, "[rand-trace] boot open=%d update_screen #%d max=%ld\n", (int)g_rs64_rand_trace, s_n,
                                rs64_rand_trace_max());
                    }
                }
                if (s_dw && !s_dw_done && app->core.RDRAM) {
                    const double el = rs64_elapsed_seconds();
                    unsigned a = 0, v = 0, dw_w = 320; double arm = 0.0; char mode[4] = {0};
                    const int nf = sscanf(s_dw, "%x:%x:%u:%lf:%3s", &a, &v, &dw_w, &arm, mode);
                    const bool in_phase = nf >= 5 && !strcmp(mode, "in");
                    if (nf >= 2 && (s_dw_switch || in_phase) && w == dw_w && el >= arm &&
                        a >= 0x80000000u && a + 4 <= rs64_ram_top && (a & 3) == 0) {
                        *reinterpret_cast<uint32_t*>(app->core.RDRAM + (a - 0x80000000u)) = v;
                        s_dw_done = true;
                        if (const char* rt = std::getenv("ROGUESQ_RAND_TRACE")) {
                            s_rand_trace_f = fopen(rt, "w");
                            g_rs64_rand_trace = s_rand_trace_f != nullptr;
                        }
                        fprintf(stderr, "[debug-write] update_screen #%d t=%.1f width=%u addr=0x%08X value=0x%08X\n",
                                s_n, el, w, a, v);
                    }
                }
                rs64_m5_route_fingerprint_snapshot(w, pvi->VI_ORIGIN_REG);
                // s4636: dump the VI colour image (512 wide, 16bpp, 260 rows)
                // every 8th update_screen while width==512, so the RDRAM edge
                // columns can be compared offline against the screenshot edge.
                static const char* s_edge_dir = std::getenv("ROGUESQ_EDGE_DUMP");
                static int s_edge_files = 0;
                // s4639: col-511 snapshot of both hangar buffers at each of the
                // first 24 512-wide VI updates (H-stale discriminator).
                static const char* s_bw = std::getenv("ROGUESQ_BUF_WATCH");
                static int s_snap_n = 0;
                if (s_bw && s_bw[0] != '0' && w == 512u && s_snap_n < 24 && app->core.RDRAM) {
                    s_snap_n++;
                    const uint8_t* rd = app->core.RDRAM;
                    uint32_t nz[2] = {0, 0}, nzb[2] = {0, 0};
                    static const uint32_t bases[2] = {0x656400u, 0x6AB400u};
                    for (int b = 0; b < 2; ++b)
                        for (uint32_t r = 0; r < 240; ++r) {
                            const uint32_t o = bases[b] + r * 1024u;
                            if (rd[(o + 1022u) ^ 3] | rd[(o + 1023u) ^ 3]) nz[b]++;
                            if (rd[(o + 1020u) ^ 3] | rd[(o + 1021u) ^ 3]) nzb[b]++;
                        }
                    fprintf(stderr,
                        "[s4639-snap] n=%d vi_n=%d org=%06X col511_nz 656400=%u 6AB400=%u col510_nz 656400=%u 6AB400=%u\n",
                        s_snap_n, (int)s_n, pvi->VI_ORIGIN_REG & 0x00FFFFFFu, nz[0], nz[1], nzb[0], nzb[1]);
                }
                if (s_edge_dir && w == 512u && (s_n & 7) == 0 && s_edge_files < 400) {
                    const uint8_t* rd = app->core.RDRAM;
                    const uint32_t org = pvi->VI_ORIGIN_REG & 0x00FFFFFFu;
                    char path[512];
                    snprintf(path, sizeof(path), "%s/edge_%05d_%08X.bin", s_edge_dir, s_n, org);
                    if (FILE* f = fopen(path, "wb")) {
                        std::vector<uint8_t> buf(512u * 2u * 260u);
                        for (uint32_t i = 0; i < buf.size(); i++) {
                            uint32_t off = org + i;
                            buf[i] = (off < (rs64_ram_top - 0x80000000u)) ? rd[off ^ 3] : 0;
                        }
                        fwrite(buf.data(), 1, buf.size(), f);
                        fclose(f);
                        s_edge_files++;
                    }
                }
            }

            {   // s6070 g1c: per-VI frame summary (ROGUESQ_G1CF=1), unbudgeted, tagged with the dd toggle state
                static int s_f = -1;
                if (s_f < 0) { const char *e = std::getenv("ROGUESQ_G1CF"); s_f = (e && *e && *e != '0') ? 1 : 0; }
                if (s_f) {
                    uint64_t t1 = g_rs64_rt64_tri_accepted.load(), r1 = g_rs64_rt64_rect_accepted.load();
                    fprintf(stderr, "[g1cf] vi=%d dd=%d tasks=%u dsize=%u subs=%u bytes=%u tri=%u rt64tri=%llu rt64rect=%llu maxlen=%u lastlen=%u tin=%u tout=%u tzero=%u vout=%u kpx=%.1f sc=%.0f,%.0f,%.0f,%.0f bin=%u,%u,%u,%u,%u,%u,%u,%u wr=%d wm=%d\n",
                            s_n, g_rs64_dd_blk, g_rs64_g1cf_tasks, g_rs64_g1cf_dsize, s_g1cf.subs, s_g1cf.bytes, s_g1cf.tri,
                            (unsigned long long)(t1 - s_g1cf.rt0), (unsigned long long)(r1 - s_g1cf.rr0), s_g1cf.maxlen, s_g1cf.lastlen,
                            s_g1cf.tin, s_g1cf.tout, s_g1cf.tzero, s_g1cf.vout, s_g1cf.area / 1000.0,
                            s_g1cf_sc[0], s_g1cf_sc[1], s_g1cf_sc[2], s_g1cf_sc[3],
                            s_g1cf.bin[0], s_g1cf.bin[1], s_g1cf.bin[2], s_g1cf.bin[3], s_g1cf.bin[4], s_g1cf.bin[5], s_g1cf.bin[6], s_g1cf.bin[7], g_rs64_s7233_wr, g_rs64_s7239_wm);
                    s_g1cf = G1cf(); s_g1cf.rt0 = t1; s_g1cf.rr0 = r1; g_rs64_g1cf_tasks = 0; g_rs64_g1cf_dsize = 0;
                }
            }
            if (s_n <= 4 || (s_n & 63) == 0) {
                ultramodern::renderer::ViRegs* vi = ultramodern::renderer::get_vi_regs();
                // Sample 16 bytes at VI_ORIGIN to see if there's actual pixel
                // data there. If all zeros, VI is sampling an empty buffer.
                uint32_t origin = vi->VI_ORIGIN_REG & 0x00FFFFFF;
                uint32_t any_nonzero = 0;
                if (app && app->core.RDRAM && origin > 0 && origin + 16 < (rs64_ram_top - 0x80000000u)) {
                    for (int i = 0; i < 16; i++) {
                        any_nonzero |= app->core.RDRAM[origin + i];
                    }
                }
                // Also log presentQueue + workloadQueue cursors so we can
                // see whether PresentEarly is pushing presents and the
                // workload worker is consuming them. If presents stay flat
                // while workloads advance, the matcher is failing.
                int pq_wc = app->presentQueue ? (int)app->presentQueue->writeCursor : -1;
                int wq_wc = app->workloadQueue ? (int)app->workloadQueue->writeCursor : -1;
                fprintf(stderr,
                    "[vi] update_screen #%d origin=0x%08X width=%u status=0x%X v_current=%u nonzero=%d fs=%u pq.wc=%d wq.wc=%d\n",
                    s_n, vi->VI_ORIGIN_REG, vi->VI_WIDTH_REG,
                    vi->VI_STATUS_REG, vi->VI_V_CURRENT_LINE_REG, any_nonzero != 0,
                    rs64_dpc_get_cumulative_fullsyncs(),
                    pq_wc, wq_wc);
                // Every 256 updates, also dump the cumulative opcode histogram.
                if ((s_n & 255) == 0) {
                    uint32_t hist[64];
                    rs64_dpc_get_cumulative_histogram(hist);
                    uint32_t total = 0;
                    for (int i = 0; i < 64; ++i) total += hist[i];
                    fprintf(stderr, "  [opcode-hist total=%u top:", total);
                    uint32_t copy[64];
                    for (int i = 0; i < 64; ++i) copy[i] = hist[i];
                    for (int slot = 0; slot < 6; ++slot) {
                        int max_idx = 0;
                        for (int i = 0; i < 64; ++i) {
                            if (copy[i] > copy[max_idx]) max_idx = i;
                        }
                        if (copy[max_idx] == 0) break;
                        fprintf(stderr, " op%02X=%u", max_idx, copy[max_idx]);
                        copy[max_idx] = 0;
                    }
                    fprintf(stderr, "]\n");
                }
                fflush(stderr);
            }
            const double t2 = rs64_scr_now();
            if (screen_job) ultramodern::rs64_rdpq_screen_job(); else app->updateScreen();
            ultramodern::rs64_scr_note(rs64_scr_t1 - rs64_scr_t0, t2 - rs64_scr_t1, rs64_scr_now() - t2);
        }
    }

    void shutdown() override {
        ultramodern::rs64_rdpq_drain(); // s6705
        if (app) {
            g_rt64_app.store(nullptr);
            app->end();
            app.reset();
        }
    }

    uint32_t get_display_framerate() const override {
        if (app && app->presentQueue) {
            return app->presentQueue->ext.sharedResources->swapChainRate;
        }
        return 60;
    }

    float get_resolution_scale() const override {
        return app ? float(app->userConfig.resolutionMultiplier) : 1.0f;
    }
};

std::unique_ptr<ultramodern::renderer::RendererContext>
create_render_context(uint8_t* rdram, ultramodern::renderer::WindowHandle window, bool developer_mode) {
    return std::make_unique<RT64Context>(rdram, window, developer_mode);
}

} // namespace recomp

// Free-function bridge for the LLE DPC pipeline (see src/rsp/dpc_bridge.cpp).
// Forwards raw RDP byte ranges from the recompiled Factor 5 ucode into the
// live RT64::Application for rasterization (isHLE=false).
namespace ultramodern {
    // Catch AVs from RT64's processDisplayLists. Currently
    // RT64::RDP::updateCallTexcoords (rt64_rdp.cpp:1343) reads
    // workload.drawData.callTiles[drawCall.tileIndex + t] before that
    // vector has been populated, when Factor 5's ucode emits a TEXRECT
    // without prior tile setup. The OOB returns garbage in release
    // builds (and our _ITERATOR_DEBUG_LEVEL=0 path) which then AVs on
    // the load. Catch the SEH exception here and skip the submission;
    // we lose that frame's content but the game continues running.
    // SEH-protected submission. RT64's processDisplayLists can AV in
    // RDP::updateCallTexcoords (rt64_rdp.cpp:1343) when Factor 5's ucode
    // emits a TEXRECT-like sequence without prior tile setup —
    // drawCall.tileCount > 0 but workload.drawData.callTiles is empty,
    // so the indexed read goes past end.
    //
    // After the AV, even if we reset dlCpuProfiler, downstream RT64 state
    // is corrupted in multiple places (next assert is at
    // rt64_framebuffer_manager.cpp:248). Rather than chase each, we
    // disable submission entirely after the first SEH. Game continues to
    // run, just without further graphics output. Better than crashing.
    // TODO: pre-validate at dpc_bridge to drop bad commands BEFORE submit.
    static std::atomic<bool> s_rdp_disabled{false};

    // s6705 G1e: ROGUESQ_RDP_ASYNC=1 moves RT64 processing of LLE RDP ranges onto one worker thread so the RSP keeps
    // running while RT64 interprets. The ucode reuses its RDP output ring within a task, so each range's command words are
    // COPIED at submit time and RT64 reads the copy (processDisplayLists takes the command base pointer; textures still come
    // from core.RDRAM, read later than in sync mode, like the real RDP). Contiguous submits are merged up to 4 KB. Ordering
    // is FIFO; send_dl (RAII guard) and update_screen drain the queue, so dp_complete and present still follow every
    // range of the task. Submits outside send_dl run synchronously. ROGUESQ_RDP_ASYNC_TOGGLE=<s> (events.cpp) flips it.
    namespace rdpq {
        struct Job { uint32_t lo = 0, hi = 0; std::vector<uint8_t> w; bool screen = false; uint64_t gb_seq = 0; int gb_mode = 0; }; // s7539 tags
        static std::mutex m;
        static std::condition_variable cv_job, cv_idle;
        static std::deque<Job> q;
        static std::vector<std::vector<uint8_t>> pool;
        static bool busy = false, started = false;
        static Job pend;               // producer-side merge buffer (Gfx thread only)
        static bool pend_has = false;
        static int in_task = 0;        // Gfx thread only
        static uint64_t n_jobs = 0, n_ranges = 0;
        static bool task_async = false; // a range of the current task went to the worker
        // s6706 G1e: per-task split of an async task (ROGUESQ_G1B=1 only): RSP phase (enter -> drain entry), drain wait,
        // worker busy before/after drain entry, producer copy cost, last job; sync tasks log RT64 time inline. One
        // [g1e-aq] line per wall second per arm (as = mode at task entry).
        static const bool aq_on = [] { const char *e = std::getenv("ROGUESQ_G1B"); return e && *e && *e != '0'; }();
        using aclk = std::chrono::steady_clock;
        static inline double aq_ms(aclk::time_point a, aclk::time_point b) { return std::chrono::duration<double, std::milli>(b - a).count(); }
        static std::atomic<uint64_t> wk_busy_ns{0};
        static std::atomic<uint32_t> wk_last_bytes{0}; static std::atomic<uint64_t> wk_last_ns{0}, wk_max_ns{0};
        static aclk::time_point aq_t0 = aclk::now(), task_t0;
        static int task_mode = 0;
        static double t_copy = 0, t_sync = 0; static uint64_t t_bytes = 0, t_jobs = 0, t_calls = 0;
        struct AqAcc { uint64_t n = 0; double rsp = 0, drain = 0, wk = 0, wk_tail = 0, copy = 0, sync = 0, bytes = 0, jobs = 0, calls = 0,
                       pend_jobs = 0, last_kb = 0, last_ms = 0, max_ms = 0, total = 0; };
        static AqAcc aq[5]; static int aq_sec = -1;
        // s6707 G1e: as=2 = async task whose deferred RDP ranges the bridge streams to the worker every ROGUESQ_RDP_STREAM_KB
        // (default 16, 0 = off) while the RSP runs, instead of one commit after it exits. ROGUESQ_RDP_STREAM_TOGGLE=1 streams
        // only every other async window (same-run as=1 vs as=2). Latched per task at entry.
        static const uint32_t stream_bytes = [] { const char *e = std::getenv("ROGUESQ_RDP_STREAM_KB"); return (e ? (uint32_t)strtoul(e, nullptr, 0) : 16u) * 1024u; }();
        static const bool stream_toggle = [] { const char *e = std::getenv("ROGUESQ_RDP_STREAM_TOGGLE"); return e && *e && *e != '0'; }();
        static int last_async = 0; static uint64_t async_windows = 0;
        static uint32_t task_stream = 0; // bytes per streamed flush for the current task, 0 = commit at task end
        // s6708 G1e: the drained tail is State::fullSync (~3.3 ms: fb-pair encode + GPU execute/wait), so ROGUESQ_RDP_NODRAIN=1
        // lets send_dl return (dp_complete) without waiting for it; the next task's RSP overlaps the tail and its ranges queue
        // FIFO behind it. update_screen/shutdown/sync submits still drain. =2 alternates per async window (same-run A/B:
        // as=2 drained vs as=3 not drained). Latched per task at entry.
        static const int nodrain_env = [] { const char *e = std::getenv("ROGUESQ_RDP_NODRAIN"); return e ? atoi(e) : 0; }();
        static bool task_nodrain = false;
        // s7540 class GB fix: ROGUESQ_RDP_NODRAIN=3 = "reads-wait": send_dl returns once the worker has done the RDRAM texture
        // reads of the task (RT64 State::fullSync calls rs64_s7540_reads_done() after its last fullSyncFramebufferPairTiles),
        // not after the whole tail (renderAndSynchronize GPU work). =2 now alternates per TASK drain/nodrain (s7539: it counted
        // async windows, which never flipped, so =2 == =1). =4 cycles per task full drain / nodrain / reads-wait (same-run A/B/C:
        // aq as=1|2 / as=3 / as=4, s7539-gb as=1 / as=3 / as=4).
        static bool task_rwait = false;
        static bool cur_rd = false;                    // under m: the job the worker is running signalled reads-done
        static uint64_t rw_sig = 0, rw_idle = 0;       // Gfx thread: reads-wait ended by the signal / by an idle worker
        static const bool screen_job_env = [] { const char *e = std::getenv("ROGUESQ_RDP_SCREEN_JOB"); return e && *e && *e != '0'; }();
        static std::atomic<int> screen_pend{0}; // at 2 queued the next VI takes the drain path, so the worker cannot run away
        static double scr_drain = 0, scr_pre = 0, scr_up = 0, scr_upmax = 0; static uint64_t scr_n = 0; // Gfx thread only
        static void aq_print(int sec) {
            if (rw_sig + rw_idle) std::fprintf(stderr, "[s7540-rw] t=%d sig=%llu idle=%llu\n", sec, (unsigned long long)rw_sig, (unsigned long long)rw_idle);
            rw_sig = rw_idle = 0;
            if (scr_n) std::fprintf(stderr, "[g1e-scr] t=%d n=%llu drain=%.2f pre=%.3f up=%.2f up_max=%.2f\n", sec, (unsigned long long)scr_n,
                                    scr_drain / scr_n, scr_pre / scr_n, scr_up / scr_n, scr_upmax);
            scr_drain = scr_pre = scr_up = scr_upmax = 0; scr_n = 0;
            for (int a = 0; a < 5; ++a) {
                AqAcc &x = aq[a]; if (!x.n) continue; const double n = (double)x.n;
                std::fprintf(stderr, "[g1e-aq] t=%d as=%d n=%llu total=%.2f rsp=%.2f drain=%.2f wk=%.2f wk_tail=%.2f copy=%.3f sync_rt64=%.2f "
                    "kB=%.1f jobs=%.1f calls=%.1f pend_jobs=%.2f last_kB=%.2f last_ms=%.2f max_job_ms=%.2f\n", sec, a, (unsigned long long)x.n,
                    x.total / n, x.rsp / n, x.drain / n, x.wk / n, x.wk_tail / n, x.copy / n, x.sync / n, x.bytes / n / 1024.0, x.jobs / n,
                    x.calls / n, x.pend_jobs / n, x.last_kb / n, x.last_ms / n, x.max_ms / n);
                x = AqAcc{};
            }
        }
        // s7539 class GB: ROGUESQ_S7539_GB_CHK=1. At task exit (just before send_dl returns and dp_complete is posted) the Gfx
        // thread snapshots guest RAM [0,16 MB) into one of two ping-pong buffers (async no-drain tasks only; drained tasks only
        // advance gb_posted). Every non-deferred RT64 texture load (fullSync -> load{Tile,Block,TLUT}Operation, rt64_rdp.cpp)
        // on the worker whose job's task is already posted compares its RDRAM source rows against that task's snapshot.
        // Controls: real-world (the same rows vs the OLDER snapshot, an earlier task's exit: frame-to-frame texture changes),
        // planted (every 64th compared load re-run against a copy with one byte flipped; caught == planted), activity witness
        // (every 32nd snapshot, bytes of [0,16 MB) changed between the post and the end of that task's last worker job).
        namespace gb {
            static const bool on = [] { const char *e = std::getenv("ROGUESQ_S7539_GB_CHK"); return e && *e && *e != '0'; }();
            static constexpr uint32_t SZ = 16u << 20;
            static uint8_t *snap[2] = {nullptr, nullptr}; static uint64_t snap_seq[2] = {0, 0}; static int cur = -1; static uint64_t n_snap = 0;
            static uint64_t snap_no[2] = {0, 0};
            static std::mutex sm;
            static uint64_t task_seq = 0;                    // Gfx thread
            static std::atomic<uint64_t> posted{0};          // highest task seq whose exit (post) happened
            static thread_local uint64_t wk_seq = 0; static thread_local int wk_mode = -1;
            struct C { uint64_t loads = 0, pre = 0, post = 0, post_nosnap = 0, bytes = 0, dl = 0, db = 0, prev = 0, prev_dl = 0, prev_db = 0,
                       planted = 0, caught = 0, wit_n = 0, wit_bytes = 0, wit_max = 0; };
            static C c[5]; static uint64_t hist[256]; static uint64_t prev_hist[256]; // diff bytes per 64 KB bucket (as=3)
            static std::mutex cm;
            static uint64_t rows_cmp(const uint8_t *a, const uint8_t *b, uint32_t start, uint32_t stride, uint32_t rowBytes, uint32_t rows, uint64_t *h) {
                uint64_t d = 0;
                for (uint32_t r = 0; r < rows; ++r) {
                    uint32_t s0 = (start + r * stride) & 0xFFFFFFu, e0 = s0 + rowBytes; s0 &= ~3u; e0 = (e0 + 3u) & ~3u; if (e0 > SZ) e0 = SZ;
                    for (uint32_t i = s0; i < e0; ++i) if (a[i] != b[i]) { ++d; if (h) ++h[i >> 16]; }
                }
                return d;
            }
            static void print_locked(const char *why) {
                for (int m = 0; m < 5; ++m) { const C &x = c[m]; if (!x.loads) continue;
                    std::fprintf(stderr, "[s7539-gb] %s as=%d loads=%llu pre=%llu post=%llu post_nosnap=%llu cmp_bytes=%llu diff_loads=%llu diff_bytes=%llu "
                        "prev_cmp=%llu prev_diff_loads=%llu prev_diff_bytes=%llu ctl_planted=%llu ctl_caught=%llu wit_n=%llu wit_bytes=%llu wit_max=%llu snaps=%llu\n",
                        why, m, (unsigned long long)x.loads, (unsigned long long)x.pre, (unsigned long long)x.post, (unsigned long long)x.post_nosnap,
                        (unsigned long long)x.bytes, (unsigned long long)x.dl, (unsigned long long)x.db, (unsigned long long)x.prev, (unsigned long long)x.prev_dl,
                        (unsigned long long)x.prev_db, (unsigned long long)x.planted, (unsigned long long)x.caught, (unsigned long long)x.wit_n,
                        (unsigned long long)x.wit_bytes, (unsigned long long)x.wit_max, (unsigned long long)n_snap); }
                std::string hs, ps; for (int b = 0; b < 256; ++b) { if (hist[b]) hs += " " + std::to_string(b) + ":" + std::to_string(hist[b]); if (prev_hist[b]) ps += " " + std::to_string(b) + ":" + std::to_string(prev_hist[b]); }
                std::fprintf(stderr, "[s7539-gbh] %s diff64k=%s | prev64k=%s\n", why, hs.empty() ? " none" : hs.c_str(), ps.empty() ? " none" : ps.c_str());
            }
            // s7541 class GB residual: RT64 guest-RAM accesses after reads_done (final renderAndSynchronize fb read-ins, copyNativeToRAM
            // writebacks, hashTracking). kind 0 colour read-in, 1 depth read-in, 2 writeback pre (bytes the guest changed after the post that
            // the writeback overwrites = clobber), 3 writeback post (bytes now differing from the guest's view at the post = late-visible
            // RDP output; the span is then written through into the snapshot so kind 4 sees only guest changes), 4 hashTracking (guest
            // change inside a tracked fb hashed after the post = a change RT64 will not notice). ar = access after this job's reads_done.
            // ROGUESQ_S7541_HOLD=1: a reads-wait (as=4) job holds after reads_done until its task is posted (<=50 ms), so every
            // post-reads_done access really happens after the post (the 16 MB snapshot copy would otherwise delay the post past them).
            static const bool hold = [] { const char *e = std::getenv("ROGUESQ_S7541_HOLD"); return e && *e && *e != '0'; }();
            static thread_local bool wk_rd = false;
            struct C2 { uint64_t n = 0, ar = 0, pre = 0, post = 0, nosnap = 0, bytes = 0, dn = 0, db = 0, prev = 0, prev_dn = 0, prev_db = 0, planted = 0, caught = 0; };
            static C2 c2[5][5]; static uint64_t hold_n = 0, hold_to = 0; static double hold_ms = 0;
            static void print2_locked(const char *why) {
                for (int m = 0; m < 5; ++m) for (int k = 0; k < 5; ++k) { const C2 &x = c2[m][k]; if (!x.n) continue;
                    std::fprintf(stderr, "[s7541-gb] %s as=%d kind=%d n=%llu ar=%llu pre=%llu post=%llu nosnap=%llu bytes=%llu diff_n=%llu diff_bytes=%llu "
                        "prev_n=%llu prev_diff_n=%llu prev_diff_bytes=%llu ctl_planted=%llu ctl_caught=%llu\n", why, m, k, (unsigned long long)x.n,
                        (unsigned long long)x.ar, (unsigned long long)x.pre, (unsigned long long)x.post, (unsigned long long)x.nosnap, (unsigned long long)x.bytes,
                        (unsigned long long)x.dn, (unsigned long long)x.db, (unsigned long long)x.prev, (unsigned long long)x.prev_dn, (unsigned long long)x.prev_db,
                        (unsigned long long)x.planted, (unsigned long long)x.caught); }
                std::fprintf(stderr, "[s7541-hold] %s on=%d n=%llu timeouts=%llu ms=%.3f\n", why, (int)hold, (unsigned long long)hold_n, (unsigned long long)hold_to, hold_ms);
            }
            // Gfx thread, outer task exit, after flush_pend()/drain().
            static void at_exit(const uint8_t *rdram, bool nd_async) {
                if (nd_async && rdram) {
                    std::lock_guard<std::mutex> lk(sm);
                    if (!snap[0]) { snap[0] = (uint8_t *)std::malloc(SZ); snap[1] = (uint8_t *)std::malloc(SZ); }
                    const int i = cur < 0 ? 0 : (cur ^ 1);
                    std::memcpy(snap[i], rdram, SZ); snap_seq[i] = task_seq; snap_no[i] = ++n_snap; cur = i;
                }
                posted.store(task_seq, std::memory_order_release);
                static uint64_t np = 0; if ((++np % 600) == 0) { std::lock_guard<std::mutex> lk(cm); char t[32]; std::snprintf(t, sizeof t, "p%llu", (unsigned long long)np); print_locked(t); print2_locked(t); }
            }
            // Worker thread: end of a job; witness on the last job of a snapshotted task.
            static void job_end(const uint8_t *rdram, uint64_t seq, bool last_of_task) {
                if (!last_of_task || !rdram) return;
                std::lock_guard<std::mutex> lk(sm);
                for (int b = 0; b < 2; ++b) if (snap[b] && snap_seq[b] == seq && (snap_no[b] % 32) == 0) {
                    uint64_t d = 0; const uint32_t *x = (const uint32_t *)snap[b], *y = (const uint32_t *)rdram;
                    for (uint32_t k = 0; k < SZ / 4; ++k) d += (x[k] != y[k]);
                    std::lock_guard<std::mutex> lc(cm); C &cc = c[3]; ++cc.wit_n; cc.wit_bytes += d * 4; if (d * 4 > cc.wit_max) cc.wit_max = d * 4;
                }
            }
            static void dump_exit() { if (!on) return; std::lock_guard<std::mutex> lk(cm); print_locked("exit"); print2_locked("exit"); }
        }
        static void worker() {
            pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
            pthread_setname_np("RS64 RDP async");
            for (;;) {
                Job j;
                {
                    std::unique_lock<std::mutex> lk(m);
                    cv_job.wait(lk, [] { return !q.empty(); });
                    j = std::move(q.front()); q.pop_front(); busy = true; cur_rd = false;
                }
                RT64::Application *app = g_rt64_app.load();
                const aclk::time_point jt0 = aq_on ? aclk::now() : aclk::time_point{};
                if (j.screen) { // s6884: the events the drain would have cleared belong to this thread now
                    RT64::g_s4280_n = 0;
                    if (app) app->updateScreen();
                    screen_pend.fetch_sub(1);
                }
                else if (app && !s_rdp_disabled.load(std::memory_order_relaxed)) {
                    gb::wk_seq = j.gb_seq; gb::wk_mode = j.gb_mode; gb::wk_rd = false; // s7539, s7541
                    app->processDisplayLists(j.w.data() - j.lo, j.lo, j.hi, /*isHLE*/ false);
                    gb::wk_mode = -1;
                    if (gb::on) { bool last; { std::lock_guard<std::mutex> lk(m); last = q.empty() || q.front().gb_seq != j.gb_seq; } gb::job_end(app->core.RDRAM, j.gb_seq, last); }
                }
                if (aq_on) {
                    const uint64_t ns = (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(aclk::now() - jt0).count();
                    wk_busy_ns += ns; wk_last_ns = ns; wk_last_bytes = (uint32_t)j.w.size();
                    if (ns > wk_max_ns.load()) wk_max_ns = ns;
                }
                {
                    std::lock_guard<std::mutex> lk(m);
                    j.w.clear(); pool.push_back(std::move(j.w)); busy = false;
                    if (q.empty()) cv_idle.notify_all();
                }
            }
        }
        static void flush_pend() {
            if (!pend_has) return;
            pend_has = false;
            if (aq_on) { t_bytes += pend.w.size(); ++t_jobs; }
            pend.gb_seq = gb::task_seq; pend.gb_mode = task_nodrain ? (task_rwait ? 4 : 3) : (task_stream ? 2 : 1); // s7539 (task_stream/nodrain latched at entry)
            std::lock_guard<std::mutex> lk(m);
            if (!started) { started = true; std::thread(worker).detach(); }
            q.push_back(std::move(pend)); ++n_jobs;
            pend = Job{};
            if (!pool.empty()) { pend.w = std::move(pool.back()); pool.pop_back(); }
            cv_job.notify_one();
        }
        static void drain() {
            flush_pend();
            if (!started) return;
            std::unique_lock<std::mutex> lk(m);
            cv_idle.wait(lk, [] { return q.empty() && !busy; });
        }
        // s7540: all jobs popped and the running one has done its fullSync texture reads (or the worker is idle).
        static void reads_wait() {
            flush_pend();
            if (!started) return;
            std::unique_lock<std::mutex> lk(m);
            cv_idle.wait(lk, [] { return q.empty() && (!busy || cur_rd); });
            if (busy) ++rw_sig; else ++rw_idle;
        }
        // true = queued; false = caller must process synchronously.
        static bool submit(RT64::Application *app, uint32_t lo, uint32_t hi) {
            if (!rs64_rdp_async_on || !in_task || !app->core.RDRAM) { drain(); return false; }
            const aclk::time_point ct0 = aq_on ? aclk::now() : aclk::time_point{};
            if (pend_has && (lo != pend.hi || pend.w.size() >= 4096)) flush_pend();
            if (!pend_has) { pend.lo = lo; pend.hi = lo; pend.w.clear(); pend_has = true; }
            const uint8_t *src = app->core.RDRAM + lo;
            pend.w.insert(pend.w.end(), src, src + (hi - lo));
            pend.hi = hi; ++n_ranges; task_async = true;
            if (aq_on) { t_copy += aq_ms(ct0, aclk::now()); ++t_calls; }
            return true;
        }
    }
    bool rs64_rdpq_screen_ready() {
        using namespace rdpq;
        return screen_job_env && rs64_rdp_async_on && in_task == 0 && task_nodrain && task_async && screen_pend.load() < 2;
    }
    void rs64_rdpq_screen_job() {
        using namespace rdpq;
        flush_pend(); task_async = false; screen_pend.fetch_add(1);
        Job j; j.screen = true;
        std::lock_guard<std::mutex> lk(m);
        q.push_back(std::move(j)); ++n_jobs; cv_job.notify_one();
    }
    void rs64_scr_note(double drain_ms, double pre_ms, double up_ms) {
        using namespace rdpq; if (!aq_on) return;
        scr_drain += drain_ms; scr_pre += pre_ms; scr_up += up_ms; if (up_ms > scr_upmax) scr_upmax = up_ms; ++scr_n;
    }
    void rs64_rdpq_drain() {
        rdpq::drain();
        if (rdpq::in_task == 0 && rdpq::task_async) { rdpq::task_async = false; RT64::g_s4280_n = 0; } // s6708 no-drain tasks
    }
    void rs64_rdpq_task_enter() {
        using namespace rdpq;
        if (in_task == 0) {
            ++gb::task_seq; // s7539
            if (rs64_rdp_async_on && !last_async) ++async_windows;
            last_async = rs64_rdp_async_on;
            task_stream = (rs64_rdp_async_on && stream_bytes && (!stream_toggle || (async_windows & 1) == 0)) ? stream_bytes : 0;
            const uint64_t ts = gb::task_seq;
            task_nodrain = rs64_rdp_async_on && (nodrain_env == 1 || nodrain_env == 3 || (nodrain_env == 2 && (ts & 1) == 1) || (nodrain_env == 4 && ts % 3 != 0));
            task_rwait = task_nodrain && (nodrain_env == 3 || (nodrain_env == 4 && ts % 3 == 2));
        }
        if (in_task++ == 0 && aq_on) {
            task_t0 = aclk::now(); task_mode = rs64_rdp_async_on ? (task_nodrain ? (task_rwait ? 4 : 3) : task_stream ? 2 : 1) : 0; t_copy = t_sync = 0; t_bytes = t_jobs = t_calls = 0;
            wk_busy_ns = 0; wk_max_ns = 0; wk_last_ns = 0; wk_last_bytes = 0;
        }
    }
    // The bridge's s4280 cimg walk (rs64_dpc_defer_end) maps RT64's SetColorImage events back to RDRAM by pointer offset,
    // meaningless for a copied range; it skips async tasks and the events they left are cleared here once drained.
    void rs64_rdpq_task_exit() {
        using namespace rdpq;
        if (--in_task == 0 && aq_on) {
            const aclk::time_point d0 = aclk::now();
            double pj = 0; uint64_t wk0;
            { std::lock_guard<std::mutex> lk(m); pj = (double)q.size() + (busy ? 1 : 0) + (pend_has ? 1 : 0); wk0 = wk_busy_ns.load(); }
            if (task_rwait) reads_wait(); else if (task_nodrain) flush_pend(); else drain();
            const aclk::time_point d1 = aclk::now();
            AqAcc &x = aq[task_mode]; ++x.n;
            x.rsp += aq_ms(task_t0, d0); x.drain += aq_ms(d0, d1); x.total += aq_ms(task_t0, d1);
            const uint64_t wk1 = wk_busy_ns.load();
            x.wk += wk1 / 1e6; x.wk_tail += (wk1 - wk0) / 1e6; x.copy += t_copy; x.sync += t_sync;
            x.bytes += t_bytes; x.jobs += t_jobs; x.calls += t_calls; x.pend_jobs += pj;
            x.last_kb += wk_last_bytes / 1024.0; x.last_ms += wk_last_ns / 1e6; x.max_ms += wk_max_ns / 1e6;
            const int sec = (int)(aq_ms(aq_t0, d1) / 1000.0);
            if (aq_sec < 0) aq_sec = sec;
            if (sec != aq_sec) { aq_print(aq_sec); aq_sec = sec; }
        }
        if (in_task == 0 && task_nodrain) { if (task_rwait) reads_wait(); else flush_pend(); if (gb::on) { RT64::Application *a = g_rt64_app.load(); gb::at_exit(a ? a->core.RDRAM : nullptr, task_async); } return; } // s6708: task_async stays set until a real drain
        rdpq::drain(); if (rdpq::task_async) { rdpq::task_async = false; RT64::g_s4280_n = 0; }
        if (gb::on && in_task == 0) gb::at_exit(nullptr, false); } // s7539: drained task posts with no worker job left
}
// s7539 class GB: called by RT64 (rt64_rdp.cpp load{Tile,Block,TLUT}Operation, non-deferred = the real RDRAM read in fullSync).
extern "C" int rs64_s7539_on = [] { const char *e = std::getenv("ROGUESQ_S7539_GB_CHK"); return (e && *e && *e != '0') ? 1 : 0; }();
extern "C" void rs64_s7539_load(const uint8_t *rdram, uint32_t start, uint32_t stride, uint32_t rowBytes, uint32_t rows) {
    using namespace ultramodern::rdpq;
    if (!rdram || !rows || !rowBytes) return;
    const int m = gb::wk_mode < 0 ? 0 : gb::wk_mode;
    std::lock_guard<std::mutex> lc(gb::cm);
    gb::C &x = gb::c[m]; ++x.loads;
    if (gb::wk_mode < 0 || gb::wk_seq > gb::posted.load(std::memory_order_acquire)) { ++x.pre; return; }
    ++x.post;
    std::lock_guard<std::mutex> ls(gb::sm);
    int b = -1; for (int k = 0; k < 2; ++k) if (gb::snap[k] && gb::snap_seq[k] == gb::wk_seq) b = k;
    if (b < 0) { ++x.post_nosnap; return; }
    const uint64_t d = gb::rows_cmp(gb::snap[b], rdram, start, stride, rowBytes, rows, m == 3 ? gb::hist : nullptr);
    x.bytes += (uint64_t)rowBytes * rows; if (d) { ++x.dl; x.db += d; }
    if (d && m == 3) { // s7539b: name the bytes: first differing word (old snapshot value -> value the worker reads), lag in tasks
        static int ne = 0;
        if (ne++ < 60) for (uint32_t r = 0; r < rows; ++r) {
            uint32_t s0 = ((start + r * stride) & 0xFFFFFFu) & ~3u, e0 = ((((start + r * stride) & 0xFFFFFFu) + rowBytes + 3u) & ~3u); if (e0 > gb::SZ) e0 = gb::SZ;
            uint32_t f = 0xFFFFFFFFu, nw = 0; for (uint32_t i = s0; i < e0; i += 4) if (std::memcmp(gb::snap[b] + i, rdram + i, 4)) { if (f == 0xFFFFFFFFu) f = i; ++nw; }
            if (f == 0xFFFFFFFFu) continue;
            uint32_t ov, nv; std::memcpy(&ov, gb::snap[b] + f, 4); std::memcpy(&nv, rdram + f, 4);
            std::fprintf(stderr, "[s7539-gbd] seq=%llu lag=%llu load=0x%06X stride=%u rowB=%u rows=%u row=%u first=0x%06X words=%u old=%08X new=%08X diff=%llu\n",
                (unsigned long long)gb::wk_seq, (unsigned long long)(gb::posted.load() - gb::wk_seq), start & 0xFFFFFFu, stride, rowBytes, rows, r, f, nw, ov, nv, (unsigned long long)d);
            break;
        }
    }
    const int o = b ^ 1;
    if (gb::snap[o] && gb::snap_seq[o] < gb::wk_seq) {
        const uint64_t pd = gb::rows_cmp(gb::snap[o], rdram, start, stride, rowBytes, rows, m == 3 ? gb::prev_hist : nullptr);
        ++x.prev; if (pd) { ++x.prev_dl; x.prev_db += pd; }
    }
    if ((x.post % 64) == 0) { // planted control: flip one source byte in the snapshot, the comparator must see exactly that change
        const uint32_t a = (start + (uint32_t)(x.post / 64 % rows) * stride) & 0xFFFFFFu;
        if (a < gb::SZ) { ++x.planted; gb::snap[b][a] ^= 0x5A;
            const uint64_t d2 = gb::rows_cmp(gb::snap[b], rdram, start, stride, rowBytes, rows, nullptr);
            gb::snap[b][a] ^= 0x5A; if (d2 != d) ++x.caught; }
    }
}
// s7540: RT64 State::fullSync, after the last fullSyncFramebufferPairTiles (no more texture-source RDRAM reads in this job).
extern "C" void rs64_s7540_reads_done() {
    using namespace ultramodern::rdpq;
    if (gb::wk_mode < 0) return; // Gfx-thread (synchronous) fullSync
    { std::lock_guard<std::mutex> lk(m); cur_rd = true; cv_idle.notify_all(); }
    gb::wk_rd = true; // s7541
    if (gb::on && gb::hold && gb::wk_mode == 4) {
        const aclk::time_point h0 = aclk::now(); bool to = false;
        while (gb::posted.load(std::memory_order_acquire) < gb::wk_seq) { if (aq_ms(h0, aclk::now()) > 50.0) { to = true; break; } std::this_thread::yield(); }
        std::lock_guard<std::mutex> lc(gb::cm); ++gb::hold_n; gb::hold_to += to; gb::hold_ms += aq_ms(h0, aclk::now());
    }
}
// s7541: RT64 post-reads_done guest-RAM spans (see gb::C2). Worker thread inside fullSync; Gfx-thread (sync) calls count as pre.
extern "C" void rs64_s7541_span(int kind, const uint8_t *rdram, uint32_t addr, uint32_t bytes) {
    using namespace ultramodern::rdpq;
    if (!gb::on || !rdram || !bytes || kind < 0 || kind > 4) return;
    const int m = gb::wk_mode < 0 ? 0 : gb::wk_mode;
    addr &= 0xFFFFFFu; if ((uint64_t)addr + bytes > gb::SZ) bytes = gb::SZ - addr;
    std::lock_guard<std::mutex> lc(gb::cm);
    gb::C2 &x = gb::c2[m][kind]; ++x.n; if (gb::wk_mode >= 0 && gb::wk_rd) ++x.ar;
    if (gb::wk_mode < 0 || gb::wk_seq > gb::posted.load(std::memory_order_acquire)) { ++x.pre; return; }
    ++x.post;
    std::lock_guard<std::mutex> ls(gb::sm);
    int b = -1; for (int k = 0; k < 2; ++k) if (gb::snap[k] && gb::snap_seq[k] == gb::wk_seq) b = k;
    if (b < 0) { ++x.nosnap; return; }
    const uint64_t d = gb::rows_cmp(gb::snap[b], rdram, addr, 0, bytes, 1, nullptr);
    x.bytes += bytes; if (d) { ++x.dn; x.db += d; }
    if (d && (m == 3 || m == 4)) { static int ne = 0;
        if (ne++ < 80) { uint32_t f = 0xFFFFFFFFu; for (uint32_t i = addr & ~3u; i < addr + bytes; i += 4) if (std::memcmp(gb::snap[b] + i, rdram + i, 4)) { f = i; break; }
            uint32_t ov = 0, nv = 0; if (f != 0xFFFFFFFFu) { std::memcpy(&ov, gb::snap[b] + f, 4); std::memcpy(&nv, rdram + f, 4); }
            std::fprintf(stderr, "[s7541-gbd] as=%d kind=%d seq=%llu lag=%llu addr=0x%06X bytes=%u diff=%llu first=0x%06X old=%08X new=%08X\n", m, kind,
                (unsigned long long)gb::wk_seq, (unsigned long long)(gb::posted.load() - gb::wk_seq), addr, bytes, (unsigned long long)d, f, ov, nv); } }
    const int o = b ^ 1;
    if (gb::snap[o] && gb::snap_seq[o] < gb::wk_seq) { const uint64_t pd = gb::rows_cmp(gb::snap[o], rdram, addr, 0, bytes, 1, nullptr); ++x.prev; if (pd) { ++x.prev_dn; x.prev_db += pd; } }
    if ((x.post % 16) == 1) { // planted control: one flipped snapshot byte must change the comparator's count by exactly one
        const uint32_t a = addr + (uint32_t)((x.post / 16) % bytes);
        const int bf = gb::snap[b][a] != rdram[a], af = (uint8_t)(gb::snap[b][a] ^ 0x5A) != rdram[a];
        if (bf != af) { ++x.planted; gb::snap[b][a] ^= 0x5A; const uint64_t d2 = gb::rows_cmp(gb::snap[b], rdram, addr, 0, bytes, 1, nullptr); gb::snap[b][a] ^= 0x5A;
            if (d2 == d - bf + af) ++x.caught; } }
    if (kind == 3) std::memcpy(gb::snap[b] + addr, rdram + addr, bytes); // RT64's own output is not a guest change for kind 4
}
extern "C" int rs64_rdpq_task_async() { return ultramodern::rdpq::task_async ? 1 : 0; }
extern "C" uint32_t rs64_rdpq_task_stream() { return ultramodern::rdpq::in_task ? ultramodern::rdpq::task_stream : 0; }
namespace ultramodern {

    static void run_rdp_submission(RT64::Application* app, uint32_t lo_phys, uint32_t hi_phys) {
        if (s_rdp_disabled.load(std::memory_order_relaxed)) {
            return;
        }
        static const bool log_e9_consumer = [] {
            const char *e = std::getenv("ROGUESQ_LOG_E9_UNIFIED");
            const char *advance = std::getenv("ROGUESQ_LOG_RDP_ADVANCE");
            const char *all = std::getenv("ROGUESQ_LOG_ALL");
            return (e && *e && *e != '0') || (advance && *advance && *advance != '0') ||
                   (all && *all && *all != '0');
        }();
        if (log_e9_consumer) {
            const uint32_t task = rs64_e9prov_current_task();
            const uint32_t scope = rs64_e9prov_current_scope();
            uint64_t synthetic = 0;
            const bool is_synthetic = rs64_dpc_take_synthetic_consumer(&synthetic);
            if (scope != 0) {
                if (is_synthetic) {
                    fprintf(stderr,
                            "[e9-synthetic-consumer] synthetic=%llu task=%u scope=%s "
                            "serial=%llu lo=0x%06X hi=0x%06X\n",
                            (unsigned long long)synthetic, task,
                            scope == 1 ? "control" : "sec2",
                            (unsigned long long)rs64_dpc_get_last_submit_serial(),
                            lo_phys, hi_phys);
                } else {
                    fprintf(stderr,
                            "[e9-ordinary-consumer] serial=%llu task=%u scope=%s lo=0x%06X hi=0x%06X\n",
                            (unsigned long long)rs64_dpc_get_last_submit_serial(), task,
                            scope == 1 ? "control" : "sec2", lo_phys, hi_phys);
                }
                fflush(stderr);
            }
        }
#ifdef _WIN32
        __try {
            app->processDisplayLists(app->core.RDRAM, lo_phys, hi_phys, /*isHLE*/ false);
        }
        __except (EXCEPTION_EXECUTE_HANDLER) {
            // Reset the profiler timer too in case anything still tries to
            // touch it (the disable flag should prevent that, but be safe).
            if (app->state) {
                app->state->dlCpuProfiler.startedTimestamp = RT64::Timestamp{};
            }
            s_rdp_disabled.store(true, std::memory_order_relaxed);
            fprintf(stderr, "[rdp-submit] SEH in processDisplayLists "
                            "lo=0x%08X hi=0x%08X — RDP submission DISABLED for the rest "
                            "of this session (RT64 state corrupted by AV).\n",
                            lo_phys, hi_phys);
            // Dump cumulative opcode histogram so we can see what kinds of
            // commands the game submitted before the crash. Tells us
            // whether actual rendering work (TEXRECT, FILLRECT, triangles)
            // was happening.
            uint32_t hist[64];
            rs64_dpc_get_cumulative_histogram(hist);
            uint32_t total = 0;
            for (int i = 0; i < 64; ++i) total += hist[i];
            fprintf(stderr, "[rdp-submit] cumulative opcode histogram (total=%u):\n", total);
            // Print top 12 by count
            uint32_t copy[64];
            for (int i = 0; i < 64; ++i) copy[i] = hist[i];
            for (int slot = 0; slot < 12; ++slot) {
                int max_idx = 0;
                for (int i = 0; i < 64; ++i) {
                    if (copy[i] > copy[max_idx]) max_idx = i;
                }
                if (copy[max_idx] == 0) break;
                fprintf(stderr, "  op 0x%02X = %u\n", max_idx, copy[max_idx]);
                copy[max_idx] = 0;
            }
            fflush(stderr);
        }
#else
        if (rdpq::submit(app, lo_phys, hi_phys)) return; // s6705: queued for the async consumer
        const auto st0 = (rdpq::aq_on && rdpq::in_task) ? rdpq::aclk::now() : rdpq::aclk::time_point{}; // s6706
        { // s7385 ROGUESQ_RENDER_TO_RAM_TOG=<secs>: diagnostic in-run A/B, renderToRAM on in even blocks, off in odd
          // blocks (Gfx thread, before the DL parse that reaches fullSync, so one fullSync sees one value).
            static const int tog = [] { const char *e = std::getenv("ROGUESQ_RENDER_TO_RAM_TOG"); return e ? std::atoi(e) : 0; }();
            if (tog > 0) {
                static const auto t0 = std::chrono::steady_clock::now();
                const long blk = (long)(std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - t0).count() / tog);
                const bool want = (blk % 2) == 0;
                if (app->emulatorConfig.framebuffer.renderToRAM != want) {
                    app->emulatorConfig.framebuffer.renderToRAM = want;
                    s4267::s7385_r2r.store(want ? 1 : 0); s4267::s7385_ntog.fetch_add(1);
                    fprintf(stderr, "[s7385-tog] blk=%ld renderToRAM=%d\n", blk, want ? 1 : 0);
                }
            }
        }
        { s4267::T s4267_pd(5); app->processDisplayLists(app->core.RDRAM, lo_phys, hi_phys, /*isHLE*/ false); }
        if (rdpq::aq_on && rdpq::in_task) { rdpq::t_sync += rdpq::aq_ms(st0, rdpq::aclk::now()); rdpq::t_bytes += hi_phys - lo_phys; ++rdpq::t_calls; }
#endif
    }

    void submit_rdp_range(uint32_t lo_phys, uint32_t hi_phys) {
        RT64::Application *app = g_rt64_app.load();
        if (app && hi_phys > lo_phys) {
            // s6165: join RDP targets to the VI state at the same submission.
            // The budget is per phase so boot traffic cannot hide menu frames.
            static int s_route = -1;
            static int s_words = -1;
            static uint32_t s_route_phase = UINT32_MAX;
            static uint32_t s_route_rows = 0;
            static uint32_t s_word_phase = UINT32_MAX;
            static uint32_t s_word_rows = 0;
            if (s_route < 0) {
                const char* e = std::getenv("ROGUESQ_LOG_RDP_ROUTE");
                s_route = (e && *e && *e != '0') ? 1 : 0;
            }
            if (s_words < 0) {
                const char* e = std::getenv("ROGUESQ_LOG_RDP_WORDS");
                s_words = (e && *e && *e != '0') ? 1 : 0;
            }
            if (s_route || s_words) {
                const uint32_t phase = rs64_phase_ord();
                if (phase != s_route_phase) {
                    s_route_phase = phase;
                    s_route_rows = 0;
                }
                const auto* vi = ultramodern::renderer::get_vi_regs();
                const uint32_t viw = vi ? vi->VI_WIDTH_REG : 0;
                const uint32_t vio = vi ? vi->VI_ORIGIN_REG : 0;
                if (s_route_rows < 160 && viw >= 320 && viw <= 1024 && app->core.RDRAM) {
                    const uint8_t* r = app->core.RDRAM;
                    uint32_t a = lo_phys;
                    bool saw_ci = false, saw_sc = false;
                    while (a + 8 <= hi_phys) {
                        const uint32_t w0 = (uint32_t(r[a ^ 3]) << 24) |
                                            (uint32_t(r[(a + 1) ^ 3]) << 16) |
                                            (uint32_t(r[(a + 2) ^ 3]) << 8) |
                                            uint32_t(r[(a + 3) ^ 3]);
                        const uint32_t w1 = (uint32_t(r[(a + 4) ^ 3]) << 24) |
                                            (uint32_t(r[(a + 5) ^ 3]) << 16) |
                                            (uint32_t(r[(a + 6) ^ 3]) << 8) |
                                            uint32_t(r[(a + 7) ^ 3]);
                        const uint32_t op = (w0 >> 24) & 0x3F;
                        uint32_t n = 8;
                        if (op >= 8 && op <= 15) n = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
                        else if (op == 0x24 || op == 0x25) n = 16;
                        if (s_words && phase >= 4u) {
                            if (phase != s_word_phase) {
                                s_word_phase = phase;
                                s_word_rows = 0;
                            }
                            if (s_word_rows < 20000u) {
                                std::fprintf(stderr,
                                    "[g1d-word] phase=%u row=%u addr=0x%06X op=0x%02X w0=0x%08X w1=0x%08X vi_w=%u vi_o=0x%06X\n",
                                    phase, s_word_rows, a, op, w0, w1, viw, vio & 0xFFFFFFu);
                                ++s_word_rows;
                            }
                        }
                        if (phase >= 4u) {
                            static int s_cmd_log = -1;
                            static uint32_t s_cmd_phase = UINT32_MAX;
                            static uint32_t s_cmd_rows = 0;
                            if (s_cmd_log < 0) {
                                const char *e = std::getenv("ROGUESQ_LOG_G1D_CMD");
                                s_cmd_log = (e && *e && *e != '0') ? 1 : 0;
                            }
                            if (s_cmd_log) {
                                if (phase != s_cmd_phase) { s_cmd_phase = phase; s_cmd_rows = 0; }
                                const bool rect = (op == 0x24 || op == 0x25 ||
                                                   op == 0x2D || op == 0x36);
                                const bool draw = (op >= 0x08 && op <= 0x0F) || rect;
                                const bool structural = (op == 0x2D || op == 0x3F);
                                static uint32_t s_ti_w0 = 0, s_ti_w1 = 0;
                                if (op == 0x3D) { s_ti_w0 = w0; s_ti_w1 = w1; }
                                static uint32_t s_st_w0[8], s_st_w1[8], s_lb_w0 = 0, s_lb_w1 = 0, s_lb_op = 0;
                                if (op == 0x35) { s_st_w0[(w1 >> 24) & 7] = w0; s_st_w1[(w1 >> 24) & 7] = w1; }
                                if (op == 0x33 || op == 0x34) { s_lb_w0 = w0; s_lb_w1 = w1; s_lb_op = op; }
                                if (rect && (op == 0x24 || op == 0x25) && s_cmd_rows < 4000u) {
                                    // s6230: SETTIMG source + content probe for each texrect
                                    // s7649 MK8: keyed at 16 MB (dd>1 / OSMEM 12 photo tiles sit at 0x9xxxxx-0xBxxxxx; the
                                    // old & 0x7FFFFF key hashed aliased low RAM, s6230/s6231). tex8= prints the old key.
                                    const uint32_t ta = s_ti_w1 & 0xFFFFFFu, ta8 = s_ti_w1 & 0x7FFFFFu;
                                    uint32_t h = 2166136261u; uint32_t hist[256] = {0}; uint32_t distinct = 0;
                                    uint32_t b0 = 0;
                                    if (ta + 64 <= 0x1000000u) {
                                        for (uint32_t i = 0; i < 64; ++i) {
                                            const uint8_t bb = r[(ta + i) ^ 3];
                                            h = (h ^ bb) * 16777619u;
                                            if (!hist[bb]++) ++distinct;
                                            if (i < 4) b0 = (b0 << 8) | bb;
                                        }
                                    }
                                    std::fprintf(stderr,
                                        "[g1d-tex] phase=%u row=%u addr=0x%06X tex=0x%06X tex8=0x%06X fmt=%u siz=%u w=%u hash=0x%08X distinct64=%u b0=0x%08X\n",
                                        phase, s_cmd_rows, a, ta, ta8, (s_ti_w0 >> 21) & 7, (s_ti_w0 >> 19) & 3,
                                        (s_ti_w0 & 0xFFF) + 1, h, distinct, b0);
                                    {
                                        // s6231: SETTILE/LOAD params in force + full 4096 B tile dump
                                        const uint32_t t7 = (w1 >> 24) & 7;
                                        std::fprintf(stderr,
                                            "[g1d-tex2] phase=%u row=%u addr=0x%06X tile=%u st_w0=0x%08X st_w1=0x%08X st7_w0=0x%08X st0_w0=0x%08X ld_op=0x%02X ld_w0=0x%08X ld_w1=0x%08X\n",
                                            phase, s_cmd_rows, a, t7, s_st_w0[t7], s_st_w1[t7], s_st_w0[7], s_st_w0[0], s_lb_op, s_lb_w0, s_lb_w1);
                                        static uint32_t s_dumped = 0;
                                        if (s_dumped < 70u && ta + 4096 <= 0x1000000u) {
                                            char fn[160];
                                            std::snprintf(fn, sizeof(fn), "scratch/agent/m6/s6231_tiles/%02u_%06X.bin", s_dumped, ta);
                                            if (FILE* df = std::fopen(fn, "wb")) {
                                                uint8_t buf[4096];
                                                for (uint32_t i = 0; i < 4096; ++i) buf[i] = r[(ta + i) ^ 3];
                                                std::fwrite(buf, 1, 4096, df); std::fclose(df);
                                            }
                                            ++s_dumped;
                                        }
                                    }
                                }
                                if ((draw || structural) && s_cmd_rows < 4000u) {
                                    uint32_t x0 = 0, y0 = 0, x1 = 0, y1 = 0;
                                    bool central = false;
                                    if (rect) {
                                        x0 = ((w0 >> 12) & 0xFFF) >> 2;
                                        y0 = (w0 & 0xFFF) >> 2;
                                        x1 = ((w1 >> 12) & 0xFFF) >> 2;
                                        y1 = (w1 & 0xFFF) >> 2;
                                        if (x0 > x1) { const uint32_t t = x0; x0 = x1; x1 = t; }
                                        if (y0 > y1) { const uint32_t t = y0; y0 = y1; y1 = t; }
                                        central = x0 < (viw * 2u) / 3u && x1 > viw / 3u && y1 > y0;
                                    }
                                    const char *kind = (op == 0x3F) ? "cimg" :
                                        (op == 0x2D) ? "scissor" :
                                        (op == 0x24) ? "texrect" :
                                        (op == 0x25) ? "texrectflip" :
                                        (op == 0x36) ? "fillrect" : "tri";
                                    std::fprintf(stderr,
                                        "[g1d-cmd] phase=%u row=%u addr=0x%06X op=0x%02X kind=%s "
                                        "rect=%u,%u-%u,%u central=%u w0=0x%08X w1=0x%08X "
                                        "task=%u root_dl=0x%06X guest_pc=0x%08X "
                                        "dpc=0x%06X-0x%06X submit=%llu\n",
                                        phase, s_cmd_rows++, a, op, kind,
                                        x0, y0, x1, y1, central ? 1u : 0u, w0, w1,
                                        rs64_e9prov_current_task(),
                                        rs64_e9prov_current_root_dl() & 0x7FFFFFu,
                                        (uint32_t)g_rs64_last_guest_pc,
                                        g_rsp_dpc_start & 0x3FFFFFFu,
                                        g_rsp_dpc_end & 0x3FFFFFFu,
                                        (unsigned long long)rs64_dpc_get_last_submit_serial());
                                }
                            }
                        }
                        if (op == 0x3F) {
                            if (g_rs64_g1d_join_phase.load(std::memory_order_relaxed) != phase)
                                g_rs64_g1d_join_cis.store(0, std::memory_order_relaxed);
                            g_rs64_g1d_join_phase.store(phase, std::memory_order_relaxed);
                            g_rs64_g1d_join_lo.store(lo_phys, std::memory_order_relaxed);
                            g_rs64_g1d_join_hi.store(hi_phys, std::memory_order_relaxed);
                            g_rs64_g1d_join_ci_w.store((w0 & 0x3FF) + 1u, std::memory_order_relaxed);
                            g_rs64_g1d_join_ci_a.store(w1 & 0xFFFFFFu, std::memory_order_relaxed);
                            g_rs64_g1d_join_cis.fetch_add(1, std::memory_order_relaxed);
                            {
                                std::lock_guard<std::mutex> lock(g_rs64_g1d_ci_mutex);
                                if (g_rs64_g1d_ci_frame.size() < 64) {
                                    g_rs64_g1d_ci_frame.push_back({(w0 & 0x3FF) + 1u,
                                                                    w1 & 0xFFFFFFu,
                                                                    lo_phys, hi_phys});
                                }
                            }
                            std::fprintf(stderr, "[rdp-route] phase=%u lo=0x%06X len=%u ci_w=%u ci_a=0x%06X vi_w=%u vi_o=0x%06X\n",
                                phase, lo_phys, hi_phys - lo_phys, (w0 & 0x3FF) + 1, w1 & 0xFFFFFF, viw, vio & 0xFFFFFF);
                            saw_ci = true;
                        } else if (op == 0x2D) {
                            std::fprintf(stderr, "[rdp-route] phase=%u lo=0x%06X len=%u sc=%u,%u-%u,%u vi_w=%u vi_o=0x%06X\n",
                                phase, lo_phys, hi_phys - lo_phys, (w0 >> 12) & 0xFFF, w0 & 0xFFF,
                                (w1 >> 12) & 0xFFF, w1 & 0xFFF, viw, vio & 0xFFFFFF);
                            saw_sc = true;
                        }
                        a += n;
                    }
                    if (saw_ci || saw_sc) ++s_route_rows;
                    std::fflush(stderr);
                }
            }
            {
                // s6206: phase-4 color/texture image addresses inside the
                // early-image span. A summary line fires even when the hit
                // count is zero, so a miss is not a silent scanner.
                static int s_img = -1;
                static uint32_t s_subs = 0, s_ci = 0, s_ti = 0, s_ci_hit = 0, s_ti_hit = 0;
                static uint32_t s_hits = 0;
                static uint32_t s_last_ci = 0, s_last_ti = 0;
                static int s_logged_ci = 0;
                // Distinct phase-4 TI addresses in [0xA6A000, 0xB00000).
                // The 48-line hit log stays capped. Past 256 kept addresses,
                // below-pool addresses are dropped (ov=1) but max still
                // moves, and above-pool addresses go in the side buffer so
                // that count stays exact until abcap.
                static uint32_t s_ti_set[256];
                static uint32_t s_ti_extra[256];
                static uint32_t s_ti_n = 0;
                static uint32_t s_ti_extra_n = 0;
                static uint32_t s_ti_min = 0xFFFFFFFFu;
                static uint32_t s_ti_max = 0;
                static uint32_t s_ti_ov = 0;
                static uint32_t s_ti_extra_ov = 0;
                static int s_ti_saw_ctl = 0;
                static int s_ti_saw_wide = 0;
                if (s_img < 0) {
                    const char* e = std::getenv("ROGUESQ_LOG_G1D_TASK");
                    s_img = (e && *e && *e != '0') ? 1 : 0;
                }
                if (s_img && app->core.RDRAM && rs64_phase_ord() == 4u) {
                    const uint8_t* r = app->core.RDRAM;
                    uint32_t a = lo_phys;
                    while (a + 8 <= hi_phys) {
                        const uint32_t w0 = (uint32_t(r[a ^ 3]) << 24) |
                                            (uint32_t(r[(a + 1) ^ 3]) << 16) |
                                            (uint32_t(r[(a + 2) ^ 3]) << 8) |
                                            uint32_t(r[(a + 3) ^ 3]);
                        const uint32_t w1 = (uint32_t(r[(a + 4) ^ 3]) << 24) |
                                            (uint32_t(r[(a + 5) ^ 3]) << 16) |
                                            (uint32_t(r[(a + 6) ^ 3]) << 8) |
                                            uint32_t(r[(a + 7) ^ 3]);
                        const uint32_t op = (w0 >> 24) & 0x3F;
                        uint32_t ncmd = 8;
                        if (op >= 8 && op <= 15) {
                            ncmd = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
                        } else if (op == 0x24 || op == 0x25) {
                            ncmd = 16;
                        }
                        if (op == 0x3F || op == 0x3D) {
                            const uint32_t addr = w1 & 0x00FFFFFFu;
                            const bool hit = addr >= 0x00A6A000u && addr < 0x00B00000u;
                            if (op == 0x3F) { ++s_ci; s_last_ci = addr; if (hit) ++s_ci_hit; }
                            else { ++s_ti; s_last_ti = addr; if (hit) ++s_ti_hit; }
                            if (hit && s_hits < 48u) {
                                ++s_hits;
                                std::fprintf(stderr,
                                    "[g1d-img-hit] kind=%s addr=0x%06X w0=0x%08X w1=0x%08X pc=0x%08X n=%u\n",
                                    op == 0x3F ? "ci" : "ti", addr, w0, w1,
                                    (uint32_t)g_rs64_last_guest_pc, s_hits);
                                std::fflush(stderr);
                            }
                            if (op == 0x3D && hit) {
                                if (addr < s_ti_min) s_ti_min = addr;
                                if (addr > s_ti_max) s_ti_max = addr;
                                if (addr == 0x00A6AA10u) s_ti_saw_ctl = 1;
                                if (addr == 0x00AE5F20u) s_ti_saw_wide = 1;
                                {
                                    static const uint32_t k_tb[3] = {0x00A6AA10u, 0x00AE5F20u, 0x00AE6B20u};
                                    static bool s_tb_done[3] = {false, false, false};
                                    static uint32_t s_tb_hits[3] = {0, 0, 0};
                                    for (int ti = 0; ti < 3; ++ti) {
                                        if (addr == k_tb[ti] && ++s_tb_hits[ti] == 2u) rs64_g1d_tb2("ti-hit2");
                                        if (addr != k_tb[ti] || s_tb_done[ti]) continue;
                                        s_tb_done[ti] = true;
                                        rs64_g1d_tb2("ti-hit1");
                                        uint32_t wv[8];
                                        for (uint32_t k = 0; k < 8u; ++k) {
                                            uint32_t v = 0;
                                            for (uint32_t b = 0; b < 4u; ++b)
                                                v = (v << 8) | r[(addr + k * 4u + b) ^ 3u];
                                            wv[k] = v;
                                        }
                                        std::fprintf(stderr,
                                            "[g1d-tb] addr=0x%06X %08X %08X %08X %08X %08X %08X %08X %08X\n",
                                            addr, wv[0], wv[1], wv[2], wv[3], wv[4], wv[5], wv[6], wv[7]);
                                        std::fflush(stderr);
                                    }
                                }
                                bool seen = false;
                                for (uint32_t i = 0; i < s_ti_n; ++i) {
                                    if (s_ti_set[i] == addr) { seen = true; break; }
                                }
                                if (!seen) {
                                    for (uint32_t i = 0; i < s_ti_extra_n; ++i) {
                                        if (s_ti_extra[i] == addr) { seen = true; break; }
                                    }
                                }
                                if (!seen) {
                                    if (s_ti_n < 256u) {
                                        s_ti_set[s_ti_n++] = addr;
                                    } else {
                                        s_ti_ov = 1u;
                                        uint32_t pool_now = 0;
                                        const uint32_t ram_bytes = rs64_ram_top > 0x80000000u
                                            ? (rs64_ram_top - 0x80000000u) : 0u;
                                        if (0x1163ECu <= ram_bytes) {
                                            for (uint32_t b = 0; b < 4u; ++b) {
                                                pool_now = (pool_now << 8) | r[(0x1163E8u + b) ^ 3u];
                                            }
                                        }
                                        const uint32_t pool_phys = pool_now & 0x00FFFFFFu;
                                        if (pool_phys != 0u && addr >= pool_phys) {
                                            if (s_ti_extra_n < 256u) s_ti_extra[s_ti_extra_n++] = addr;
                                            else s_ti_extra_ov = 1u;
                                        }
                                    }
                                }
                            }
                        }
                        a += ncmd;
                    }
                    ++s_subs;
                    if ((s_ci > 0u && !s_logged_ci) || s_subs <= 4u ||
                        (s_ci == 0u && s_subs <= 64u) || (s_subs % 16u) == 0u) {
                        std::fprintf(stderr,
                            "[g1d-img] phase=4 subs=%u ci=%u ti=%u ci_hit=%u ti_hit=%u last_ci=0x%06X last_ti=0x%06X pc=0x%08X\n",
                            s_subs, s_ci, s_ti, s_ci_hit, s_ti_hit, s_last_ci, s_last_ti,
                            (uint32_t)g_rs64_last_guest_pc);
                        uint32_t pool = 0;
                        const uint32_t ram_bytes = rs64_ram_top > 0x80000000u
                            ? (rs64_ram_top - 0x80000000u) : 0u;
                        if (0x1163ECu <= ram_bytes) {
                            for (uint32_t b = 0; b < 4u; ++b)
                                pool = (pool << 8) | r[(0x1163E8u + b) ^ 3u];
                        }
                        const uint32_t pool_phys = pool & 0x00FFFFFFu;
                        uint32_t above = 0;
                        uint32_t low = 0;
                        uint32_t listed[8];
                        auto take_above = [&](uint32_t a) {
                            if (pool_phys == 0u || a < pool_phys) return;
                            if (above < 8u) listed[above] = a;
                            if (above == 0u || a < low) low = a;
                            ++above;
                        };
                        for (uint32_t i = 0; i < s_ti_n; ++i) take_above(s_ti_set[i]);
                        for (uint32_t i = 0; i < s_ti_extra_n; ++i) take_above(s_ti_extra[i]);
                        char addr_txt[96];
                        addr_txt[0] = 0;
                        if (above >= 1u && above <= 8u) {
                            for (uint32_t i = 1; i < above; ++i) {
                                const uint32_t v = listed[i];
                                uint32_t j = i;
                                while (j > 0u && listed[j - 1u] > v) {
                                    listed[j] = listed[j - 1u];
                                    --j;
                                }
                                listed[j] = v;
                            }
                            size_t used = 0;
                            for (uint32_t i = 0; i < above; ++i) {
                                used += static_cast<size_t>(std::snprintf(
                                    addr_txt + used, sizeof(addr_txt) - used,
                                    "%s0x%06X", i ? "," : "", listed[i]));
                            }
                        }
                        const uint32_t n_known = s_ti_n + s_ti_extra_n;
                        std::fprintf(stderr,
                            "[g1d-ti] n=%u min=0x%06X max=0x%06X above=%u low=0x%06X ov=%u abcap=%u pool=0x%08X saw=%s%s%s%s%s%s\n",
                            n_known, n_known ? s_ti_min : 0u, n_known ? s_ti_max : 0u,
                            above, above ? low : 0u, s_ti_ov, s_ti_extra_ov, pool,
                            s_ti_saw_ctl ? "0xA6AA10" : "",
                            (s_ti_saw_ctl && s_ti_saw_wide) ? "," : "",
                            s_ti_saw_wide ? "0xAE5F20" : "",
                            (!s_ti_saw_ctl && !s_ti_saw_wide) ? "none" : "",
                            addr_txt[0] ? " addrs=" : "",
                            addr_txt);
                        std::fflush(stderr);
                        if (s_ci > 0u) s_logged_ci = 1;
                    }
                }
            }
            // Diagnostic: log the LAST submission's last bytes so we can see
            // what RDP commands trigger RT64's vector-OOB assert. Gate behind
            // ROGUESQ_LOG_RDP_SUBMIT=1.
            static int s_log = -1;
            if (s_log < 0) {
                const char* e = std::getenv("ROGUESQ_LOG_RDP_SUBMIT");
                s_log = (e && *e && *e != '0') ? 1 : 0;
            }
            if (s_log) {
                static int s_count = 0;
                ++s_count;
                uint32_t len = hi_phys - lo_phys;
                fprintf(stderr, "[rdp-submit #%d] lo=0x%08X hi=0x%08X len=%u\n",
                        s_count, lo_phys, hi_phys, len);
                // Dump first 32 bytes of submission (4 commands worth)
                if (len >= 8 && app->core.RDRAM) {
                    uint8_t* bytes = app->core.RDRAM + lo_phys;
                    int dump_len = (int)std::min<uint32_t>(len, 64);
                    fprintf(stderr, "  bytes: ");
                    for (int i = 0; i < dump_len; ++i) {
                        fprintf(stderr, "%02X ", bytes[i]);
                        if ((i & 7) == 7 && i + 1 < dump_len) fprintf(stderr, "\n         ");
                    }
                    fprintf(stderr, "\n");
                }
                fflush(stderr);
            }
            if (rs64_g1d_walk_diag == 1 && app->core.RDRAM) {   // s6851: wrapped rect about to reach RT64 vs what the s6850 walker saw
                static uint32_t s_cw = 0; static int s_hit = 0, s_ctl = 0, s_rng = 0;
                const uint8_t *r = app->core.RDRAM;
                auto rw = [&](uint32_t a) { uint32_t v; memcpy(&v, r + a, 4); return v; };
                for (uint32_t a = lo_phys, n = 8; a + 8 <= hi_phys; a += n) {
                    const uint32_t w0 = rw(a), w1 = rw(a + 4), op = (w0 >> 24) & 0x3F; n = 8;
                    if (op >= 0x08 && op <= 0x0F) n = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
                    else if (op == 0x24 || op == 0x25) n = 16;
                    else if (op == 0x3F) s_cw = (w0 & 0x3FF) + 1;
                    if (op != 0x24 && op != 0x25 && op != 0x36) continue;
                    const uint32_t lrx = (w0 >> 12) & 0xFFF, lry = w0 & 0xFFF, ulx = (w1 >> 12) & 0xFFF, uly = w1 & 0xFFF;
                    const bool zw = op == 0x36 && ulx == 0 && lrx == 0 && lry > uly, wr = lrx < ulx && lry > uly && ulx < s_cw * 4;
                    if (!zw && !wr) continue;
                    if (zw ? s_ctl++ >= 12 : s_hit++ >= 300) continue;
                    // where did the walker step around a?
                    const auto &v = g_rs64_g1d_walk; size_t i = 0, prev = SIZE_MAX;
                    for (; i < v.size(); i += 3) { if (v[i] == a) break; if (v[i] < a) prev = i; }
                    const bool same = rs64_g1d_walk_lo == lo_phys && rs64_g1d_walk_hi == hi_phys;
                    if (i < v.size())
                        fprintf(stderr, "[g1d-binwalk] %s vi=%u lo=%06X hi=%06X a=%06X bin=%08X,%08X cw=%u walk=%s walked=%08X,%08X wcw=%u\n",
                            zw ? "ZW" : "WRAP", rs64_vi_n_g, lo_phys, hi_phys, a, w0, w1, s_cw, same ? "same" : "other", v[i + 1], v[i + 2], g_rs64_g1d_walk_cw[i / 3]);
                    else
                        fprintf(stderr, "[g1d-binwalk] %s vi=%u lo=%06X hi=%06X a=%06X bin=%08X,%08X cw=%u walk=%s(%06X..%06X n=%zu) MISSED prev=%06X:%08X,%08X\n",
                            zw ? "ZW" : "WRAP", rs64_vi_n_g, lo_phys, hi_phys, a, w0, w1, s_cw, same ? "same" : "other", rs64_g1d_walk_lo, rs64_g1d_walk_hi,
                            v.size() / 3, prev == SIZE_MAX ? 0u : v[prev], prev == SIZE_MAX ? 0u : v[prev + 1], prev == SIZE_MAX ? 0u : v[prev + 2]);
                }
                (void)s_rng;
            }
            {   // s4517: raw RDP byte dump (RS64_RDP_BIN_PORT=path) for retail rdp.bin diff.
                // s6787: RS64_RDP_BIN_PORT_MAX_MB = file cap (default 600 MB; two-passcode SHOWROOM routes need ~1.5 GB).
                static FILE *s_bin = nullptr; static int s_bin_init = 0; static uint64_t s_bin_total = 0, s_bin_cap = 600ull << 20;
                if (!s_bin_init) { s_bin_init = 1; const char *e = std::getenv("RS64_RDP_BIN_PORT"); if (e && *e) s_bin = fopen(e, "wb");
                    const char *m = std::getenv("RS64_RDP_BIN_PORT_MAX_MB"); if (m && *m) s_bin_cap = (uint64_t)strtoull(m, nullptr, 10) << 20; }
                // s6922: RS64_RDP_BIN_PORT_WIN=<from_s>:<to_s>, seconds since the first submit, so one late shot can be dumped from a long run.
                static double s_bin_from = -1, s_bin_to = 0; static uint64_t s_bin_t0 = 0;
                if (s_bin_from < 0) { s_bin_from = 0; s_bin_t0 = mach_absolute_time(); const char *e = std::getenv("RS64_RDP_BIN_PORT_WIN"); if (e && *e) sscanf(e, "%lf:%lf", &s_bin_from, &s_bin_to); }
                const double s_bin_now = (double)(mach_absolute_time() - s_bin_t0) / 24e6;
                if (s_bin && app->core.RDRAM && s_bin_total < s_bin_cap && s_bin_now >= s_bin_from && (s_bin_to <= 0 || s_bin_now < s_bin_to)) {
                    // s6792: RS64_RDP_BIN_PORT_VI=1 stamps the VI counter instead of the phase ordinal (per-shot cinematic
                    // durations in VIs, tools/g3_cine_sweep.py).
                    static int s_bin_vi = -1; if (s_bin_vi < 0) { const char *v = std::getenv("RS64_RDP_BIN_PORT_VI"); s_bin_vi = (v && *v && *v != '0') ? 1 : 0; }
                    uint32_t hdr[4] = {0x50445250u, lo_phys, hi_phys - lo_phys, s_bin_vi ? (uint32_t)rs64_vi_n_g : rs64_phase_ord()};
                    fwrite(hdr, 4, 4, s_bin);
                    fwrite(app->core.RDRAM + lo_phys, 1, hi_phys - lo_phys, s_bin);
                    s_bin_total += 16 + (hi_phys - lo_phys);
                }
            }
            {   // s6070 g1cf: per-VI accumulation (tri counted from the RDP stream, independent of the s5424 gate)
                s_g1cf.subs++; s_g1cf.bytes += hi_phys - lo_phys; s_g1cf.lastlen = hi_phys - lo_phys;
                if (hi_phys - lo_phys > s_g1cf.maxlen) s_g1cf.maxlen = hi_phys - lo_phys;
                if (app->core.RDRAM) { const uint8_t *r = app->core.RDRAM; uint32_t a = lo_phys;
                    while (a + 8 <= hi_phys) { uint32_t op = r[a ^ 3] & 0x3F, n = 8;
                        if (op >= 0x08 && op <= 0x0F) { n = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0); ++s_g1cf.tri;
                            if (a + 32 <= hi_phys) {   // s7232 bbox classify
                                uint32_t w[8]; memcpy(w, r + a, 32);
                                auto s14 = [](uint32_t v) { return (float)((int32_t)(v << 18) >> 18) * 0.25f; };
                                const float yl = s14(w[0] & 0x3FFF), ym = s14((w[1] >> 16) & 0x3FFF), yh = s14(w[1] & 0x3FFF);
                                const float xl = (int32_t)w[2] / 65536.f, dl = (int32_t)w[3] / 65536.f, xh = (int32_t)w[4] / 65536.f,
                                            dh = (int32_t)w[5] / 65536.f, xm = (int32_t)w[6] / 65536.f, dm = (int32_t)w[7] / 65536.f;
                                const float yt = floorf(yh), px[6] = {xh, xm, xh + dh * (ym - yt), xm + dm * (ym - yt), xl, xl + dl * (yl - ym)};
                                float x0 = px[0], x1 = px[0]; for (float v : px) { x0 = std::min(x0, v); x1 = std::max(x1, v); }
                                { const float xe = xh + dh * (yl - yt); x0 = std::min(x0, xe); x1 = std::max(x1, xe); }
                                const float *sc = s_g1cf_sc, sw = sc[2] - sc[0];
                                if (yl - yh < 1.0f && floorf(yl) == floorf(yh)) ++s_g1cf.tzero;
                                else if (x1 <= sc[0] || x0 >= sc[2] || yl <= sc[1] || yh >= sc[3]) ++s_g1cf.tout;
                                else { ++s_g1cf.tin;
                                    const float cx0 = std::max(x0, sc[0]), cx1 = std::min(x1, sc[2]), cy0 = std::max(yh, sc[1]), cy1 = std::min(yl, sc[3]);
                                    s_g1cf.area += (double)(cx1 - cx0) * (cy1 - cy0);
                                    int b = sw > 0 ? (int)(((cx0 + cx1) * 0.5f - sc[0]) / sw * 8.f) : 0; s_g1cf.bin[std::clamp(b, 0, 7)]++; }
                                if (x1 <= sc[0] + sw || x0 >= sc[2] + sw || yl <= sc[1] || yh >= sc[3]) ++s_g1cf.vout;
                            } }
                        else if (op == 0x24 || op == 0x25) n = 16;
                        else if (op == 0x2D) { uint32_t w0, w1; memcpy(&w0, r + a, 4); memcpy(&w1, r + a + 4, 4);   // s7232 Set Scissor (10.2)
                            s_g1cf_sc[0] = ((w0 >> 12) & 0xFFF) * 0.25f; s_g1cf_sc[1] = (w0 & 0xFFF) * 0.25f;
                            s_g1cf_sc[2] = ((w1 >> 12) & 0xFFF) * 0.25f; s_g1cf_sc[3] = (w1 & 0xFFF) * 0.25f; }
                        a += n; } }
            }
            {   // s5424: per-submission RDP command census (ROGUESQ_LOG_RDP_TRICOUNT=1) for flight-vs-hangar geometry volume.
                static int s_tc = -1;
                if (s_tc < 0) { const char *e = std::getenv("ROGUESQ_LOG_RDP_TRICOUNT"); s_tc = (e && *e && *e != '0') ? 1 : 0; }
                if (s_tc && app->core.RDRAM) {
                    const uint8_t *r = app->core.RDRAM;
                    uint32_t tri = 0, trect = 0, frect = 0, other = 0, a = lo_phys;
                    while (a + 8 <= hi_phys) {
                        uint32_t op = r[a ^ 3] & 0x3F, n = 8;
                        if (op >= 0x08 && op <= 0x0F) { n = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0); ++tri; }
                        else if (op == 0x24 || op == 0x25) { n = 16; ++trect; }
                        else if (op == 0x36) { ++frect; }
                        else ++other;
                        a += n;
                    }
                    static uint32_t s_tc_n[64]; uint32_t tco = rs64_phase_ord() & 63;
                    if (s_tc_n[tco]++ < 4000)  // s5441: per-phase cap (log flood: 1.2M lines/phase)
                    fprintf(stderr, "[tricnt] ord=%u len=%u tri=%u trect=%u frect=%u other=%u\n",
                            rs64_phase_ord(), hi_phys - lo_phys, tri, trect, frect, other);
                }
            }
            static int s_dr = -1;
            uint64_t dr_t0 = 0, dr_r0 = 0;
            if (s_dr < 0) { const char *e = std::getenv("ROGUESQ_LOG_RT64_DRAWN"); s_dr = (e && *e && *e != '0') ? 1 : 0; }
            if (s_dr) { dr_t0 = g_rs64_rt64_tri_accepted.load(); dr_r0 = g_rs64_rt64_rect_accepted.load(); }
            run_rdp_submission(app, lo_phys, hi_phys);
            static uint32_t s_dr_n[64];
            if (s_dr && s_dr_n[rs64_phase_ord() & 63]++ < 4000) fprintf(stderr, "[rt64drawn] ord=%u tri=%llu rect=%llu\n", rs64_phase_ord(),
                              (unsigned long long)(g_rs64_rt64_tri_accepted.load() - dr_t0),
                              (unsigned long long)(g_rs64_rt64_rect_accepted.load() - dr_r0));
        }
    }
}
