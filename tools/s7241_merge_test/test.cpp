// s7241: host unit test of the s7239 WIDEWIN 2x2 merge mesh (run.sh extracts the live block from upstream_compat.cpp).
// Emulates renderFlatMeshFaceGroup's flat lod-2 TRI_GEN writer (docs/WIDEWIN-MERGE-PLAN.md fact 2) with the H3/H4/H5 hooks
// at the same points as tools/apply_s7239_widewin_merge.py, then decodes every emitted command the way the F5 ucode TriGen02
// does (fact 3) and checks the merged quad's four outer corners (x, y, z, colour) against the unmerged 2x2 block.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#include <array>
#include <mach/mach_time.h>
static int g_tog_ph = 1;
extern "C" void rs64_tog_anchor(uint64_t) {}
extern "C" int rs64_tog_odd(uint64_t) { return g_tog_ph; }
#include "s7239_block.inc"

static uint8_t* rd;
static void ww(uint32_t a, uint32_t v) { *reinterpret_cast<uint32_t*>(rd + (a - 0x80000000u)) = v; }
static uint32_t rw(uint32_t a) { return *reinterpret_cast<uint32_t*>(rd + (a - 0x80000000u)); }
static void wh(uint32_t a, uint16_t v) { *reinterpret_cast<uint16_t*>(rd + ((a - 0x80000000u) ^ 2u)) = v; }
static void wb(uint32_t a, uint8_t v) { rd[(a - 0x80000000u) ^ 3u] = v; }

struct Cell { int x, z, yb, v; int h[4]; uint32_t col[4]; uint16_t mat = 7; bool flat = true; float d2 = 1e9f; };
struct Corner { int x, y, z; uint32_t c; bool operator==(const Corner& o) const { return x == o.x && y == o.y && z == o.z && c == o.c; } };

static uint32_t g_base = 0x80200000u;
static int fails = 0, cases = 0;
static const uint32_t FARCUT = 0x8009DEB4u, CUR0 = 0x81000000u;
static const float FARCUT_V = 1000.f;

// Writes the cells as an element list (+0x00 next) and returns {group s1, list head s0}.
static std::pair<uint32_t, uint32_t> build(const std::vector<Cell>& cs, bool flag) {
    const uint32_t s1 = g_base; g_base += 0x100;
    ww(s1 + 0x2C, flag ? 0x40000000u : 0u);
    std::vector<uint32_t> el;
    for (const Cell& c : cs) {
        const uint32_t e = g_base, hp = g_base + 0x40, cg = g_base + 0x80; g_base += 0x100;
        el.push_back(e);
        wh(e + 0x08, (uint16_t)c.x); wh(e + 0x0A, (uint16_t)c.yb); wh(e + 0x0C, (uint16_t)c.z);
        ww(e + 0x10, c.flat ? 0x02020202u : 0x01010101u); ww(e + 0x14, 0x02000000u);
        ww(e + 0x18, 0); ww(e + 0x1C, 0);
        wb(e + 0x20, 0); wb(e + 0x21, 0x11); wh(e + 0x22, (uint16_t)(c.v >> 2));
        ww(e + 0x24, hp); ww(e + 0x28, cg); wh(e + 0x2C, c.mat); wh(e + 0x2E, 1);
        wb(hp + 0x00, (uint8_t)c.h[0]); wb(hp + 0x04, (uint8_t)c.h[1]); wb(hp + 0x14, (uint8_t)c.h[2]); wb(hp + 0x18, (uint8_t)c.h[3]);
        ww(cg + 0x00, c.col[0]); ww(cg + 0x10, c.col[1]); ww(cg + 0x50, c.col[2]); ww(cg + 0x60, c.col[3]);
        uint32_t d2b; memcpy(&d2b, &c.d2, 4); rs64_s7239_node(e, d2b);  // H1
    }
    for (size_t i = 0; i < el.size(); i++) ww(el[i], i + 1 < el.size() ? el[i + 1] : 0u);
    ww(s1 + 0x20, el.empty() ? 0u : el[0]);
    return {s1, el.empty() ? 0u : el[0]};
}

