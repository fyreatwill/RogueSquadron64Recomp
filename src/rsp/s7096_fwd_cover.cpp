// s7096 (rdp-submit-coverage): does the DPC bridge (src/rsp/dpc_bridge.cpp rsp_dpc_submit_impl + the deferred commit,
// wrap flush and stream flush) hand RT64 exactly the bytes a hardware RDP would consume, each once and in order?
//
// HW stream: on every mtc0 DPC_END v the hardware RDP consumes [CURRENT, v), with CURRENT = START when START_VALID
// (a fresh START), else the previous END (CURRENT persists across tasks). An instant RDP therefore consumes the
// concatenation of those ranges; we keep it per gfx task as coalesced runs plus a byte snapshot taken at END time.
// FWD stream: every ultramodern::submit_rdp_range call (all go through rs64_rt_submit), tagged by call site.
// Matcher (online, per task): a forwarded chunk at the HW cursor = matched (and its bytes are compared with the END-time
// snapshot = content diff, which includes intentional bridge edits such as spike culls); a chunk found AHEAD of the cursor
// skips the HW bytes in between into a pending list; a chunk found in the pending list = out of order; a chunk found
// only BEHIND the cursor = duplicate; a chunk in no HW run = foreign (synthetic FULL_SYNCs are expected here).
// At task end, pending + untouched tail bytes = missing; each missing byte is attributed to a drop the bridge recorded
// in the same task (pipe / synth / cimg / oob / wrapdrop / noflush / uj) or counted UNEXPLAINED.
// ROGUESQ_S7096_FWD=1 arms it; =ctl additionally mutates the matcher's input on 1 task per 1000 (inside the first
// forwarded call >= 64 B: drop 8 B, duplicate 8 B, swap two 8 B chunks, flip one snapshot byte), counted separately: every
// mutated ctl task must show missing, dup, order and content > 0. An init self-test on
// crafted streams is the detector's positive control. Dump: build/rs64_s7096.log every 5 s (SIGKILL-safe).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <vector>
#include <algorithm>
extern "C" int rs64_s7096_on = [] {
    const char* e = getenv("ROGUESQ_S7096_FWD");
    int v = !(e && *e && *e != '0') ? 0 : (e[0] == 'c' ? 2 : 1);
    if (v) fprintf(stderr, "[s7096] rdp forwarding coverage armed%s\n", v == 2 ? " (+ctl mutant)" : "");
    return v;
}();
namespace {
enum { S_LIVE, S_MERGED, S_WRAP, S_COMMIT, S_SYNTH, S_FORCEFS, S_N };
const char* kSite[S_N] = {"live", "merged", "wrap", "commit", "synth", "forcefs"};
enum { D_PIPE, D_SYNTHREP, D_CIMG, D_OOB, D_WRAPDROP, D_NOFLUSH, D_EQLAST, D_UJ, D_N };
const char* kDrop[D_N] = {"pipe", "synthrep", "cimg", "oob", "wrapdrop", "noflush", "eqlast", "uj"};
struct Run { uint32_t lo, hi; size_t off; };   // HW run, snapshot bytes at [off, off+hi-lo)
struct Rng { uint32_t lo, hi; size_t off; };
struct Drop { uint32_t lo, hi; int why; };
struct Tot {
    uint64_t tasks = 0, hw = 0, fwd = 0, matched = 0, order = 0, dup = 0, foreign = 0, missing_unexpl = 0, content = 0;
    uint64_t missing_by[D_N] = {}, fwd_site[S_N] = {}, dup_site[S_N] = {}, foreign_site[S_N] = {}, content_site[S_N] = {};
    uint64_t tasks_bad = 0, hw_laps_nostart = 0, drops_rec[D_N] = {};
    uint64_t pre = 0, pre_unaligned = 0, post_op[64] = {}, pre_op[64] = {}, pre_bytes = 0;
};
struct Ex { char s[160]; };
struct Matcher {
    std::vector<Run> hw; std::vector<uint8_t> snap; std::vector<Rng> pend; std::vector<Drop> drops;
    size_t cr = 0; uint32_t co = 0;   // cursor: run index, offset within run
    uint64_t hwb = 0, fwdb = 0, matched = 0, order = 0, dup = 0, foreign = 0, content = 0;
    uint64_t fwd_site[S_N] = {}, dup_site[S_N] = {}, foreign_site[S_N] = {}, content_site[S_N] = {};
    std::vector<Ex>* ex = nullptr; uint64_t task = 0;
    uint64_t pre = 0, pre_unaligned = 0, post_op[64] = {}, pre_op[64] = {}, pre_bytes = 0; int vex = 0;
    void clear() { hw.clear(); snap.clear(); pend.clear(); drops.clear(); pre = pre_unaligned = pre_bytes = 0; memset(post_op, 0, sizeof post_op); memset(pre_op, 0, sizeof pre_op); vex = 0; cr = 0; co = 0; hwb = fwdb = matched = order = dup = foreign = content = 0;
                   memset(fwd_site, 0, sizeof fwd_site); memset(dup_site, 0, sizeof dup_site); memset(foreign_site, 0, sizeof foreign_site); memset(content_site, 0, sizeof content_site); }
    void note(const char* fmt, uint32_t a, uint32_t b, int site) {
        if (!ex || ex->size() >= 16) return;
        Ex e; snprintf(e.s, sizeof e.s, "task=%llu %s 0x%06X..0x%06X site=%s", (unsigned long long)task, fmt, a, b, site >= 0 ? kSite[site] : "-");
        ex->push_back(e);
    }
    void add_hw(uint32_t lo, uint32_t hi, const uint8_t* rd) {
        if (hi <= lo) return;
        hwb += hi - lo;
        if (!hw.empty() && hw.back().hi == lo) hw.back().hi = hi; else hw.push_back({lo, hi, snap.size()});
        if (rd) snap.insert(snap.end(), rd + lo, rd + hi); else snap.resize(snap.size() + (hi - lo));
    }
    void ctl_flip(uint32_t a) {   // flip the END-time snapshot byte the cursor will compare for address a (control only)
        while (cr < hw.size() && co >= hw[cr].hi - hw[cr].lo) { cr++; co = 0; }
        if (cr < hw.size() && a >= hw[cr].lo + co && a < hw[cr].hi && hw[cr].off + (a - hw[cr].lo) < snap.size()) snap[hw[cr].off + (a - hw[cr].lo)] ^= 0xFF;
    }
    void cmp(uint32_t a, size_t off, uint32_t n, const uint8_t* rd, int site) {
        if (!rd) return;
        uint64_t d = 0;
        for (uint32_t i = 0; i < n; i++) if (rd[a + i] != snap[off + i]) {
            d++;
            const uint32_t c = (a + i) & ~7u; const size_t co8 = off + (c - a + i - i);  // command start in snapshot (snap is contiguous per run)
            (void)co8;
            const int op = rd[c + 3] & 0x3F; post_op[op]++;
            if (vex < 3 && ex && ex->size() < 40) { Ex e; snprintf(e.s, sizeof e.s, "task=%llu post-diff addr=0x%06X word_off=%u snap=%02X now=%02X op=%02X site=%s",
                (unsigned long long)task, a + i, (a + i) & 7, snap[off + i], rd[a + i], op, kSite[site]); ex->push_back(e); vex++; }
        }
        if (d) { content += d; content_site[site] += d; }
    }
    // Dry-run compare from the cursor without moving it (called just before the bridge's record/edit step).
    void precmp(uint32_t lo, uint32_t hi, const uint8_t* rd) {
        if (!rd || hi <= lo) return;
        size_t r = cr; uint32_t o = co; uint32_t p = lo;
        while (p < hi) {
            while (r < hw.size() && o >= hw[r].hi - hw[r].lo) { r++; o = 0; }
            if (r >= hw.size() || hw[r].lo + o != p) { pre_unaligned += hi - p; return; }
            const uint32_t n = std::min(hi - p, hw[r].hi - hw[r].lo - o);
            for (uint32_t i = 0; i < n; i++) if (rd[p + i] != snap[hw[r].off + o + i]) { pre++; pre_op[rd[((p + i) & ~7u) + 3] & 0x3F]++; }
            pre_bytes += n; o += n; p += n;
        }
    }
    void fwd(uint32_t lo, uint32_t hi, int site, const uint8_t* rd) {
        if (hi <= lo) return;
        fwdb += hi - lo; fwd_site[site] += hi - lo;
        uint32_t p = lo;
        while (p < hi) {
            while (cr < hw.size() && co >= hw[cr].hi - hw[cr].lo) { cr++; co = 0; }
            if (cr < hw.size() && hw[cr].lo + co == p) {
                const uint32_t n = std::min(hi - p, hw[cr].hi - hw[cr].lo - co);
                cmp(p, hw[cr].off + co, n, rd, site); matched += n; co += n; p += n; continue;
            }
            bool got = false;
            for (size_t i = 0; i < pend.size(); i++) {
                Rng& r = pend[i];
                if (p < r.lo || p >= r.hi) continue;
                const uint32_t n = std::min(hi - p, r.hi - p);
                cmp(p, r.off + (p - r.lo), n, rd, site);
                if (!order) note("out-of-order", p, p + n, site);
                order += n;
                // split r around [p, p+n)
                Rng tail{p + n, r.hi, r.off + (p + n - r.lo)}; r.hi = p;
                // s7365 class AP: r is a reference into pend; push_back may reallocate, so decide on r before it.
                const bool rdead = r.hi <= r.lo;
                if (rdead) pend.erase(pend.begin() + i);
                if (tail.hi > tail.lo) pend.push_back(tail);
                p += n; got = true; break;
            }
            if (got) continue;
            // ahead of the cursor?
            size_t fi = SIZE_MAX;
            for (size_t i = cr; i < hw.size(); i++) {
                const uint32_t from = (i == cr) ? hw[i].lo + co : hw[i].lo;
                if (p >= from && p < hw[i].hi) { fi = i; break; }
            }
            if (fi != SIZE_MAX) {   // skip HW bytes [cursor, p) into pending
                for (size_t i = cr; i <= fi; i++) {
                    const uint32_t a = (i == cr) ? hw[i].lo + co : hw[i].lo;
                    const uint32_t b = (i == fi) ? p : hw[i].hi;
                    if (b > a) pend.push_back({a, b, hw[i].off + (a - hw[i].lo)});
                }
                cr = fi; co = p - hw[fi].lo; continue;
            }
            const uint32_t n = std::min<uint32_t>(hi - p, 8);
            bool behind = false;
            for (size_t i = 0; i < hw.size() && !behind; i++) if (p >= hw[i].lo && p < hw[i].hi) behind = true;
            if (behind) { if (!dup) note("duplicate", p, hi, site); dup += n; dup_site[site] += n; }
            else { if (!foreign_site[site]) note("foreign", p, hi, site); foreign += n; foreign_site[site] += n; }
            p += n;
        }
    }
    // Missing bytes at task end: pending + tail. Attribute each to a recorded drop.
    void finish(uint64_t* by, uint64_t& unexpl) {
        std::vector<Rng> miss = pend;
        for (size_t i = cr; i < hw.size(); i++) {
            const uint32_t a = (i == cr) ? hw[i].lo + co : hw[i].lo;
            if (hw[i].hi > a) miss.push_back({a, hw[i].hi, 0});
        }
        for (const Rng& m : miss) {
            for (uint32_t a = m.lo; a < m.hi; a += 8) {
                const uint32_t b = std::min(a + 8, m.hi);
                int why = -1;
                for (const Drop& d : drops) if (a < d.hi && b > d.lo) { why = d.why; break; }
                if (why >= 0) by[why] += b - a; else { if (!unexpl) note("missing", a, m.hi, -1); unexpl += b - a; }
            }
        }
    }
};
struct Model { uint32_t start = 0, end = 0, cur = 0; bool sv = false; };
Model g_hm; Matcher g_m; Tot g_t, g_c; std::vector<Ex> g_ex, g_cex; time_t g_last = 0;
uint64_t g_task = 0; int g_ctl_task = 0, g_ctl_k = 0; bool g_ctl_held = false; uint32_t g_hold_lo = 0, g_hold_hi = 0; int g_hold_site = 0;
const uint8_t* g_rd = nullptr; bool g_selftest_ok = false; int g_selftest_bad = -1;
void fold(Tot& t, Matcher& m, uint64_t& tasks_ctl_ok) {
    uint64_t by[D_N] = {}, un = 0;
    m.finish(by, un);
    t.tasks++; t.hw += m.hwb; t.fwd += m.fwdb; t.matched += m.matched; t.order += m.order; t.dup += m.dup; t.foreign += m.foreign;
    t.content += m.content; t.missing_unexpl += un; t.pre += m.pre; t.pre_unaligned += m.pre_unaligned; t.pre_bytes += m.pre_bytes;
    for (int i = 0; i < 64; i++) { t.post_op[i] += m.post_op[i]; t.pre_op[i] += m.pre_op[i]; }
    for (int i = 0; i < D_N; i++) t.missing_by[i] += by[i];
    for (int i = 0; i < S_N; i++) { t.fwd_site[i] += m.fwd_site[i]; t.dup_site[i] += m.dup_site[i]; t.foreign_site[i] += m.foreign_site[i]; t.content_site[i] += m.content_site[i]; }
    if (un || m.order || m.dup) t.tasks_bad++;
    if (un && m.order && m.dup && m.content) tasks_ctl_ok++;
}
uint64_t g_ctl_ok = 0, g_dummy = 0;
void dump() {
    FILE* o = fopen("rs64_s7096.log", "w");
    if (!o) return;
    fprintf(o, "s7096 selftest=%s bad=%d mode=%d\n", g_selftest_ok ? "pass" : "FAIL", g_selftest_bad, rs64_s7096_on);
    for (int k = 0; k < 2; k++) {
        const Tot& t = k ? g_c : g_t;
        fprintf(o, "%s tasks=%llu tasks_bad=%llu hw=%llu fwd=%llu matched=%llu order=%llu dup=%llu foreign=%llu MISSING_UNEXPLAINED=%llu content_diff=%llu hw_laps_nostart=%llu%s\n",
                k ? "CTL" : "MAIN", (unsigned long long)t.tasks, (unsigned long long)t.tasks_bad, (unsigned long long)t.hw, (unsigned long long)t.fwd,
                (unsigned long long)t.matched, (unsigned long long)t.order, (unsigned long long)t.dup, (unsigned long long)t.foreign,
                (unsigned long long)t.missing_unexpl, (unsigned long long)t.content, (unsigned long long)t.hw_laps_nostart,
                k ? "" : "");
        fprintf(o, "  missing_by:"); for (int i = 0; i < D_N; i++) fprintf(o, " %s=%llu", kDrop[i], (unsigned long long)t.missing_by[i]); fprintf(o, "\n");
        fprintf(o, "  drops_recorded:"); for (int i = 0; i < D_N; i++) fprintf(o, " %s=%llu", kDrop[i], (unsigned long long)t.drops_rec[i]); fprintf(o, "\n");
        fprintf(o, "  pre_record_diff=%llu pre_unaligned=%llu pre_bytes(should equal fwd minus foreign)=%llu\n  diff_by_op post/pre:", (unsigned long long)t.pre, (unsigned long long)t.pre_unaligned, (unsigned long long)t.pre_bytes);
        for (int i = 0; i < 64; i++) if (t.post_op[i] || t.pre_op[i]) fprintf(o, " %02X=%llu/%llu", i, (unsigned long long)t.post_op[i], (unsigned long long)t.pre_op[i]);
        fprintf(o, "\n");
        fprintf(o, "  site fwd/dup/foreign/content:"); for (int i = 0; i < S_N; i++) fprintf(o, " %s=%llu/%llu/%llu/%llu", kSite[i], (unsigned long long)t.fwd_site[i],
                (unsigned long long)t.dup_site[i], (unsigned long long)t.foreign_site[i], (unsigned long long)t.content_site[i]); fprintf(o, "\n");
    }
    fprintf(o, "CTL tasks_with_all_three(must equal CTL tasks)=%llu\n", (unsigned long long)g_ctl_ok);
    for (const Ex& e : g_ex) fprintf(o, "EX %s\n", e.s);
    for (const Ex& e : g_cex) fprintf(o, "CTLEX %s\n", e.s);
    fclose(o);
}
// Detector positive control on crafted streams.
int selftest() {
    int bad = 0; uint8_t rd[0x400]; for (int i = 0; i < 0x400; i++) rd[i] = (uint8_t)i;
    auto mk = [&](Matcher& m) { m.clear(); m.add_hw(0x100, 0x140, rd); m.add_hw(0x140, 0x180, rd); m.add_hw(0x080, 0x0C0, rd); };   // run A (merged) + lap run B
    auto res = [&](Matcher& m, uint64_t* by, uint64_t& un) { memset(by, 0, sizeof(uint64_t) * D_N); un = 0; m.finish(by, un); };
    uint64_t by[D_N], un;
    { Matcher m; mk(m); m.fwd(0x100, 0x180, S_MERGED, rd); m.fwd(0x080, 0x0C0, S_WRAP, rd); res(m, by, un);
      if (un || m.order || m.dup || m.foreign || m.content || m.matched != 0xC0) bad++; }                        // exact
    { Matcher m; mk(m); m.fwd(0x100, 0x140, S_LIVE, rd); m.fwd(0x148, 0x180, S_LIVE, rd); m.fwd(0x080, 0x0C0, S_LIVE, rd); res(m, by, un);
      if (un != 8 || m.order || m.dup) bad++; }                                                                    // one 8-byte drop, unexplained
    { Matcher m; mk(m); m.drops.push_back({0x140, 0x148, D_PIPE}); m.fwd(0x100, 0x140, S_LIVE, rd); m.fwd(0x148, 0x180, S_LIVE, rd); m.fwd(0x080, 0x0C0, S_LIVE, rd);
      res(m, by, un); if (un || by[D_PIPE] != 8) bad++; }                                                          // same drop, attributed
    { Matcher m; mk(m); m.fwd(0x100, 0x180, S_LIVE, rd); m.fwd(0x170, 0x180, S_LIVE, rd); m.fwd(0x080, 0x0C0, S_LIVE, rd); res(m, by, un);
      if (m.dup != 0x10 || un || m.order) bad++; }                                                                 // duplicate
    { Matcher m; mk(m); m.fwd(0x140, 0x180, S_LIVE, rd); m.fwd(0x100, 0x140, S_LIVE, rd); m.fwd(0x080, 0x0C0, S_LIVE, rd); res(m, by, un);
      if (m.order != 0x40 || un || m.dup) bad++; }                                                                 // swap
    { Matcher m; mk(m); m.fwd(0x100, 0x180, S_LIVE, rd); m.fwd(0x300, 0x308, S_SYNTH, rd); m.fwd(0x080, 0x0C0, S_LIVE, rd); res(m, by, un);
      if (m.foreign != 8 || un || m.dup || m.order) bad++; }                                                       // foreign
    { Matcher m; mk(m); rd[0x150] ^= 0xFF; m.fwd(0x100, 0x180, S_LIVE, rd); m.fwd(0x080, 0x0C0, S_LIVE, rd); rd[0x150] ^= 0xFF; res(m, by, un);
      if (m.content != 1) bad++; }                                                                                 // late write
    { Matcher m; mk(m); m.fwd(0x100, 0x180, S_LIVE, rd); res(m, by, un); if (un != 0x40) bad++; }                 // lost lap tail
    return bad;
}
const bool g_init = [] {
    if (!rs64_s7096_on) return true;
    g_selftest_bad = selftest(); g_selftest_ok = g_selftest_bad == 0;
    fprintf(stderr, "[s7096] selftest %s (%d bad of 8)\n", g_selftest_ok ? "pass" : "FAIL", g_selftest_bad);
    g_m.ex = &g_ex;
    return true;
}();
}  // namespace
extern "C" void rs64_s7096_task() {   // called at every gfx task reset: fold the previous task
    if (g_ctl_held) { g_m.fwd(g_hold_lo, g_hold_hi, g_hold_site, g_rd); g_ctl_held = false; }
    if (g_ctl_task) fold(g_c, g_m, g_ctl_ok); else fold(g_t, g_m, g_dummy);
    if (g_ctl_task && (!g_c.tasks || g_c.tasks_bad < g_c.tasks)) { /* keep counting; ctl verdict = g_ctl_ok vs CTL tasks */ }
    ++g_task;
    g_ctl_task = (rs64_s7096_on == 2 && (g_task % 1000) == 999) ? 1 : 0;
    g_ctl_k = 0;
    const uint64_t prev_main_drops = 0; (void)prev_main_drops;
    g_m.clear(); g_m.task = g_task; g_m.ex = g_ctl_task ? &g_cex : &g_ex;
    time_t t = time(nullptr); if (t - g_last >= 5) { g_last = t; dump(); }
}
extern "C" void rs64_s7096_start(uint32_t v) { g_hm.start = v & 0xFFFFFF; g_hm.sv = true; }
extern "C" void rs64_s7096_end(uint32_t v, const uint8_t* rdram) {
    if (rdram) g_rd = rdram;
    v &= 0xFFFFFF;
    uint32_t from = g_hm.cur;
    if (g_hm.sv) { from = g_hm.start; g_hm.sv = false; }
    if ((int32_t)(v - from) < 0) (g_ctl_task ? g_c : g_t).hw_laps_nostart++;
    else if (v < 0x1000000u) g_m.add_hw(from, v, g_rd);
    g_hm.end = v; g_hm.cur = v;
}
extern "C" void rs64_s7096_fwd(uint32_t lo, uint32_t hi, int site) {
    lo &= 0xFFFFFF; hi = (hi - 1) % 0x1000000u + 1;
    if (g_ctl_task && !g_ctl_k && hi - lo >= 64) {   // mutate the first big call once: drop [8,16), dup [16,24), swap [24,32)/[32,40), flip one snapshot byte at +44
        g_ctl_k = 1;
        g_m.ctl_flip(lo + 44);
        g_m.fwd(lo, lo + 8, site, g_rd);
        g_m.fwd(lo + 16, lo + 24, site, g_rd); g_m.fwd(lo + 16, lo + 24, site, g_rd);
        g_m.fwd(lo + 32, lo + 40, site, g_rd); g_m.fwd(lo + 24, lo + 32, site, g_rd);
        g_m.fwd(lo + 40, hi, site, g_rd);
        return;
    }
    g_m.fwd(lo, hi, site, g_rd);
}
extern "C" void rs64_s7096_drop(uint32_t lo, uint32_t hi, int why) {
    lo &= 0xFFFFFF; hi &= 0xFFFFFF; if (hi <= lo) return;
    g_m.drops.push_back({lo, hi, why}); (g_ctl_task ? g_c : g_t).drops_rec[why] += hi - lo;
}
extern "C" void rs64_s7096_pre(uint32_t lo, uint32_t hi) { if (!g_ctl_task) g_m.precmp(lo & 0xFFFFFF, (hi - 1) % 0x1000000u + 1, g_rd); }
