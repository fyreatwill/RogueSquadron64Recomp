// G6c (s7623): draw-only stand-ins for level objects and ground units the game has not spawned yet, so they show at draw distance > 1
// instead of popping in. Port of upstream (MikeSemicolonD) src/game/static_standins.cpp (read via `git show origin/main:...`, never
// merged): a model instance and a 0x50-byte prop state block per DAT item, built in a host region the game never allocates, go into
// the game's own visibility bucket (addNpcToVisibilityBucket 0x80057C8C), so the game's traverseSceneGraphRecursive copies the
// matrices into its DL pool and our LLE F5 ucode draws them like any spawned prop. Nothing the game reads is written.
// Differences from upstream (docs/G6C-STANDINS-PLAN.md):
//  - region: the top 1 MB of the dd>1 spill arena, 0x81700000..0x81800000 (upstream 0x80A5C000 is our guest heap / DL pool). The spill
//    arena is capped to 7 MB while stand-ins are on (upstream_compat.cpp rs64_s7326_spill_cap; dd8 peak 0x688B50, s7327). Only CPU code
//    reads the region: the node matrix is converted into *0x8011DC5C (DL pool) by convertMat3x4ToN64Mtx from a stack copy.
//  - no save-state snapshot / replay mark, and probe droids (subtype 0x0E) are dropped (they need upstream's selectMeshLod hooks).
// Called from runInMissionFrame at L_800FAC68 (tools/apply_s7623_standins.py), after the render broadcast, $s2 = the message (+0 view).
// ROGUESQ_STANDINS=1 (on), =tog (on in even mach seconds only: same-run A/B for step 3); off unless ROGUESQ_DRAW_DISTANCE > 1.
// ROGUESQ_STANDINS_LOG=1: one `[standins-s]` line per second (submits, candidates, skip reasons). Rebuild always logs `[standins]`.
#include "recomp.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <initializer_list>
#include <vector>

extern "C" recomp_func_t* get_function(int32_t vram);
extern "C" uint32_t rs64_ram_top;