// renderFlatMeshFaceGroup's loop with the four hooks; returns the emitted command addresses.
static std::vector<uint32_t> emit(uint32_t s1, uint32_t s0) {
    std::vector<uint32_t> out; uint32_t cur = CUR0;
    if (g_rs64_s7239_on) rs64_s7239_group(rd, s1, s0, 1);  // H2
    for (uint32_t e = s0; e; e = rw(e)) {
        const uint32_t a3 = cur, hp = rw(e + 0x24), cg = rw(e + 0x28);
        auto hb = [&](uint32_t o) { return (int32_t)(int8_t)rd[(hp + o - 0x80000000u) ^ 3u]; };
        auto hh = [&](uint32_t o) { return *reinterpret_cast<uint16_t*>(rd + ((e + o - 0x80000000u) ^ 2u)); };
        ww(a3 + 0x00, 0x05000000u | (uint32_t)rd[(e + 0x21 - 0x80000000u) ^ 3u] << 16 | ((hh(0x2E) & 1) ? 0x300u : 0x200u));
        ww(a3 + 0x04, ((uint32_t)hb(0x00) << 20) | (((uint32_t)hb(0x04) << 4) & 0xFFFFu));
        ww(a3 + 0x08, ((uint32_t)hb(0x14) << 20) | (((uint32_t)hb(0x18) << 4) & 0xFFFFu));
        ww(a3 + 0x0C, rw(cg + 0x00)); ww(a3 + 0x10, rw(cg + 0x10)); ww(a3 + 0x14, rw(cg + 0x50)); ww(a3 + 0x18, rw(cg + 0x60));
        ww(a3 + 0x1C, (uint32_t)hh(0x2C) << 5);
        ww(a3 + 0x20, (uint32_t)hh(0x08) << 16 | hh(0x0A));
        ww(a3 + 0x24, (uint32_t)hh(0x0C) << 16 | (((uint32_t)(int32_t)(int16_t)hh(0x22) << 2) & 0xFFFFu));
        if (g_rs64_s7239_act) rs64_s7239_cmd(rd, e, a3);  // H3 (0x80011884)
        const bool sk = g_rs64_s7239_skip; cur += sk ? 0 : 0x28; g_rs64_s7239_skip = 0;  // H4 (0x800119A8)
        if (!sk) out.push_back(a3);
        // the next element overwrites a dropped slot, as on the game side
        if (sk) { std::vector<uint32_t> keep; for (uint32_t o : out) if (o != a3) keep.push_back(o); out = keep; }
    }
    if (g_rs64_s7239_act) rs64_s7239_end(rd);  // H5 (L_800119BC)
    return out;
}

// TriGen02 decode: origin (x, yb<<4, z) + {0, V} in x/z, corner heights (int16 halves of w1/w2) added to y.
static void decode(uint32_t a, Corner k[4]) {
    const int X = (int16_t)(rw(a + 0x20) >> 16), YB = (int16_t)(rw(a + 0x20) & 0xFFFF), Z = (int16_t)(rw(a + 0x24) >> 16), V = (int)(rw(a + 0x24) & 0xFFFF);
    const int h[4] = {(int16_t)(rw(a + 4) >> 16), (int16_t)(rw(a + 4) & 0xFFFF), (int16_t)(rw(a + 8) >> 16), (int16_t)(rw(a + 8) & 0xFFFF)};
    const int dx[4] = {0, V, 0, V}, dz[4] = {0, 0, V, V};
    for (int i = 0; i < 4; i++) k[i] = {X + dx[i], YB * 16 + h[i], Z + dz[i], rw(a + 0x0C + 4u * i)};
}
static Corner cellCorner(const Cell& c, int i) {
    const int dx[4] = {0, c.v, 0, c.v}, dz[4] = {0, 0, c.v, c.v};
    return {c.x + dx[i], c.yb * 16 + c.h[i] * 16, c.z + dz[i], c.col[i]};
}

static unsigned long long tally(int t) { return s7239_t[1][t] + s7239_t[0][t]; }
static void reset_t() { memset(s7239_t, 0, sizeof s7239_t); }

static Cell mk(int x, int z, int v, int seed) {
    Cell c; c.x = x; c.z = z; c.v = v; c.yb = 100 + seed * 7 % 23;
    for (int i = 0; i < 4; i++) { c.h[i] = ((seed * 31 + i * 17) % 200) - 100; c.col[i] = 0x10203000u + (uint32_t)seed * 16 + (uint32_t)i; }
    return c;
}
static std::vector<Cell> block(int x, int z, int v, int seed) {
    return {mk(x, z, v, seed), mk(x + v, z, v, seed + 1), mk(x, z + v, v, seed + 2), mk(x + v, z + v, v, seed + 3)};
}

#define CHECK(cond, ...) do { if (!(cond)) { fails++; printf("  FAIL %s:%d ", name, __LINE__); printf(__VA_ARGS__); printf("\n"); } } while (0)

// Expect `merged` 2x2 blocks among cs (given in list order); blocks[] = indices {A,B,C,D} of each expected merge.
static void run(const char* name, std::vector<Cell> cs, std::vector<std::array<int, 4>> blocks, bool flag = false,
                unsigned long long expNear = 0, unsigned long long expOvf = 0) {
    cases++; reset_t(); const int f0 = fails;
    auto [s1, s0] = build(cs, flag);
    std::vector<uint32_t> out = emit(s1, s0);
    const size_t expCmds = cs.size() - 3 * blocks.size();
    CHECK(out.size() == expCmds, "cmds %zu != %zu", out.size(), expCmds);
    CHECK(tally(T_MERGED) == blocks.size(), "merged %llu != %zu", tally(T_MERGED), blocks.size());
    CHECK(tally(T_DROP) == 3 * blocks.size(), "drop %llu != %zu", tally(T_DROP), 3 * blocks.size());
    CHECK(tally(T_UNM) == 0, "unm %llu", tally(T_UNM));
    CHECK(tally(T_NEAR) == expNear, "near %llu != %llu", tally(T_NEAR), expNear);
    CHECK(tally(T_OVF) == expOvf, "ovf %llu != %llu", tally(T_OVF), expOvf);
    // Every expected merge must appear as one command whose corners are the block's outer corners; every other
    // emitted command must be an unmerged cell, unchanged.
    std::vector<int> used(out.size(), 0);
    for (auto& b : blocks) {
        Corner want[4] = {cellCorner(cs[b[0]], 0), cellCorner(cs[b[1]], 1), cellCorner(cs[b[2]], 2), cellCorner(cs[b[3]], 3)};
        bool found = false;
        for (size_t i = 0; i < out.size() && !found; i++) { Corner k[4]; decode(out[i], k);
            if (k[0] == want[0] && k[1] == want[1] && k[2] == want[2] && k[3] == want[3]) { found = true; used[i] = 1; } }
        CHECK(found, "merged quad at (%d,%d) not found with the outer corners", cs[b[0]].x, cs[b[0]].z);
    }
    std::vector<int> inBlock(cs.size(), 0); for (auto& b : blocks) for (int i : b) inBlock[i] = 1;
    for (size_t j = 0; j < cs.size(); j++) { if (inBlock[j]) continue;
        Corner want[4]; for (int i = 0; i < 4; i++) want[i] = cellCorner(cs[j], i);
        bool found = false;
        for (size_t i = 0; i < out.size() && !found; i++) { if (used[i]) continue; Corner k[4]; decode(out[i], k);
            if (k[0] == want[0] && k[1] == want[1] && k[2] == want[2] && k[3] == want[3]) { found = true; used[i] = 1; } }
        CHECK(found, "unmerged cell %zu at (%d,%d) missing or altered", j, cs[j].x, cs[j].z);
    }
    printf("%s %s (cmds %zu, merged %llu)\n", fails != f0 ? "...." : "ok  ", name, out.size(), tally(T_MERGED));
}