namespace {

inline uint32_t rw(const uint8_t* r, uint32_t a) { uint32_t v = 0; for (uint32_t i = 0; i < 4; ++i) v = (v << 8) | r[(a + i - 0x80000000u) ^ 3]; return v; }
inline void ww(uint8_t* r, uint32_t a, uint32_t v) { for (uint32_t i = 0; i < 4; ++i) r[(a + i - 0x80000000u) ^ 3] = (uint8_t)(v >> (24 - 8 * i)); }
inline float rf(const uint8_t* r, uint32_t a) { const uint32_t b = rw(r, a); float f; std::memcpy(&f, &b, 4); return f; }
inline void wf(uint8_t* r, uint32_t a, float f) { uint32_t b; std::memcpy(&b, &f, 4); ww(r, a, b); }
inline uint16_t rh(const uint8_t* r, uint32_t a) { return (uint16_t)((r[(a - 0x80000000u) ^ 3] << 8) | r[(a + 1 - 0x80000000u) ^ 3]); }
inline uint8_t rb(const uint8_t* r, uint32_t a) { return r[(a - 0x80000000u) ^ 3]; }
inline void wh(uint8_t* r, uint32_t a, uint16_t v) { r[(a - 0x80000000u) ^ 3] = (uint8_t)(v >> 8); r[(a + 1 - 0x80000000u) ^ 3] = (uint8_t)v; }
inline bool guest(uint32_t a) { return a >= 0x80000000u && a < 0x81700000u; }  // guest heap, DL pool and spill arena; never our own region

struct Call { uint32_t v0; float f0; };

// Calls the recompiled function at vram with a0-a3 = args, stack words at sp+0x10.., below the hook site's frame; ctx is restored after.
Call mips_call(uint8_t* rdram, recomp_context* ctx, uint32_t vram, std::initializer_list<uint32_t> args, std::initializer_list<uint32_t> stack = {},
               float f12 = 0.0f, float f14 = 0.0f) {
    const recomp_context saved = *ctx;
    ctx->r29 = (gpr)(int32_t)((uint32_t)ctx->r29 - 0x40);
    gpr* regs[4] = { &ctx->r4, &ctx->r5, &ctx->r6, &ctx->r7 };
    uint32_t i = 0;
    for (uint32_t a : args) { if (i < 4) *regs[i] = (gpr)(int32_t)a; ++i; }
    i = 0;
    for (uint32_t s : stack) { if (i < 12) ww(rdram, (uint32_t)ctx->r29 + 0x10u + 4u * i, s); ++i; }
    ctx->f12.fl = f12;
    ctx->f14.fl = f14;
    get_function((int32_t)vram)(rdram, ctx);
    const Call out{ (uint32_t)ctx->r2, ctx->f0.fl };
    *ctx = saved;
    return out;
}

constexpr uint32_t kDatFile = 0x801375D8u;
constexpr uint32_t kModelHash = 0x801394B0u;
constexpr uint32_t kModelEntries = 0x80139020u;
constexpr uint32_t kDifficulty = 0x80137CE4u;
constexpr uint32_t kComposeEuler = 0x80059D78u;        // composeEulerRotationXYZ
constexpr uint32_t kAddToBucket = 0x80057C8Cu;         // addNpcToVisibilityBucket
constexpr uint32_t kRootMatrix = 0x80059C24u;          // mat34CrossRowsAndCopyPosPtr
constexpr uint32_t kUniformRootMatrix = 0x80059B50u;   // mat34CrossRowsAndCopyPos
constexpr uint32_t kConditionMet = 0x80065828u;        // isDatItemConditionMet
constexpr uint32_t kGridEntries = 0x80136FCCu;
constexpr uint32_t kCutsceneFlag = 0x80130B39u;
constexpr uint32_t kDatItemByName = 0x80047B48u;       // getLevelDatItemByName
constexpr uint32_t kTerrainHeight = 0x80068180u;       // sampleTerrainSurfaceAtWorldXz
constexpr uint32_t kRegion = 0x81700000u;
constexpr uint32_t kRegionEnd = 0x81800000u;
constexpr uint32_t kStateSize = 0x50u;
constexpr uint16_t kSubProbeDroid = 0x0Eu;

struct Standin { uint32_t item, state, inst, scale; };

uint32_t s_dat = 0;
std::vector<Standin> s_standins;

bool names_in_item(uint16_t sub) {
    switch (sub) { case 0x14: case 0x33: case 0x36: case 0x44: case 0x46: case 0x4A: case 0x4B: case 0x4F: return true; default: return false; }
}

// Subtypes whose handler picks the model itself (rodata strings in the handlers; upstream table, addresses verified identical s7621).
uint32_t handler_model_name(uint16_t sub) {
    switch (sub) {
    case 0x0D: return 0x800A6A40u; case 0x1E: return 0x800A6A4Cu; case 0x28: return 0x800A6A58u; case 0x41: return 0x800A6A64u;
    case 0x42: return 0x800A6A70u; case 0x0F: return 0x800A6ED0u; case 0x1F: return 0x800A70E0u;
    case 0x25: return 0x800A76F4u; case 0x2A: return 0x800A7D38u; case 0x32: return 0x8003D518u; case 0x47: return 0x800A874Cu;
    case 0x24: return 0x800A7480u; case 0x2C: return 0x800A748Cu; case 0x48: return 0x800A7498u; case 0x4D: return 0x800A74A4u;
    case 0x2B: return 0x800A7E60u; case 0x2D: return 0x800A7E70u; case 0x2E: return 0x800A7E7Cu; case 0x0C: return 0x800A7C00u;
    case 0x12: return 0x800A7BE0u; case 0x13: return 0x800A7BD4u; case 0x29: return 0x800A7BECu; case 0x43: return 0x800A7BF4u;
    case 0x2F: return 0x800A80C0u; case 0x30: return 0x800A80CCu; case 0x31: return 0x800A80D8u; case 0x34: return 0x800A80E8u;
    case 0x35: return 0x800A80F4u; case 0x4C: return 0x800A8890u;
    default: return 0;  // 0x0E probe droid dropped (needs selectMeshLod + upstream's gameplay-protection hooks)
    }
}

// walkMeshdef0List 0x80056EB0's lookup: byte sum mod 25 indexes u16 chains of 12-byte entries, +4 the model, names compared up to 16 bytes.
uint32_t find_model(const uint8_t* rdram, uint32_t name) {
    uint32_t sum = 0;
    for (uint32_t i = 0; i < 64 && rb(rdram, name + i) != 0; ++i) sum += rb(rdram, name + i);
    uint32_t idx = rh(rdram, kModelHash + (sum % 25u) * 2u);
    for (int hops = 0; idx != 0xFFFFu && hops < 1024; ++hops) {
        const uint32_t entry = kModelEntries + idx * 12u;
        const uint32_t model = rw(rdram, entry + 4u);
        if (!guest(model)) return 0;
        bool same = true;
        for (uint32_t i = 0; i < 16; ++i) {
            const uint8_t a = rb(rdram, name + i);
            if (a != rb(rdram, model + i)) { same = false; break; }
            if (a == 0) break;
        }
        if (same) return model;
        idx = rh(rdram, entry);
    }
    return 0;
}

// walkMeshdef0List's instance: 0xC header (+0 model), nodes of 0x4C (four child links, +0x10 leaf list, +0x14/+0x18, the 0x30-byte matrix
// at +0x1C copied from the model's node), then leaves of 0x5C chained per node. The model's use count (+0x3A) is left alone.
uint32_t build_instance(uint8_t* rdram, uint32_t model, uint32_t at) {
    const uint32_t table = rw(rdram, model + 0x14u);
    if (!guest(table) || !guest(rw(rdram, model + 0x18u))) return 0;
    const uint32_t nodes = rh(rdram, table);
    const uint32_t leaves = rh(rdram, table + 2u);
    const uint32_t size = 0xCu + nodes * 0x4Cu + leaves * 0x5Cu;
    if (nodes == 0 || at + size > kRegionEnd) return 0;
    for (uint32_t i = 0; i < size; i += 4) ww(rdram, at + i, 0);
    ww(rdram, at, model);
    const uint32_t node0 = at + 0xCu;
    uint32_t leaf = node0 + nodes * 0x4Cu;
    const uint32_t leaf_end = leaf + leaves * 0x5Cu;
    for (uint32_t i = 0; i < leaves; ++i) ww(rdram, leaf + i * 0x5Cu + 0xCu, 4);
    uint32_t lists = rw(rdram, model + 0x18u) + 4u;
    for (uint32_t n = 0; n < nodes; ++n) {
        const uint32_t node = node0 + n * 0x4Cu;
        const uint32_t links = rw(rdram, table + 4u + n * 8u);
        const uint32_t src = rw(rdram, table + 8u + n * 8u);
        if (!guest(src)) return 0;
        static constexpr int kShift[4] = { 24, 18, 12, 6 };
        for (int k = 0; k < 4; ++k) {
            const uint32_t child = (links >> kShift[k]) & 0x3Fu;
            ww(rdram, node + 4u * k, (child && child <= nodes) ? node0 + (child - 1u) * 0x4Cu : 0u);
        }
        ww(rdram, node + 0x14u, rw(rdram, src + 0x14u));
        ww(rdram, node + 0x18u, rw(rdram, src + 0x18u));
        for (uint32_t i = 0; i < 0x30u; i += 4) ww(rdram, node + 0x1Cu + i, rw(rdram, src + 0x1Cu + i));
        if (rw(rdram, lists) == 0) { ww(rdram, node + 0x10u, 0); lists += 4u; continue; }
        ww(rdram, node + 0x10u, leaf);
        uint32_t prev = 0;
        while (rw(rdram, lists) != 0) {
            if (leaf + 0x5Cu > leaf_end) return 0;  // model's list table disagrees with its leaf count
            const bool more = rw(rdram, lists + 4u) != 0;
            ww(rdram, leaf, more ? leaf + 0x5Cu : 0u);
            ww(rdram, leaf + 4u, prev);
            ww(rdram, leaf + 8u, rw(rdram, lists));
            ww(rdram, leaf + 0xCu, 4);
            prev = leaf;
            leaf += 0x5Cu;
            lists += 4u;
        }
        lists += 4u;
    }
    return size;
}

// A unit with a path (name at item + item[+0x8C], "-" for none) spawns on it (func_800F947C): the spline starts at the path's second point
// facing along (p2 - p0). Walkers stand on the terrain, ground transports keep the DAT's height above it.
void place_on_path(uint8_t* rdram, recomp_context* ctx, uint32_t item, uint32_t state) {
    const uint32_t offset = rw(rdram, item + 0x8Cu);
    const uint32_t name = item + offset;
    if (offset < 0x90u || offset >= 0x400u || rb(rdram, name) == '-' || rb(rdram, name) == 0) return;
    const uint32_t path = mips_call(rdram, ctx, kDatItemByName, { name }).v0;
    if (!guest(path) || rh(rdram, path) != 3 || rw(rdram, path + 0x1Cu) < 3) return;
    const uint32_t pts = rw(rdram, path + 0x20u);
    if (!guest(pts)) return;
    const float x = rf(rdram, path + 0x10u) + rf(rdram, pts + 12u);
    const float y = rf(rdram, path + 0x14u) + rf(rdram, pts + 16u);
    const float z = rf(rdram, path + 0x18u) + rf(rdram, pts + 20u);
    const float dx = rf(rdram, pts + 24u) - rf(rdram, pts);
    const float dz = rf(rdram, pts + 32u) - rf(rdram, pts + 8u);
    const float len = std::sqrt(dx * dx + dz * dz);
    const uint16_t sub = rh(rdram, item);
    const bool walker = sub == 0x0F || sub == 0x1F || sub == 0x47;
    const bool transport = sub == 0x2B || sub == 0x2D || sub == 0x2E;
    const float ground = walker || transport ? mips_call(rdram, ctx, kTerrainHeight, { 0, 0, 0, 0 }, {}, x, z).f0 : 0.0f;
    const float dat_ground = transport ? mips_call(rdram, ctx, kTerrainHeight, { 0, 0, 0, 0 }, {}, rf(rdram, item + 0x10u), rf(rdram, item + 0x18u)).f0 : 0.0f;
    wf(rdram, state, x);
    wf(rdram, state + 4u, walker ? ground : (transport ? rf(rdram, item + 0x14u) + ground - dat_ground : y));
    wf(rdram, state + 8u, z);
    if (len > 1e-4f) {
        wf(rdram, state + 0xCu, dx / len); wf(rdram, state + 0x10u, 0.0f); wf(rdram, state + 0x14u, dz / len);
        wf(rdram, state + 0x18u, 0.0f); wf(rdram, state + 0x1Cu, 1.0f); wf(rdram, state + 0x20u, 0.0f);
    }
}

// The prop handler's spawn (message 1): position in row 0, Euler rotation, the instance and the item, and the cull radius = model radius
// (+0x44) times the largest scale component (instance flag 0x400 when y is largest, 0x800 when z is).
void build_state(uint8_t* rdram, recomp_context* ctx, uint32_t item, uint32_t state, uint32_t inst, uint32_t model, uint32_t* scale) {
    for (uint32_t i = 0; i < kStateSize; i += 4) ww(rdram, state + i, 0);
    for (uint32_t i = 0; i < 12; i += 4) ww(rdram, state + i, rw(rdram, item + 0x10u + i));
    mips_call(rdram, ctx, kComposeEuler, { state, rw(rdram, item + 0x1Cu), rw(rdram, item + 0x20u), rw(rdram, item + 0x24u) });
    for (uint32_t i = 0x24u; i < 0x30u; i += 4) ww(rdram, state + i, 0);
    place_on_path(rdram, ctx, item, state);
    ww(rdram, state + 0x30u, inst);
    ww(rdram, state + 0x34u, item);
    const uint16_t sub = rh(rdram, item);
    // Walkers (AT-AT, AT-ST, AT-PT) and shuttles draw at a uniform scale of item +0x28 over the model's +0x34.
    if (sub == 0x0F || sub == 0x1F || sub == 0x47 || sub == 0x24 || sub == 0x2C || sub == 0x48 || sub == 0x4D) {
        const float ws = rf(rdram, item + 0x28u) / rf(rdram, model + 0x34u);
        const float r = rf(rdram, model + 0x44u) * ws;
        uint32_t bits;
        std::memcpy(&bits, &ws, 4);
        std::memcpy(scale, &r, 4);
        mips_call(rdram, ctx, kUniformRootMatrix, { inst + 0x28u, state, bits });
        return;
    }
    const float sx = rf(rdram, item + 0x28u), sy = rf(rdram, item + 0x2Cu), sz = rf(rdram, item + 0x30u);
    float s = sx;
    uint32_t flags = 0;
    if (sx < sy) { s = sy; flags = 0x400u; if (!(sz < sy)) { s = sz; flags = 0x800u; } }
    else if (sx < sz) { s = sz; flags = 0x800u; }
    wh(rdram, inst + 8u, (uint16_t)(rh(rdram, inst + 8u) | flags));
    const float r = rf(rdram, model + 0x44u) * s;
    std::memcpy(scale, &r, 4);
    ww(rdram, state + 0x38u, *scale);
    mips_call(rdram, ctx, kRootMatrix, { inst + 0x28u, state, item + 0x28u });
}

struct Tally { uint32_t frames, submits, cand, spawned, unlinked, dead, cond; };
Tally s_t{};

void rebuild(uint8_t* rdram, recomp_context* ctx, uint32_t dat) {
    s_standins.clear();
    s_dat = dat;
    const uint32_t count = rw(rdram, dat);
    const uint32_t list = rw(rdram, dat + 4u);
    uint32_t at = kRegion, nomodel = 0, noname = 0, probe = 0, full = 0;
    for (uint32_t i = 0; guest(list) && i < count && i < 4096; ++i) {
        const uint32_t item = rw(rdram, list + i * 4u);
        if (!guest(item)) continue;
        const uint16_t sub = rh(rdram, item);
        if (sub == kSubProbeDroid) { ++probe; continue; }
        const uint32_t name = names_in_item(sub) ? rw(rdram, item + 0x5Cu) : handler_model_name(sub);
        if (!guest(name)) { ++noname; continue; }
        const uint32_t model = find_model(rdram, name);
        if (model == 0) { ++nomodel; continue; }
        const uint32_t state = at;
        const uint32_t inst = at + kStateSize;
        const uint32_t size = build_instance(rdram, model, inst);
        if (size == 0) { ++full; if (inst + 0x1000u > kRegionEnd) break; continue; }
        Standin s{ item, state, inst, 0 };
        build_state(rdram, ctx, item, state, inst, model, &s.scale);
        s_standins.push_back(s);
        at = (inst + size + 15u) & ~15u;
    }
    std::fprintf(stderr, "[standins] %zu objects, %u KB (dat %08X items %u: no-name %u no-model %u probe-dropped %u build-fail %u) level %u\n",
                 s_standins.size(), (at - kRegion) / 1024u, dat, count, noname, nomodel, probe, full, rw(rdram, 0x80130B70u));
}

int mode() {  // 0 off, 1 on, 2 tog
    static const int m = [] {
        const char* e = std::getenv("ROGUESQ_STANDINS");
        const char* d = std::getenv("ROGUESQ_DRAW_DISTANCE");
        int v = (e && *e && *e != '0') ? (std::strcmp(e, "tog") == 0 ? 2 : 1) : 0;
        const double dd = (d && *d) ? std::atof(d) : 1.0;
        if (v && !(dd > 1.0)) { std::fprintf(stderr, "[standins] ROGUESQ_STANDINS set but draw distance %.2f <= 1: off (retail)\n", dd); v = 0; }
        if (v) std::fprintf(stderr, "[standins] on mode=%s dd=%.2f region %08X..%08X\n", v == 2 ? "tog" : "on", dd, kRegion, kRegionEnd);
        return v;
    }();
    return m;
}

}  // namespace

// Read by rs64_s7326_spill_cap (upstream_compat.cpp): the spill arena gives up its top 1 MB to the stand-in region while this is on.
extern "C" int rs64_standins_on(void) { return mode() != 0; }

// runInMissionFrame 0x800FAC68 (both the broadcast path and the beq skip path), $s2 = the render message (+0 the view).
extern "C" void rs64_standins_submit(uint8_t* rdram, recomp_context* ctx) {
    const int m = mode();
    if (!m) return;
    static int s_region_ok = -1;
    if (s_region_ok < 0) {
        s_region_ok = rs64_ram_top >= kRegionEnd ? 1 : 0;
        if (!s_region_ok) std::fprintf(stderr, "[standins] DISABLED: rs64_ram_top %08X < region end %08X (needs the dd>1 SPILL_HI + RAMTOP 24 bundle)\n", rs64_ram_top, kRegionEnd);
    }
    if (!s_region_ok) return;
    const uint32_t dat = rw(rdram, kDatFile);
    if (!guest(dat)) return;
    static uint32_t s_level = ~0u, s_frame = 0;
    const uint32_t level = rw(rdram, 0x80130B70u);
    const uint32_t frame = rw(rdram, 0x8013889Cu);
    if (dat != s_dat || level != s_level || frame < s_frame) { s_level = level; rebuild(rdram, ctx, dat); }
    s_frame = frame;

    static const bool s_log = [] { const char* e = std::getenv("ROGUESQ_STANDINS_LOG"); return e && *e && *e != '0'; }();
    const double now = std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
    static double s_t0 = std::floor(now);  // windows on whole seconds, so a tog window is all-on or all-off
    if (s_log && now - s_t0 >= 1.0) {
        std::fprintf(stderr, "[standins-s] frames=%u submits=%u cand=%u skip spawned=%u unlinked=%u dead=%u cond=%u objects=%zu tog=%d\n",
                     s_t.frames, s_t.submits, s_t.cand, s_t.spawned, s_t.unlinked, s_t.dead, s_t.cond, s_standins.size(),
                     m == 2 ? (int)(((long long)s_t0) & 1) ^ 1 : -1);  // tog=1: the window just logged was an on second
        s_t = Tally{};
        s_t0 = std::floor(now);
    }
    ++s_t.frames;
    if (m == 2 && (((long long)now) & 1)) return;  // tog: odd seconds are the off arm

    const uint32_t view = rw(rdram, (uint32_t)ctx->r18);
    const uint32_t diff = rw(rdram, kDifficulty) & 3u;
    // Items the game still spawns on approach are linked in a DAT grid cell (updateActiveGridCellState moves a spawned item's entry to
    // the free list): 12-byte entries, +2 next, +4 type (3 = item), +8 the item.
    static std::vector<uint32_t> s_linked;
    const uint32_t cells = rw(rdram, kDatFile + 0x14u) * rw(rdram, kDatFile + 0x18u);
    const uint32_t heads = rw(rdram, kDatFile + 0x1Cu);
    const uint32_t entries = rw(rdram, kGridEntries);
    s_linked.clear();
    if (guest(heads) && guest(entries)) {
        for (uint32_t c = 0; c < cells && c < 0x10000u; ++c) {
            uint32_t idx = rh(rdram, heads + c * 2u);
            for (int hops = 0; idx != 0xFFFFu && hops < 4096; ++hops) {
                const uint32_t e = entries + idx * 12u;
                if (rh(rdram, e + 4u) == 3) s_linked.push_back(rw(rdram, e + 8u));
                idx = rh(rdram, e + 2u);
            }
        }
    }
    std::sort(s_linked.begin(), s_linked.end());
    const bool cutscene = rb(rdram, kCutsceneFlag) != 0;
    for (const Standin& s : s_standins) {
        ++s_t.cand;
        if (rh(rdram, s.item + 6u) != 0xFFFFu) { ++s_t.spawned; continue; }
        if (!std::binary_search(s_linked.begin(), s_linked.end(), s.item)) { ++s_t.unlinked; continue; }
        if ((int32_t)rw(rdram, s.item + 0x6Cu + diff * 4u) <= 0) { ++s_t.dead; continue; }
        if (!cutscene && mips_call(rdram, ctx, kConditionMet, { s.item }).v0 == 0) { ++s_t.cond; continue; }
        mips_call(rdram, ctx, kAddToBucket, { view, s.inst, s.state, s.scale });
        ++s_t.submits;
    }
}