int main() {
    rd = (uint8_t*)calloc(64u << 20, 1);
    uint32_t fc; memcpy(&fc, &FARCUT_V, 4); ww(FARCUT, fc);
    s7239_frac = 0.5f; g_rs64_s7239_on = 1;  // thr = 0.25 * 1000 = 250
    s7246_E = s7246_C = 1 << 30;  // s7246: the pre-flatness cases use random heights; gate off for them (tested below)
    run("basic 2x2", block(0, 0, 64, 1), {{0, 1, 2, 3}});
    { auto b = block(0, 0, 64, 5); std::vector<Cell> r = {b[3], b[1], b[0], b[2]};  // partners before the anchor
      run("partners before anchor", r, {{2, 1, 3, 0}}); }
    run("negative coords", block(-128, -256, 64, 9), {{0, 1, 2, 3}});
    run("negative odd-free (x=-64)", block(-64, 0, 64, 13), {});  // -64/64 = -1 odd -> no anchor
    run("odd-aligned x", block(64, 0, 64, 17), {});
    { auto b = block(0, 0, 64, 21); b[2].d2 = 100.f; run("one cell near", b, {}, false, 1); }
    // s7244: thr = frac^2 * (farthest node of this pass) = 0.25 * 1000 = 250
    { auto b = block(0, 0, 64, 25); for (auto& c : b) c.d2 = 1000.f; b[3].d2 = 250.f; run("at threshold (pass max)", b, {{0, 1, 2, 3}}); }
    { auto b = block(0, 0, 64, 26); for (auto& c : b) c.d2 = 1000.f; b[3].d2 = 249.f; run("below threshold (pass max)", b, {}, false, 1); }
    { auto b = block(0, 0, 64, 27), f = block(256, 0, 64, 28); for (auto& c : b) c.d2 = 200.f; for (auto& c : f) c.d2 = 1000.f;
      b.insert(b.end(), f.begin(), f.end()); run("near block vs far block, same pass", b, {{4, 5, 6, 7}}, false, 1); }
    { auto b = block(0, 0, 64, 31); for (auto& c : b) c.d2 = 7.f; run("whole pass close: frac of its own max merges", b, {{0, 1, 2, 3}}); }
    { auto b = block(0, 0, 64, 29); b[1].mat = 9; run("material mismatch", b, {}); }
    { auto b = block(0, 0, 64, 33); b[3].flat = false; run("non-flat partner", b, {}); }
    run("flagged group", block(0, 0, 64, 37), {}, true);
    { auto b = block(0, 0, 64, 41); b[1].yb = b[0].yb + 3000; run("height overflow", b, {}, false, 0, 1); }
    { std::vector<Cell> s; for (int i = 0; i < 4; i++) for (int j = 0; j < 2; j++) s.push_back(mk(i * 128, j * 128, 128, 50 + i * 2 + j));
      // 4x2 strip of V=128 cells -> anchors (0,0) and (256,0); list order is x-major, so indices are i*2+j
      run("4x2 strip", s, {{0, 2, 1, 3}, {4, 6, 5, 7}}); }
    { auto b = block(0, 0, 64, 61); b.push_back(mk(128, 0, 64, 70)); b.push_back(mk(128, 64, 64, 71)); run("block + 2 loose", b, {{0, 1, 2, 3}}); }
    { auto b = block(0, 0, 64, 81); b[2].v = 128; run("spacing mismatch", b, {}); }
    run("block at int16 x edge", block(32640, 0, 64, 91), {{0, 1, 2, 3}});  // partners at x 32704, outer corner 32768
    // s7242 stale guard: a dist2 fed in an earlier build pass must not drive a merge in a later one (miss + stale, no merge);
    // re-feeding all four in the new pass merges again (the generation bump does not break the normal flow).
    for (int refeed = 0; refeed < 2; refeed++) { cases++; reset_t(); const char* name = refeed ? "new pass, all refed" : "stale dist2 (earlier pass)"; const int f0 = fails;
      auto [s1, s0] = build(block(0, 0, 64, 111 + refeed), false); emit(s1, s0); reset_t();
      int n = 0; for (uint32_t e = s0; e; e = rw(e), n++) { if (!refeed && n == 3) continue; float d = 2000.f; uint32_t b; memcpy(&b, &d, 4); rs64_s7239_node(e, b); }
      auto out = emit(s1, s0);
      if (refeed) CHECK(out.size() == 1 && tally(T_MERGED) == 1 && tally(T_STALE) == 0 && tally(T_MISS) == 0, "cmds %zu merged %llu stale %llu", out.size(), tally(T_MERGED), tally(T_STALE));
      else CHECK(out.size() == 4 && tally(T_MERGED) == 0 && tally(T_MISS) == 1 && tally(T_STALE) == 1, "cmds %zu merged %llu miss %llu stale %llu", out.size(), tally(T_MERGED), tally(T_MISS), tally(T_STALE));
      printf("%s %s\n", fails != f0 ? "...." : "ok  ", name); }
    // TOG ph0: candidates counted, nothing merged.
    { g_tog_ph = 0; s7239_tg = 1; cases++; reset_t(); const char* name = "tog ph0"; const int f0 = fails;
      auto [s1, s0] = build(block(0, 0, 64, 99), false); auto out = emit(s1, s0);
      CHECK(out.size() == 4 && s7239_t[0][T_CAND] == 1 && s7239_t[0][T_ANC] == 0 && tally(T_MERGED) == 0, "ph0 cmds %zu cand %llu", out.size(), s7239_t[0][T_CAND]);
      printf("%s %s\n", fails != f0 ? "...." : "ok  ", name); g_tog_ph = 1; s7239_tg = 0; }
    // s7246 flatness gate (E = edge-midpoint T-junction gap, C = centre vs both diagonals; emitted units = 16 * height units).
    { auto planar = [](int x0, int z0, int v, int ybv) { std::vector<Cell> b = block(x0, z0, v, 3);
        for (int k = 0; k < 4; k++) { Cell& c = b[k]; c.yb = 100 + ybv * k; const int dx[4] = {0, 1, 0, 1}, dz[4] = {0, 0, 1, 1};
          for (int i = 0; i < 4; i++) { const int X = (c.x - x0) / v + dx[i], Z = (c.z - z0) / v + dz[i]; c.h[i] = 3 * X - 2 * Z + 5 - c.yb + 100; } }
        return b; };
      s7246_E = s7246_C = 0;
      { const char* name = "flat: planar block merges at E=0"; run(name, planar(0, 0, 64, 0), {{0, 1, 2, 3}});
        CHECK(tally(T_FLATE) == 0 && tally(T_FLATC) == 0 && tally(T_SHMIS) == 0 && tally(T_DH0) == 1, "flatrej %llu ctr %llu shmis %llu dh0 %llu", tally(T_FLATE), tally(T_FLATC), tally(T_SHMIS), tally(T_DH0)); }
      { const char* name = "flat: planar, per-cell ybase rebased"; run(name, planar(0, 0, 64, 7), {{0, 1, 2, 3}});
        CHECK(tally(T_SHMIS) == 0 && tally(T_DH0) == 1, "shmis %llu dh0 %llu", tally(T_SHMIS), tally(T_DH0)); }
      { const char* name = "flat: raised edge midpoint rejects at E=0"; auto b = planar(0, 0, 64, 0); b[0].h[1] += 1; b[1].h[0] += 1;  // A4 == B0, +1 unit
        run(name, b, {}); CHECK(tally(T_FLATE) == 1 && tally(T_DH2) == 1, "flatrej %llu dh2 %llu (dev 16)", tally(T_FLATE), tally(T_DH2)); }
      { const char* name = "flat: same block merges at E=16"; s7246_E = 16; auto b = planar(0, 0, 64, 0); b[0].h[1] += 1; b[1].h[0] += 1;
        run(name, b, {{0, 1, 2, 3}}); CHECK(tally(T_FLATE) == 0, "flatrej %llu", tally(T_FLATE)); s7246_E = 0; }
      { const char* name = "flat: raised centre rejects via C"; s7246_E = 1 << 30; s7246_C = 0; auto b = planar(0, 0, 64, 0);
        b[0].h[3] += 2; b[1].h[2] += 2; b[2].h[1] += 2; b[3].h[0] += 2;
        run(name, b, {}); CHECK(tally(T_FLATC) == 1 && tally(T_FLATE) == 0, "ctrrej %llu flatrej %llu", tally(T_FLATC), tally(T_FLATE)); s7246_E = s7246_C = 0; }
      { const char* name = "flat: shared-corner mismatch counted"; auto b = planar(0, 0, 64, 0); b[1].h[0] += 4;  // B0 != A4, A's own edge still planar
        run(name, b, {{0, 1, 2, 3}}); CHECK(tally(T_SHMIS) == 1, "shmis %llu", tally(T_SHMIS)); }
      { const char* name = "flat: random terrain rejects at E=0 (negative control)"; run(name, block(0, 0, 64, 1), {});
        CHECK(tally(T_FLATE) + tally(T_FLATC) == 1 && tally(T_DH0) == 0, "rej %llu dh0 %llu", tally(T_FLATE) + tally(T_FLATC), tally(T_DH0)); }
      s7246_E = s7246_C = 1 << 30; }
    // Positive control for the checker itself: corrupt one rewrite and the corner check must fail.
    { int before = fails; cases++; reset_t(); auto b = block(0, 0, 64, 7);
      auto [s1, s0] = build(b, false); auto out = emit(s1, s0); ww(out[0] + 0x10, 0xDEADBEEFu);
      Corner k[4]; decode(out[0], k); const bool caught = !(k[1] == cellCorner(b[1], 1));
      if (!caught) { fails++; printf("  FAIL checker control: corrupted colour not detected\n"); }
      else printf("ok   checker control (a corrupted corner is detected)\n"); (void)before; }
    printf("s7241 merge test: %d cases, %d failures\n", cases, fails);
    return fails ? 1 : 0;
}
