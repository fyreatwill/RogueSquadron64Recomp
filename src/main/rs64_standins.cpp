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
#include <unordered_map>
#include <vector>
#include <set>
#include "rs64_apf.h"  // s7652: s7359 class AJ bounded append for the [standins-*] log rows

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

struct Standin {
    uint32_t item, state, inst, scale; double first_add = -1.0, last_add = -1.0; bool spawn_logged = false;
    // s7689: submits / accepted adds split by submit-call parity (s_calls & 1), printed on the [standins-spawn] line (par=try0/add0,try1/add1)
    uint32_t par_try[2] = {}, par_add[2] = {};
    // s7672 handoff (ROGUESQ_STANDINS_LOG=1): frame ids are our submit-call count (one per mission frame)
    int64_t last_si = -1, spawn_f = -1, real_call = -1, real_add = -1, real_last = -1; uint32_t overlap = 0, real_frames = 0, held = 0, held_ok = 0;
    // s7674: held culled frames by our own view-test exit class, and the real object's rejected calls while we wait for its first accept
    uint32_t si_cls[4] = {}, re_cls[4] = {}, re_rej = 0;
    uint32_t idx = 0; uint16_t sub = 0; int end_reason = -1, prev_reason = -1; float dpos = -1.0f; bool ho_logged = false, by_pos = false, by_rs = false;
    // s7675 ghost probe: nearest real (non-self) bucket call to this held stand-in since the last [s7675-gh] line
    float nd2 = -1.0f; uint32_t n_state = 0, n_item = 0, n_calls = 0;
    // s7675b: camera-space distance (view test) of our held call (min over the window / the whole hold) and of the real object's first call
    double si_dmin = -1.0, si_dall = -1.0, fr_d = -1.0, spawn_d = -1.0;
    // s7679: min camera-space distance over ACCEPTED stand-in draws (any phase), and the add count, for the per-generation life table
    double add_dmin = -1.0; uint32_t adds = 0;
    bool released = false;  // s7679 near release: hold dropped because the stand-in came nearer than any real object's first draw
    // s7690: calls whose instance slice group (inst+8 & 0x180) would reuse the cached cull bit this game frame; fixed = regrouped
    uint32_t par_mism = 0, par_fix = 0; bool par_logged = false;
};

uint32_t s_dat = 0;
uint32_t s_par_mism = 0, s_par_fix = 0;  // s7690 run totals
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

struct Tally { uint32_t frames, submits, cand, spawned, unlinked, dead, cond, added, onframes, faron, cutframes, cutadded; };  // s7696: cut* = frames / adds with the cutscene byte 0x80130B39 set
Tally s_t{};

// s7672: addNpcToVisibilityBucket returns (tools/apply_s7672_bucket_handoff.py). rs64_bk_on is set by the submit hook (stand-ins active, dd>1 only); our own
// call is excluded by rs64_bk_self. A real call is matched to a stand-in by state+0x34 (the prop handler stores the item there) or,
// failing that, by its state row-0 position within 2 units of the stand-in's. Reasons: 0 added, 1 culled, 2 spawned, 3 unlinked,
// 4 dead, 5 cond.
int64_t s_bk_frame = 0;
int rs64_bk_self = 0;
bool s_bk_log = false;
std::unordered_map<uint32_t, size_t> s_bk_by_item;
std::vector<size_t> s_gh_idx;  // s7675: held stand-ins >= 30 frames past spawn, probed against every real bucket call
size_t s_bk_gen_size = ~size_t(0);
// s7677: the item->index map was keyed on s_standins.size(), so a rebuild with the same object count (same level re-entered after
// a mission abort, items at new addresses) kept the previous mission's item keys. s_gen counts rebuilds; ROGUESQ_S7677_GEN=0 restores
// the size-only key (same-build control).
uint32_t s_gen = 0, s_bk_gen = ~0u, s_bk_wrong = 0;
uint32_t s_bk_calls = 0, s_bk_item_hits = 0, s_bk_pos_hits = 0, s_bk_rs_hits = 0;
uint32_t s_bk_item_lo = ~0u, s_bk_item_hi = 0, s_bk_pos_rej = 0;  // s7685
const char* const kReason[] = { "added", "culled", "spawned", "unlinked", "dead", "cond" };
void ho_log(Standin& s, const char* why) {
    if (s.ho_logged) return;
    s.ho_logged = true;
    const int64_t gap = (s.real_add >= 0 && s.last_si >= 0) ? s.real_add - s.last_si - 1 : -9999;
    std::fprintf(stderr, "[s7672-ho] item %08X sub %04X why=%s spawn_f=%lld last_si=%lld real_call=%lld real_add=%lld gap=%lld overlap=%u "
                 "real_frames30=%u end=%s dpos=%.2f match=%s si_before_spawn=%lld odd=%u held=%u held_ok=%u si_off=%u si_far=%u si_novt=%u si_vtpass=%u re_rej=%u re_off=%u re_far=%u re_novt=%u re_vtpass=%u\n",
                 s.item, (unsigned)s.sub, why, (long long)s.spawn_f, (long long)s.last_si, (long long)s.real_call, (long long)s.real_add, (long long)gap,
                 s.overlap, s.real_frames, s.end_reason >= 0 ? kReason[s.end_reason] : "none", (double)s.dpos, s.by_pos ? "pos" : (s.by_rs ? "rsitem" : "item"),
                 (long long)(s.spawn_f >= 0 && s.last_si >= 0 ? s.spawn_f - s.last_si : -9999), s.idx & 1u, s.held, s.held_ok,
                 s.si_cls[0], s.si_cls[1], s.si_cls[2], s.si_cls[3], s.re_rej, s.re_cls[0], s.re_cls[1], s.re_cls[2], s.re_cls[3]);
}
}  // namespace

extern "C" int rs64_bk_on = 0;
extern "C" double rs64_vt_lastd;  // s7675b, defined with the view-test hooks below
// s7674 (tools/apply_s7674_bucket_vt.py): last view-test exit PC / v0 and call count of the current addNpcToVisibilityBucket call.
extern "C" uint32_t rs64_bk_vt_n = 0, rs64_bk_vt_pc = 0, rs64_bk_vt_v0 = 0;
// class: 0 off-screen (camera box, behind, side planes, point near), 1 far, 2 no view test ran, 3 view test passed (bucket rejected after)
static int vt_class() {
    if (rs64_bk_vt_n == 0) return 2;
    if (rs64_bk_vt_v0 == 1u) return 3;
    switch (rs64_bk_vt_pc) { case 0x8001DDA8u: case 0x8001E080u: return 1; default: return 0; }
}
// only_sub != 0 (s7681 shield): match only stand-ins of that subtype, so a report from a non-prop path cannot hand off a neighbour.
static void bk_ret_impl(uint8_t* rdram, uint32_t state, uint32_t v0, uint16_t only_sub);
extern "C" void rs64_bk_ret(uint8_t* rdram, uint32_t state, uint32_t v0) { bk_ret_impl(rdram, state, v0, 0); }
static void bk_ret_impl(uint8_t* rdram, uint32_t state, uint32_t v0, uint16_t only_sub) {
    if (rs64_bk_self || !guest(state)) return;
    ++s_bk_calls;
    static const bool s_genfix = [] { const char* e = std::getenv("ROGUESQ_S7677_GEN"); return !(e && *e == '0'); }();
    // s7678 positive control: ROGUESQ_S7678_STALE=1 keeps the first build's map for the whole run (a planted stale key), so after a
    // real level change item_hits must collapse to ~0 (the new level's items are not in the old map); default off = unchanged.
    static const bool s_stale7678 = [] { const char* e = std::getenv("ROGUESQ_S7678_STALE"); return e && *e == '1'; }();
    if ((!s_stale7678 || s_bk_gen == ~0u) && (s_bk_gen_size != s_standins.size() || (s_genfix && s_bk_gen != s_gen))) {
        s_bk_by_item.clear();
        for (size_t i = 0; i < s_standins.size(); ++i) s_bk_by_item[s_standins[i].item] = i;
        s_bk_gen_size = s_standins.size();
        s_bk_gen = s_gen;
        s_bk_item_lo = ~0u; s_bk_item_hi = 0;
        for (const Standin& q : s_standins) { if (q.item < s_bk_item_lo) s_bk_item_lo = q.item; if (q.item > s_bk_item_hi) s_bk_item_hi = q.item; }
    }
    Standin* hit = nullptr;
    const uint32_t it = rw(rdram, state + 0x34u);
    if (s_bk_log) {
        const float gx = rf(rdram, state), gy = rf(rdram, state + 4u), gz = rf(rdram, state + 8u);
        for (size_t gi : s_gh_idx) {
            if (gi >= s_standins.size()) continue;
            Standin& g = s_standins[gi];
            ++g.n_calls;
            const float dx = rf(rdram, g.state) - gx, dy = rf(rdram, g.state + 4u) - gy, dz = rf(rdram, g.state + 8u) - gz;
            const float d2 = dx * dx + dy * dy + dz * dz;
            if (g.nd2 < 0 || d2 < g.nd2) { g.nd2 = d2; g.n_state = state; g.n_item = it; }
        }
    }
    auto f = s_bk_by_item.find(it);
    if (f != s_bk_by_item.end() && (!only_sub || s_standins[f->second].sub == only_sub)) { hit = &s_standins[f->second]; ++s_bk_item_hits; if (hit->item != it) ++s_bk_wrong; }  // s7677: wrong = stale key
    // s7684: handleRayShieldedNpcDestroy (0x800E4070; subs 0x33/0x36/0x44/0x4B/0x4F) keeps the DAT item at blk+0x34 (init 0x800E40F8)
    // but passes state = blk+4 to addNpcToVisibilityBucket (render 0x800E4320), so state+0x34 is its radius (0x800E41D8) and the item
    // is at state+0x30. Key this class there instead of the 2-unit position fallback (which can hand off a neighbour, s7681).
    // ROGUESQ_S7684_RSKEY=0 = old (position fallback only).
    static const bool s_rskey = [] { const char* e = std::getenv("ROGUESQ_S7684_RSKEY"); return !(e && *e == '0'); }();
    if (!hit && s_rskey && !only_sub) {
        auto g = s_bk_by_item.find(rw(rdram, state + 0x30u));
        if (g != s_bk_by_item.end()) {
            Standin& c = s_standins[g->second];
            switch (c.sub) {
                case 0x33: case 0x36: case 0x44: case 0x4B: case 0x4F: hit = &c; hit->by_rs = true; ++s_bk_rs_hits; break;
                default: break;
            }
        }
    }
    const float x = rf(rdram, state), y = rf(rdram, state + 4u), z = rf(rdram, state + 8u);
    if (!hit) {
        for (Standin& s : s_standins) {
            if (s.state == state || s.spawn_f < 0 || s.real_add >= 0 || (only_sub && s.sub != only_sub)) continue;  // only stand-ins waiting for their real object
            const float dx = rf(rdram, s.state) - x, dy = rf(rdram, s.state + 4u) - y, dz = rf(rdram, s.state + 8u) - z;
            const float d2 = dx * dx + dy * dy + dz * dz;
            if (d2 >= 4.0f) continue;
            // s7685: the caller's own DAT item (state+0x34, else +0x30), when it points into this level's item table, names its subtype.
            // A position match whose caller is a DIFFERENT known subtype is a neighbour, not this stand-in's object: reject it
            // (ROGUESQ_S7685_POSSUB=0 = old). Logged on every position match with STANDINS_LOG ([s7685-pos]).
            static const bool s_possub = [] { const char* e = std::getenv("ROGUESQ_S7685_POSSUB"); return !(e && *e == '0'); }();
            const uint32_t c34 = rw(rdram, state + 0x34u), c30 = rw(rdram, state + 0x30u);
            auto in_tab = [](uint32_t a) { return a >= s_bk_item_lo && a <= s_bk_item_hi + 0x200u && guest(a) && (a & 1u) == 0; };
            const uint32_t ci = in_tab(c34) ? c34 : (in_tab(c30) ? c30 : 0u);
            const int csub = ci ? (int)rh(rdram, ci) : -1;
            // s7685 L12: every position caller of a sub 0x12 (tie_inter) / 0x13 (tie_bomber) stand-in had no table item (+0x30 = +0x34 =
            // 0.25f, a new state every ~3 frames: objects spawned at the craft), while those subs' real objects match by item (118/49 vs
            // 10/14 pos over 31 logs). So for these two item-keyed subs an itemless caller is not the craft.
            // s7685 run2: the same holds for the s7684 ray-shield class (keyed at +0x30): two 0x36 pillars were handed off to itemless
            // callers (state words like E7FAFFF8 / 0.0) at d 1.15-1.99 in one arm.
            // s7686 L1/L4/L5: subs 0x0D/0x14/0x1E/0x1F/0x47 show the same picture: 165/165 position callers itemless with c30 == c34 a
            // small float (0.5f / 0.25f / 0.125f), 0.9-1.9 distinct caller states per line (fresh objects, not one real object), while
            // their real objects match by item (0x14 125 item vs 5 pos handoffs). ROGUESQ_S7686_POSSUB=0 restores s7685 for these subs.
            static const bool s_possub2 = [] { const char* e = std::getenv("ROGUESQ_S7686_POSSUB"); return !(e && *e == '0'); }();
            // s7687 L10: sub 0x0C the same again: 110/110 position callers itemless, c30 == c34 = 0.25f/0.5f, 72 distinct caller states
            // (fresh objects) over 3 stand-ins, while its real objects match by item. 0x24/0x2E (L5) logged no position callers and 0x46's
            // one L0 caller carried a different known subtype (already rejected), so those keep the plain fallback.
            // ROGUESQ_S7687_POSSUB=0 restores s7686 for 0x0C.
            static const bool s_possub3 = [] { const char* e = std::getenv("ROGUESQ_S7687_POSSUB"); return !(e && *e == '0'); }();
            bool flyer = false;
            switch (s.sub) { case 0x12: case 0x13: flyer = true; break; case 0x33: case 0x36: case 0x44: case 0x4B: case 0x4F: flyer = s_rskey; break;
                             case 0x0D: case 0x14: case 0x1E: case 0x1F: case 0x47: flyer = s_possub2; break;
                             case 0x0C: flyer = s_possub3; break; default: break; }
            const bool reject = s_possub && ((csub >= 0 && csub != (int)s.sub) || (csub < 0 && flyer));
            if (s_bk_log) {
                static std::set<uint64_t> s_pseen;  // one line per (caller state, stand-in item) pair
                if (s_pseen.size() < 2000 && s_pseen.insert(((uint64_t)state << 32) | s.item).second)
                    std::fprintf(stderr, "[s7685-pos] f=%lld state=%08X c34=%08X c30=%08X caller_item=%08X caller_sub=%04X standin=%08X sub=%04X d=%.2f %s\n",
                                 (long long)(s_bk_frame + 1), state, c34, c30, ci, csub < 0 ? 0xFFFFu : (unsigned)csub, s.item, s.sub,
                                 (double)std::sqrt(d2), reject ? "REJECT" : (csub < 0 ? "unknown" : "same"));
            }
            if (reject) { ++s_bk_pos_rej; continue; }
            hit = &s; hit->by_pos = true; ++s_bk_pos_hits; break;
        }
    }
    if (!hit) return;
    Standin& s = *hit;
    // runInMissionFrame runs the draw-phase slotDispatcherIter passes (where handlers add to the bucket) BEFORE our submit hook, so
    // a real call belongs to the frame of the NEXT submit.
    const int64_t cur = s_bk_frame + 1;
    if (s.real_call < 0) { s.real_call = cur; s.fr_d = rs64_bk_vt_n ? rs64_vt_lastd : -2.0; }
    else if (s.fr_d == -2.0 && rs64_bk_vt_n) s.fr_d = rs64_vt_lastd;  // first call reused the cached result: take the next real test
    if (v0 != 1) { if (s.real_add < 0) { ++s.re_rej; ++s.re_cls[vt_class()]; } return; }
    if (s.real_add < 0) {
        s.real_add = cur;
        const float dx = rf(rdram, s.state) - x, dy = rf(rdram, s.state + 4u) - y, dz = rf(rdram, s.state + 8u) - z;
        s.dpos = std::sqrt(dx * dx + dy * dy + dz * dz);
    }
    if (s.real_last != cur) {
        s.real_last = cur;
        if (cur - s.real_add < 30) ++s.real_frames;
    }
    if (s_bk_log && cur - s.real_add >= 30) ho_log(s, "real30");
}

// s7681 (tools/apply_s7681_shield_vt.py): npcShieldUpdate (sub 0x32) never calls addNpcToVisibilityBucket; it runs the same view test
// through 0x8005940C(view, inst, state, radius) and links itself into the bucket inline when it passes. Report that test like a bucket
// return, so its stand-in hands off (or is never held) instead of being read as "spawned, never drawn". ROGUESQ_S7681_SHIELD=0 = old.
extern "C" void rs64_bk_shield(uint8_t* rdram, uint32_t state, uint32_t v0) {
    static const bool s_on = [] { const char* e = std::getenv("ROGUESQ_S7681_SHIELD"); return !(e && *e == '0'); }();
    static uint32_t n = 0, pass = 0, lines = 0;
    ++n; if ((v0 & 0xFFu) == 1u) ++pass;
    const uint32_t hits0 = s_bk_item_hits + s_bk_pos_hits;
    if (s_on) bk_ret_impl(rdram, state, v0 & 0xFFu, 0x32);
    const bool matched = s_bk_item_hits + s_bk_pos_hits != hits0;
    if (s_bk_log && lines < 64 && (n == 1 || matched || (pass == 1 && (v0 & 0xFFu) == 1u))) {
        ++lines;
        std::fprintf(stderr, "[s7681-sh] on=%d state=%08X item=%08X v0=%u calls=%u pass=%u matched=%d pos=%.1f,%.1f,%.1f\n", s_on ? 1 : 0, state,
                     guest(state) ? rw(rdram, state + 0x34u) : 0u, v0 & 0xFFu, n, pass, matched ? 1 : 0,
                     guest(state) ? rf(rdram, state) : 0.f, guest(state) ? rf(rdram, state + 4u) : 0.f, guest(state) ? rf(rdram, state + 8u) : 0.f);
    }
}

namespace {
void rebuild(uint8_t* rdram, recomp_context* ctx, uint32_t dat) {
    // s7677 per-generation tally of how real bucket calls matched their stand-in (item key vs 2-unit position fallback)
    std::fprintf(stderr, "[s7677-gen] gen=%u end dat=%08X n=%zu bk_calls=%u item_hits=%u rs_hits=%u pos_hits=%u pos_rej=%u wrong=%u\n", s_gen, s_dat, s_standins.size(),
                 s_bk_calls, s_bk_item_hits, s_bk_rs_hits, s_bk_pos_hits, s_bk_pos_rej, s_bk_wrong);
    s_bk_calls = s_bk_item_hits = s_bk_rs_hits = s_bk_pos_hits = s_bk_pos_rej = s_bk_wrong = 0;
    // s7679 life table (ROGUESQ_STANDINS_LOG=1): one line per stand-in drawn this generation, so a drawn-but-never-spawned item
    // (spawned=0) can be told from a bridged one (spawned=1) by its nearest drawn distance.
    if (const char* e = std::getenv("ROGUESQ_STANDINS_LOG"); e && *e && *e != '0') {  // s7714: =0 is off, as at every other reader
        // s7679: a hold still open at the level change never reached the 899-frame never line, so the s7675 scorer missed it
        for (const Standin& s : s_standins)
            if (s.spawn_f >= 0 && s.real_call < 0 && s.fr_d != -4.0)
                std::fprintf(stderr, "[s7675-fr] item %08X sub %04X odd=0 delay=never fr_d=-1 spawn_d=%.2f held_dmin=%.2f open=1 released=%d\n", s.item,
                             (unsigned)s.sub, s.spawn_d, s.si_dall, s.released ? 1 : 0);
        uint32_t drawn = 0, sp = 0;
        for (const Standin& s : s_standins) {
            if (s.adds == 0) continue;
            ++drawn; if (s.spawn_logged) ++sp;
            std::fprintf(stderr, "[s7679-life] gen=%u item %08X sub %04X spawned=%d adds=%u first=%.2f last=%.2f add_dmin=%.2f spawn_d=%.2f\n", s_gen, s.item,
                         (unsigned)s.sub, s.spawn_logged ? 1 : 0, s.adds, s.first_add, s.last_add, s.add_dmin, s.spawn_d);
        }
        std::fprintf(stderr, "[s7679-life] gen=%u end n=%zu drawn=%u spawned=%u\n", s_gen, s_standins.size(), drawn, sp);
    }
    ++s_gen;
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
        s.sub = sub;
        s.idx = (uint32_t)s_standins.size();
        build_state(rdram, ctx, item, state, inst, model, &s.scale);
        s_standins.push_back(s);
        at = (inst + size + 15u) & ~15u;
    }
    // s7677 positive control: ROGUESQ_S7677_PLANT=1 reverses the stand-in order from the second build on (same count, new indexes),
    // which is exactly the case the size-only map key cannot see: wrong= must be > 0 with ROGUESQ_S7677_GEN=0 and 0 with the fix.
    static const bool s_plant7677 = [] { const char* e = std::getenv("ROGUESQ_S7677_PLANT"); return e && *e == '1'; }();
    if (s_plant7677 && s_gen >= 2) {
        std::reverse(s_standins.begin(), s_standins.end());
        for (size_t i = 0; i < s_standins.size(); ++i) s_standins[i].idx = (uint32_t)i;
    }
    std::fprintf(stderr, "[standins] %zu objects, %u KB (dat %08X items %u: no-name %u no-model %u probe-dropped %u build-fail %u) level %u\n",
                 s_standins.size(), (at - kRegion) / 1024u, dat, count, noname, nomodel, probe, full, rw(rdram, 0x80130B70u));
}

int mode() {  // 0 off, 1 on, 2 tog (whole seconds), 3 frame (alternate submit calls)
    static const int m = [] {
        const char* e = std::getenv("ROGUESQ_STANDINS");
        const char* d = std::getenv("ROGUESQ_DRAW_DISTANCE");
        int v = (e && *e && *e != '0') ? (std::strcmp(e, "tog") == 0 ? 2 : std::strcmp(e, "frame") == 0 ? 3 : 1) : 0;
        const double dd = (d && *d) ? std::atof(d) : 1.0;
        if (v && !(dd > 1.0)) { std::fprintf(stderr, "[standins] ROGUESQ_STANDINS set but draw distance %.2f <= 1: off (retail)\n", dd); v = 0; }
        if (v) std::fprintf(stderr, "[standins] on mode=%s dd=%.2f region %08X..%08X\n", v == 2 ? "tog" : v == 3 ? "frame" : "on", dd, kRegion, kRegionEnd);
        return v;
    }();
    return m;
}

}  // namespace

// s7624 step 3: read by the fbdump path in upstream_compat.cpp. ROGUESQ_STANDINS_DUMP=<a>:<b>:<n> (seconds after the first
// rebuild) opens two n-swap fb dump windows: window 1 at a with the mode's own toggling, window 2 at b with stand-ins forced off
// (same-run negative control for the flicker scorer). rs64_standins_fb_on is the on/off state of the last submit call.
extern "C" int rs64_standins_dump_left = 0;
extern "C" int rs64_standins_fb_on = -1;
extern "C" uint32_t rs64_standins_fb_call = 0;
extern "C" int rs64_standins_fb_win = 0;

// s7625 G6c step 3b: which exit of the view test (transformVec3ToNpcLocalWithScale, tools/apply_s7625_viewtest_reason.py)
// rejects the stand-ins. rs64_vt_on is set only around our addNpcToVisibilityBucket mips_call.
extern "C" int rs64_vt_on = 0;
extern "C" uint32_t rs64_vt_pc = 0;
extern "C" float rs64_vt_farmul = 1.0f;
// s7675b: rs64_vt_on bit 1 = tally (our own call), bit 2 = record depth only (every view test while STANDINS_LOG); depth of the latest test
extern "C" double rs64_vt_lastd = -1.0;  // s7625: view-test far multiplier, != 1 only inside our addNpcToVisibilityBucket call
namespace {
struct VtExit { uint32_t pc; const char* name; };
constexpr VtExit kVtExits[] = {
    { 0x8001DCF4u, "boxlo_x" }, { 0x8001DD0Cu, "boxlo_y" }, { 0x8001DD24u, "boxlo_z" }, { 0x8001DD40u, "boxhi_x" },
    { 0x8001DD54u, "boxhi_y" }, { 0x8001DD68u, "boxhi_z" }, { 0x8001DD78u, "behind" }, { 0x8001DDA8u, "far" },
    { 0x8001DF00u, "sphere_side" }, { 0x8001DF08u, "side_rej" }, { 0x8001DFD4u, "sphere_direct" }, { 0x8001DFFCu, "p_boxlo_x" },
    { 0x8001E010u, "p_boxlo_y" }, { 0x8001E024u, "p_boxlo_z" }, { 0x8001E03Cu, "p_boxhi_x" }, { 0x8001E04Cu, "p_boxhi_y" },
    { 0x8001E05Cu, "p_boxhi_z" }, { 0x8001E06Cu, "p_near" }, { 0x8001E080u, "p_far" }, { 0x8001E1B4u, "p_side_rej" },
    { 0x8001E1E4u, "p_side" },
};
constexpr int kVtN = sizeof(kVtExits) / sizeof(kVtExits[0]);
struct VtTally { uint32_t rej[kVtN + 1], pass[kVtN + 1], calls, passes; double zs[4096]; uint32_t nz; double dmin, dmax; };
VtTally s_vt{};
bool s_vt_consts_logged = false;
float vt_f(const uint8_t* rdram, uint32_t a) { return rf(rdram, a); }
}  // namespace
extern "C" void rs64_vt_why(uint8_t* rdram, recomp_context* ctx, uint32_t pc) {
    {
        const uint32_t sp0 = (uint32_t)ctx->r29;
        const float x0 = vt_f(rdram, sp0 + 0x10u), y0 = vt_f(rdram, sp0 + 0x14u), z0 = vt_f(rdram, sp0 + 0x18u);
        rs64_vt_lastd = std::sqrt((double)x0 * x0 + (double)y0 * y0 + (double)z0 * z0);
    }
    if (!(rs64_vt_on & 1)) return;
    int i = 0;
    while (i < kVtN && kVtExits[i].pc != pc) ++i;
    const bool pass = (uint32_t)ctx->r2 == 1u;
    ++s_vt.calls;
    if (pass) { ++s_vt.pass[i]; ++s_vt.passes; } else ++s_vt.rej[i];
    const uint32_t sp = (uint32_t)ctx->r29, view = (uint32_t)ctx->r17;
    const float x = vt_f(rdram, sp + 0x10u), y = vt_f(rdram, sp + 0x14u), z = vt_f(rdram, sp + 0x18u);
    const double d = std::sqrt((double)x * x + (double)y * y + (double)z * z);
    if (s_vt.nz < 4096) s_vt.zs[s_vt.nz++] = d;
    if (s_vt.calls == 1 || d < s_vt.dmin) s_vt.dmin = d;
    if (s_vt.calls == 1 || d > s_vt.dmax) s_vt.dmax = d;
    if (!s_vt_consts_logged) {
        s_vt_consts_logged = true;
        std::fprintf(stderr, "[standins-why-k] boxlo=%g boxhi=%g p_lo=%g p_hi=%g view=%08X near=%g far=%g first pc=%08X xyz=%g,%g,%g v0=%d\n",
                     vt_f(rdram, 0x8000093Cu), vt_f(rdram, 0x80000940u), vt_f(rdram, 0x80000960u), vt_f(rdram, 0x80000964u), view,
                     vt_f(rdram, view + 0x24u), vt_f(rdram, view + 0x28u), pc, x, y, z, (int)pass);
    }
}
namespace {
// s7748 G6c H-size: per added stand-in, cull radius r (model +0x44 x scale) over view-test depth d. The projected radius in fb
// pixels is ~ (r/d) * (fb_h/2)/tan(fov/2); at 240 lines and a 45 deg vertical fov that factor is 290. Logged per second with the
// sub-type mix so L12 (added, invisible) can be compared with L10 (added, visible = positive control).
// Fixed-size tallies (same shape as VtTally): at most kPxN samples per second, kPxSubs distinct sub types (rest folded into "other").
constexpr uint32_t kPxN = 4096, kPxSubs = 16;  // kPxN == the literal array size in PxTally
struct PxTally { double px[4096], r[4096], d[4096]; uint32_t n, lt1, lt2, lt4, nsub; uint16_t sub[kPxSubs]; uint32_t scnt[kPxSubs + 1]; double ssum[kPxSubs + 1]; };
PxTally s_px{};
void px_note(uint16_t sub, float r, double d) {
    if (!(d > 0.0)) return;
    const double px = (double)r * 290.0 / d;
    if (s_px.n < kPxN) { s_px.px[s_px.n] = px; s_px.r[s_px.n] = r; s_px.d[s_px.n] = d; ++s_px.n; }
    s_px.lt1 += px < 1.0; s_px.lt2 += px < 2.0; s_px.lt4 += px < 4.0;
    uint32_t k = 0;
    while (k < s_px.nsub && s_px.sub[k] != sub) ++k;
    if (k == s_px.nsub && s_px.nsub < kPxSubs) s_px.sub[s_px.nsub++] = sub;
    if (k > kPxSubs) k = kPxSubs;
    ++s_px.scnt[k]; s_px.ssum[k] += px;
}
void px_flush() {
    const uint32_t n = s_px.n < kPxN ? s_px.n : kPxN;
    if (n == 0) { s_px = PxTally{}; return; }
    std::sort(s_px.px, s_px.px + n); std::sort(s_px.r, s_px.r + n); std::sort(s_px.d, s_px.d + n);
    char buf[1024]; int o = 0;
    o = rs64_apf(buf, sizeof buf, o, "[standins-px] n=%u r_med=%.3g d_med=%.3g px_min=%.2f px_med=%.2f px_max=%.2f lt1=%u lt2=%u lt4=%u subs(cnt/sum_px)", n,
                 s_px.r[n >> 1], s_px.d[n >> 1], s_px.px[0], s_px.px[n >> 1], s_px.px[n - 1], s_px.lt1, s_px.lt2, s_px.lt4);
    for (uint32_t k = 0; k <= kPxSubs; ++k) {
        if (!s_px.scnt[k]) continue;
        if (k < s_px.nsub) o = rs64_apf(buf, sizeof buf, o, " %04X:%u/%.0f", (unsigned)s_px.sub[k], s_px.scnt[k], s_px.ssum[k]);
        else o = rs64_apf(buf, sizeof buf, o, " other:%u/%.0f", s_px.scnt[k], s_px.ssum[k]);
    }
    o = rs64_apf(buf, sizeof buf, o, "\n");
    std::fputs(buf, stderr);
    s_px = PxTally{};
}
void vt_flush(uint32_t added) {
    if (s_vt.calls == 0) return;
    char buf[1024]; int o = 0;
    o = rs64_apf(buf, sizeof buf, o, "[standins-why] calls=%u pass=%u added=%u", s_vt.calls, s_vt.passes, added);
    for (int i = 0; i <= kVtN; ++i) {
        const char* n = i < kVtN ? kVtExits[i].name : "unknown";
        if (s_vt.rej[i]) o = rs64_apf(buf, sizeof buf, o, " %s=%u", n, s_vt.rej[i]);
        if (s_vt.pass[i]) o = rs64_apf(buf, sizeof buf, o, " PASS_%s=%u", n, s_vt.pass[i]);
    }
    std::sort(s_vt.zs, s_vt.zs + s_vt.nz);
    o = rs64_apf(buf, sizeof buf, o, " dmin=%.0f dmed=%.0f dmax=%.0f\n", s_vt.dmin, s_vt.nz ? s_vt.zs[s_vt.nz / 2] : 0.0, s_vt.dmax);
    std::fputs(buf, stderr);
    s_vt = VtTally{};
}
}  // namespace

// s7626 G6c step 3c: scene-graph walk probe (tools/apply_s7626_sg_probe.py). Per second: nodes visited by
// traverseSceneGraphRecursive and nodes converted to an N64 matrix, stand-in region vs all others (control), and the packed
// translation reach max|t*f12| (N64 matrix holds |t| < 128) with the camera-space depth of converted nodes.
extern "C" int rs64_sg_probe = 0;
namespace {
struct SgSide { uint32_t visit, draw, over, pulled; double tmax, zs[2048]; uint32_t nz; };
struct SgTally { SgSide s[2]; };  // [0] others, [1] stand-in region
SgTally s_sg{};
int s_sg_cur = -1;  // side of the node being converted, -1 outside a convert
std::vector<uint32_t> s_q_ours_mtx;  // part 3: stand-in matrices converted since the last queue reset
bool in_region(uint32_t a) { return a >= kRegion && a < kRegionEnd; }
void sg_flush() {
    char buf[512]; int o = std::snprintf(buf, sizeof buf, "[standins-sg]");
    for (int k = 0; k < 2; ++k) {
        SgSide& s = s_sg.s[k];
        std::sort(s.zs, s.zs + s.nz);
        o = rs64_apf(buf, sizeof buf, o, " %s visit=%u draw=%u pulled=%u over2^31=%u tmax=%.3g zmin=%.1f zmed=%.1f zmax=%.1f", k ? "ours" : "other",
                           s.visit, s.draw, s.pulled, s.over, s.tmax, s.nz ? s.zs[0] : 0.0, s.nz ? s.zs[s.nz / 2] : 0.0, s.nz ? s.zs[s.nz - 1] : 0.0);
    }
    std::fprintf(stderr, "%s\n", buf);
    s_sg = SgTally{};
}
}  // namespace
extern "C" void rs64_sg_visit(uint32_t node) { ++s_sg.s[in_region(node) ? 1 : 0].visit; }
extern "C" void rs64_sg_draw(uint8_t* rdram, uint32_t node, uint32_t m) {
    s_sg_cur = in_region(node) ? 1 : 0;
    SgSide& s = s_sg.s[s_sg_cur];
    ++s.draw;
    const float z = rf(rdram, m + 0x2Cu);
    if (s.nz < 2048) s.zs[s.nz++] = z;
    if (s_sg_cur == 1 && s_q_ours_mtx.size() < 4096) s_q_ours_mtx.push_back(rw(rdram, 0x8011DC5Cu));
    // ROGUESQ_STANDINS_PULL=<D>: a stand-in node deeper than D has its camera-space 3x4 (a stack copy, sp+0x10) scaled by D/z, so it
    // projects to the same screen place and size at depth D. Discriminator for depth-dependent loss (far clip, fog) after conversion.
    static const float s_pull = [] { const char* e = std::getenv("ROGUESQ_STANDINS_PULL"); return e ? (float)std::atof(e) : 0.0f; }();
    if (s_sg_cur == 1 && s_pull > 0.0f && z > s_pull) {
        const float k = s_pull / z;
        for (uint32_t i = 0; i < 12; ++i) { float v = rf(rdram, m + 4 * i) * k; uint32_t u; std::memcpy(&u, &v, 4); MEM_W(4 * i, (gpr)(int32_t)m) = (int32_t)u; }
        ++s.pulled;
    }
    // s7627 ROGUESQ_STANDINS_CTL=1: real-object positive control for the pixel scorer. In dump window 1 on the off-arm submit calls,
    // every REAL prebuilt-DL node (not ours) has its 3x3 zeroed so its triangles collapse to a point: real objects flicker exactly
    // as a drawing stand-in would. Ours are never added in this arm. Scorer must find excess here or the pixel chain is blind.
    static const bool s_ctl = [] { const char* e = std::getenv("ROGUESQ_STANDINS_CTL"); return e && *e && *e != '0'; }();
    if (s_ctl && s_sg_cur == 0 && rs64_standins_fb_win == 1 && rs64_standins_fb_on == 0) {
        for (uint32_t i = 0; i < 9; ++i) MEM_W(4 * i, (gpr)(int32_t)m) = 0;
        ++s.pulled;
    }
}
extern "C" void rs64_sg_draw_end(void) { s_sg_cur = -1; }
// Prebuilt-DL queue probe (tools/apply_s7626_sg_probe.py part 3): matrices converted for stand-in nodes since the last queue reset,
// entries beginFrameDLChunk read, tallied at each reset: queued/read for stand-in matrices vs others, per reset site.
namespace {
uint8_t s_q_read[512];
struct QTally { uint32_t resets[2], q[2], rd[2], maxcnt; };
QTally s_q{};
}  // namespace
extern "C" void rs64_q_read(uint32_t entry) {
    if (entry < 0x80116400u) return;
    const uint32_t i = (entry - 0x80116400u) / 12u;
    if (i < 512) s_q_read[i] = 1;
}
extern "C" void rs64_q_reset(uint8_t* rdram, uint32_t pc) {
    ++s_q.resets[pc == 0x8000B67Cu ? 1 : 0];
    const uint32_t n = std::min<uint32_t>(rw(rdram, 0x80128C6Cu), 512u);
    if (n > s_q.maxcnt) s_q.maxcnt = n;
    std::sort(s_q_ours_mtx.begin(), s_q_ours_mtx.end());
    for (uint32_t i = 0; i < n; ++i) {
        const uint32_t m = rw(rdram, 0x80116404u + 12u * i);
        const int side = std::binary_search(s_q_ours_mtx.begin(), s_q_ours_mtx.end(), m) ? 1 : 0;
        ++s_q.q[side];
        if (s_q_read[i]) ++s_q.rd[side];
    }
    s_q_ours_mtx.clear();
    std::memset(s_q_read, 0, sizeof s_q_read);
}
namespace {
void q_flush() {
    std::fprintf(stderr, "[standins-q] resets frameStart=%u initRender=%u maxcnt=%u other queued=%u read=%u ours queued=%u read=%u\n",
                 s_q.resets[0], s_q.resets[1], s_q.maxcnt, s_q.q[0], s_q.rd[0], s_q.q[1], s_q.rd[1]);
    s_q = QTally{};
}
}  // namespace
// processSceneNode branch tally (tools/apply_s7626_sg_probe.py part 2): marks 0..6 = labels L_80014FE8 (mesh already drawn this
// frame), L_80015040, L_8001513C (first draw this frame), L_800151E0, L_80015320 (leaf flag 4 clear), L_80015360, L_80015528 (exit);
// 99 = return to the walk (zero stops it); 100.. = face-render calls in source order, with zero returns counted separately.
namespace {
int s_psn_side = -1;
uint32_t s_dl34[2][2], s_dl38[2][2], s_qmax, s_fl[2][6], s_fln[2][6];
uint32_t s_psn[2][112], s_psn_zero[2][112];
const char* const kPsnLab[7] = { "FE8", "040", "13C", "1E0", "320", "360", "528" };
void psn_flush() {
    char buf[1024];
    for (int k = 0; k < 2; ++k) {
        int o = std::snprintf(buf, sizeof buf, "[standins-psn] %s", k ? "ours" : "other");
        for (int i = 0; i < 112; ++i) {
            if (!s_psn[k][i]) continue;
            if (i < 7) o = rs64_apf(buf, sizeof buf, o, " L%s=%u", kPsnLab[i], s_psn[k][i]);
            else if (i == 99) o = rs64_apf(buf, sizeof buf, o, " ret=%u ret0=%u", s_psn[k][i], s_psn_zero[k][i]);
            else if (i >= 100) o = rs64_apf(buf, sizeof buf, o, " r%d=%u/z%u", i - 100, s_psn[k][i], s_psn_zero[k][i]);
        }
        std::fprintf(stderr, "%s\n", buf);
    }
    for (int k = 0; k < 2; ++k) {
        int o = std::snprintf(buf, sizeof buf, "[standins-dl] %s dl34 null=%u set=%u dl38 null=%u set=%u qmax=%u flags", k ? "ours" : "other",
                              s_dl34[k][0], s_dl34[k][1], s_dl38[k][0], s_dl38[k][1], s_qmax);
        for (int i = 0; i < 6 && s_fln[k][i]; ++i) o = rs64_apf(buf, sizeof buf, o, " %08X:%u", s_fl[k][i], s_fln[k][i]);
        std::fprintf(stderr, "%s\n", buf);
    }
    std::memset(s_dl34, 0, sizeof s_dl34); std::memset(s_dl38, 0, sizeof s_dl38); s_qmax = 0; std::memset(s_fln, 0, sizeof s_fln);
    std::memset(s_psn, 0, sizeof s_psn); std::memset(s_psn_zero, 0, sizeof s_psn_zero);
}
}  // namespace
extern "C" void rs64_psn_side(uint32_t leaf) { s_psn_side = leaf ? (in_region(leaf) ? 1 : 0) : -1; }
// mark 0 (L_80014FE8, $s0 = mesh): the queued cached DL mesh+0x34 / +0x38 null or not, the queue count *0x80128C6C (max per second);
// mark 2 (L_8001513C): mesh+0xC flags histogram (first 6 distinct values per side).
extern "C" void rs64_psn_mark3(uint8_t* rdram, int k, int v0, uint32_t s0) {
    if (s_psn_side < 0 || k < 0 || k >= 112) return;
    const int sd = s_psn_side;
    ++s_psn[sd][k];
    if (v0 == 0) ++s_psn_zero[sd][k];
    if (k == 0 && guest(s0)) {
        ++s_dl34[sd][rw(rdram, s0 + 0x34u) != 0];
        ++s_dl38[sd][rw(rdram, s0 + 0x38u) != 0];
        const uint32_t q = rw(rdram, 0x80128C6Cu);
        if (q > s_qmax) s_qmax = q;
    }
    if (k == 2 && guest(s0)) {
        const uint32_t fl = rw(rdram, s0 + 0xCu);
        for (int i = 0; i < 6; ++i) { if (s_fln[sd][i] && s_fl[sd][i] == fl) { ++s_fln[sd][i]; break; } if (!s_fln[sd][i]) { s_fl[sd][i] = fl; s_fln[sd][i] = 1; break; } }
    }
}
extern "C" void rs64_sg_scale(float x, float y, float z, float k) {
    if (s_sg_cur < 0) return;
    SgSide& s = s_sg.s[s_sg_cur];
    const double t = std::max({ std::fabs((double)x * k), std::fabs((double)y * k), std::fabs((double)z * k) });
    if (t > s.tmax) s.tmax = t;
    if (t >= 2147483648.0) ++s.over;  // f12 = 2^24: the packed s15.16 x 2^8 word must fit 32 bits
}

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
    {   // s7696: pre-gate census, one line per second with any hook call, so a scene where the hook never runs (H-absent) shows as a
        // gap in [standins-pre] while one where it runs without a DAT shows nodat>0. Positive control: flight seconds print calls~60.
        static const bool s_plog = [] { const char* e = std::getenv("ROGUESQ_STANDINS_LOG"); return e && *e && *e != '0'; }();
        static uint32_t s_pc = 0, s_pn = 0, s_pcut = 0;
        static double s_pt = -1.0;
        ++s_pc; if (!guest(dat)) ++s_pn; if (rb(rdram, kCutsceneFlag)) ++s_pcut;
        const double pnow = std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
        if (s_pt < 0) s_pt = pnow;
        if (s_plog && pnow - s_pt >= 1.0) {
            std::fprintf(stderr, "[standins-pre] calls=%u nodat=%u cut=%u level=%u frame=%u\n", s_pc, s_pn, s_pcut, rw(rdram, 0x80130B70u), rw(rdram, 0x8013889Cu));
            s_pc = s_pn = s_pcut = 0; s_pt = pnow;
        }
    }
    if (!guest(dat)) return;
    static uint32_t s_level = ~0u, s_frame = 0;
    const uint32_t level = rw(rdram, 0x80130B70u);
    const uint32_t frame = rw(rdram, 0x8013889Cu);
    if (dat != s_dat || level != s_level || frame < s_frame) { s_level = level; rebuild(rdram, ctx, dat); }
    s_frame = frame;

    static const bool s_log = [] { const char* e = std::getenv("ROGUESQ_STANDINS_LOG"); return e && *e && *e != '0'; }();
    // s7714 truth census: the probe follows the readers' own on/off (PULL > 0, CTL non-'0'); presence alone armed it for =0.
    static const bool s_probe_pc = [] { const char* p = std::getenv("ROGUESQ_STANDINS_PULL"); const char* c = std::getenv("ROGUESQ_STANDINS_CTL");
        return (p && std::atof(p) > 0.0) || (c && *c && *c != '0'); }();
    rs64_sg_probe = (s_log || s_probe_pc) ? 1 : 0;
    const double now = std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
    static double s_t0 = std::floor(now);  // windows on whole seconds, so a tog window is all-on or all-off
    if (s_log && now - s_t0 >= 1.0) {
        vt_flush(s_t.added);
        px_flush();
        sg_flush();
        psn_flush();
        q_flush();
        std::fprintf(stderr, "[standins-s] frames=%u on=%u submits=%u added=%u cand=%u skip spawned=%u unlinked=%u dead=%u cond=%u objects=%zu farmul=%g faron=%u tog=%d cut=%u cutadded=%u\n",
                     s_t.frames, s_t.onframes, s_t.submits, s_t.added, s_t.cand, s_t.spawned, s_t.unlinked, s_t.dead, s_t.cond, s_standins.size(), (double)rs64_vt_farmul, s_t.faron,
                     m == 2 ? (int)(((long long)s_t0) & 1) ^ 1 : -1, s_t.cutframes, s_t.cutadded);  // tog=1: the window just logged was an on second
        std::fprintf(stderr, "[s7690-pt] mism=%u fix=%u\n", s_par_mism, s_par_fix);
        s_t = Tally{};
        s_t0 = std::floor(now);
    }
    ++s_t.frames;
    // s7696 G5h x G6c: do stand-ins run inside mission cutscenes? cut= counts hook frames with the cutscene byte set; edges are logged
    // with seconds since the first hook frame, and ROGUESQ_STANDINS_DUMP=c<a>:<b>:<n> anchors the two dump windows on the first
    // cutscene rising edge instead of the first frame.
    const bool cut_now = rb(rdram, kCutsceneFlag) != 0;
    static int s_cut_prev = -1;
    static double s_cut_t0 = -1.0;
    if (cut_now) ++s_t.cutframes;
    if ((int)cut_now != s_cut_prev) {
        if (s_log) std::fprintf(stderr, "[standins-cut] edge=%d level=%u frame=%u t=%.2f\n", (int)cut_now, level, frame, s_cut_prev < 0 ? 0.0 : now - s_t0);
        if (cut_now && s_cut_t0 < 0) s_cut_t0 = now;
        s_cut_prev = (int)cut_now;
    }
    static uint32_t s_calls = 0;
    ++s_calls;
    s_bk_frame = s_calls;
    s_bk_log = s_log;
    rs64_bk_on = 1;  // s7672: the handoff hold needs the real object's first acceptance in every run, not only under LOG
    static double s_first = -1.0;
    if (s_first < 0) s_first = now;
    static int s_dwin = 0;  // 0 before window 1, 1 window 1 (toggling), 2 window 2 (forced off), 3 done
    // s7745: ROGUESQ_STANDINS_DUMP=a<min_adds>:<gap>:<n> anchors on the first moment the running per-second add count (s_t.added,
    // LOG-flushed each second) reaches min_adds: window 1 opens there (a=0), window 2 (forced off) <gap> s later. Fixed windows missed
    // L10's 2-3 s add bursts (s7744).
    static const struct DumpCfg { double a, b; int n; bool cut; int adds; } s_dc = [] {
        DumpCfg c{ -1, -1, 0, false, -1 };
        if (const char* e = std::getenv("ROGUESQ_STANDINS_DUMP")) {
            if (*e == 'c') { c.cut = true; ++e; }
            if (*e == 'a') { std::sscanf(e + 1, "%d:%lf:%d", &c.adds, &c.b, &c.n); c.a = 0; }
            else std::sscanf(e, "%lf:%lf:%d", &c.a, &c.b, &c.n);
        }
        return c;
    }();
    static double s_add_t0 = -1.0;
    if (s_dc.adds > 0 && s_add_t0 < 0 && s_t.added >= (uint32_t)s_dc.adds) {
        s_add_t0 = now;
        std::fprintf(stderr, "[standins-dump] add anchor: added=%u >= %d at t=%.2f\n", s_t.added, s_dc.adds, now - s_first);
    }
    const double d_base = s_dc.adds > 0 ? s_add_t0 : s_dc.cut ? s_cut_t0 : s_first;  // < 0 until the anchor event when anchored on one
    if (s_dc.n > 0 && d_base >= 0) {
        if (s_dwin == 0 && now - d_base >= s_dc.a) { s_dwin = 1; rs64_standins_dump_left = s_dc.n; std::fprintf(stderr, "[standins-dump] window 1 (toggle) at %.1f s, %d swaps\n", now - d_base, s_dc.n); }
        else if (s_dwin == 1 && rs64_standins_dump_left <= 0 && now - d_base >= s_dc.b) { s_dwin = 2; rs64_standins_dump_left = s_dc.n; std::fprintf(stderr, "[standins-dump] window 2 (forced off) at %.1f s, %d swaps\n", now - d_base, s_dc.n); }
        else if (s_dwin == 2 && rs64_standins_dump_left <= 0) s_dwin = 3;
    }
    rs64_standins_fb_win = (s_dwin == 1 || s_dwin == 2) ? s_dwin : 0;
    bool on = true;
    if (m == 2 && (((long long)now) & 1)) on = false;  // tog: odd seconds are the off arm
    if (m == 3 && (s_calls & 1)) on = false;           // frame: odd submit calls are the off arm
    if (s_dwin == 2) on = false;
    rs64_standins_fb_on = on ? 1 : 0;
    rs64_standins_fb_call = s_calls;
    static const bool s_ctl = [] { const char* e = std::getenv("ROGUESQ_STANDINS_CTL"); return e && *e && *e != '0'; }();
    if (s_ctl) on = false;  // s7627 control arm: stand-ins never drawn, real objects flicker instead (rs64_sg_draw)
    if (!on) {
        // spawn bookkeeping still runs on off frames so the visible-before-spawn time is exact
        for (Standin& s : s_standins)
            if (!s.spawn_logged && rh(rdram, s.item + 6u) != 0xFFFFu) {
                s.spawn_logged = true;
                std::fprintf(stderr, "[standins-spawn] item %08X t=%.2f added_first=%.2f added_last=%.2f early_s=%.2f par=%u/%u,%u/%u\n", s.item, now - s_first,
                             s.first_add < 0 ? -1.0 : s.first_add - s_first, s.last_add < 0 ? -1.0 : s.last_add - s_first,
                             s.first_add < 0 ? -1.0 : now - s.first_add, s.par_try[0], s.par_add[0], s.par_try[1], s.par_add[1]);
            }
        return;
    }
    ++s_t.onframes;

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
    // s7672 positive control: ROGUESQ_S7672_PLANT=K keeps every odd-index stand-in drawing K frames past its spawn (the instrument
    // must then report overlap ~K on those items only).
    static const int64_t s_plant = [] { const char* e = std::getenv("ROGUESQ_S7672_PLANT"); return e ? (int64_t)std::atoll(e) : (int64_t)0; }();
    // s7672 fix: the game spawns an object at a range where its own view test (retail object far) still culls it, for 9-443 frames
    // (L1/L4 dd4), so the stand-in vanished at spawn and the object popped back later. ROGUESQ_S7672_HOLD=1 (default) keeps the
    // stand-in drawing after the spawn until the real object's first accepted addNpcToVisibilityBucket (cap 900 frames);
    // =0 the s7623 behaviour, =odd only odd-index stand-ins (same-run control).
    static const int s_hold = [] { const char* e = std::getenv("ROGUESQ_S7672_HOLD"); if (e && !std::strcmp(e, "odd")) return 2; return e && *e == '0' ? 0 : 1; }();
    // s7679: a held stand-in whose real object is spawned but never asks to be drawn (attract L5 sub 0x32 "shield": spawned at depth 38,
    // held 706 frames down to 4.6 units, real_call never) is drawing something the game hides. Every real object's first accepted draw
    // was at depth >= 18.0 (137 first calls, 4 levels, s7679; s7676 walkers 28.3+), so a hold that comes nearer than that without its
    // real object ever drawing is released for good. ROGUESQ_S7679_NEAR=<depth> (default 15; 0 = old s7672 hold; =odd only odd-index
    // stand-ins, same-run control).
    static const double s_near = [] { const char* e = std::getenv("ROGUESQ_S7679_NEAR"); if (!e) return 15.0; if (!std::strcmp(e, "odd")) return -15.0; return std::atof(e); }();
    static bool s_hold_logged = false;
    if (!s_hold_logged) { s_hold_logged = true; std::fprintf(stderr, "[s7672-hold] mode=%d plant=%lld near=%g\n", s_hold, (long long)s_plant, s_near); }
    auto reason = [&](Standin& s, int r) {
        if (r != 0 && s.prev_reason == 0) s.end_reason = r;  // the first non-add after the latest add
        s.prev_reason = r;
    };
    size_t si_idx = 0;
    s_gh_idx.clear();
    for (Standin& s : s_standins) {
        ++s_t.cand;
        const bool odd = (si_idx++ & 1u) != 0;
        if (s.spawn_f < 0 && rh(rdram, s.item + 6u) != 0xFFFFu) s.spawn_f = s_calls;  // before the hold test, so the spawn frame is held too
        const bool planted = (s_plant > 0 && odd && s.spawn_f >= 0 && s_calls - s.spawn_f < s_plant) ||
                             (s_hold && (s_hold == 1 || odd) && s.spawn_f >= 0 && s.real_add < 0 && s_calls - s.spawn_f < 900 && !s.released);
        if (s_log && s.spawn_f >= 0 && !s.ho_logged && (int64_t)s_calls - s.spawn_f > 600) ho_log(s, "timeout600");
        if (s_log && s.spawn_f >= 0 && s.real_call >= 0 && s.fr_d != -3.0 && s.fr_d != -2.0) {
            std::fprintf(stderr, "[s7675-fr] item %08X sub %04X odd=%u delay=%lld fr_d=%.2f spawn_d=%.2f held_dmin=%.2f\n", s.item, (unsigned)s.sub, odd ? 1u : 0u,
                         (long long)(s.real_call - s.spawn_f), s.fr_d, s.spawn_d, s.si_dall);
            s.fr_d = -3.0;  // logged
        }
        if (s_log && s.spawn_f >= 0 && s.real_call < 0 && s.fr_d != -4.0 && (int64_t)s_calls - s.spawn_f >= 899) {
            std::fprintf(stderr, "[s7675-fr] item %08X sub %04X odd=%u delay=never fr_d=-1 spawn_d=%.2f held_dmin=%.2f\n", s.item, (unsigned)s.sub, odd ? 1u : 0u,
                         s.spawn_d, s.si_dall);
            s.fr_d = -4.0;
        }
        // s7675 ghost probe: a held stand-in whose real object never accepted. Once per 60 frames from age 30: the item's slot (+6),
        // the slot table entry (*0x80130BB0 + 8*slot: +0 npc, 0 = freed), grid link, health, condition, and the nearest real call.
        if (s_log && planted && s.spawn_f >= 0 && s.real_add < 0 && (int64_t)s_calls - s.spawn_f >= 30) {
            const int64_t age = (int64_t)s_calls - s.spawn_f;
            if (age % 60 == 30) {
                const uint16_t slot = rh(rdram, s.item + 6u);
                const uint32_t tbl = rw(rdram, 0x80130BB0u);
                uint32_t npc = 0xFFFFFFFFu, n16 = 0xFFFFu;
                if (slot != 0xFFFFu && guest(tbl) && slot < 0x800u) { npc = rw(rdram, tbl + slot * 8u); if (guest(npc)) n16 = rh(rdram, npc + 0x16u); }
                const bool linked = std::binary_search(s_linked.begin(), s_linked.end(), s.item);
                const int32_t hp = (int32_t)rw(rdram, s.item + 0x6Cu + diff * 4u);
                char nm[17] = {};
                const uint32_t mn = handler_model_name(s.sub);
                for (int i = 0; mn && i < 16; ++i) { const uint8_t c = rb(rdram, mn + i); if (!c) break; nm[i] = (c >= 32 && c < 127) ? (char)c : '?'; }
                std::fprintf(stderr, "[s7675-gh] item %08X sub %04X odd=%u age=%lld real_call=%lld re_rej=%u slot=%04X npc=%08X npc16=%04X linked=%d hp=%d "
                             "held_ok=%u near_d=%.2f near_state=%08X near_item=%08X near_calls=%u si_d=%.2f model=%s pos=%.1f,%.1f,%.1f\n",
                             s.item, (unsigned)s.sub, odd ? 1u : 0u, (long long)age, (long long)s.real_call, s.re_rej, (unsigned)slot, npc, n16, linked ? 1 : 0, hp,
                             s.held_ok, s.nd2 < 0 ? -1.0 : std::sqrt((double)s.nd2), s.n_state, s.n_item, s.n_calls, s.si_dmin, nm,
                             (double)rf(rdram, s.state), (double)rf(rdram, s.state + 4u), (double)rf(rdram, s.state + 8u));
                s.nd2 = -1.0f; s.n_state = s.n_item = s.n_calls = 0; s.si_dmin = -1.0;
            }
            s_gh_idx.push_back(si_idx - 1);
        }
        if (rh(rdram, s.item + 6u) != 0xFFFFu && !planted) {
            if (s.spawn_f < 0) s.spawn_f = s_calls;
            reason(s, 2);
            ++s_t.spawned;
            if (!s.spawn_logged) {
                s.spawn_logged = true;
                std::fprintf(stderr, "[standins-spawn] item %08X t=%.2f added_first=%.2f added_last=%.2f early_s=%.2f par=%u/%u,%u/%u\n", s.item, now - s_first,
                             s.first_add < 0 ? -1.0 : s.first_add - s_first, s.last_add < 0 ? -1.0 : s.last_add - s_first,
                             s.first_add < 0 ? -1.0 : now - s.first_add, s.par_try[0], s.par_add[0], s.par_try[1], s.par_add[1]);
            }
            continue;
        }
        if (!planted && rh(rdram, s.item + 6u) == 0xFFFFu) {
            if (!std::binary_search(s_linked.begin(), s_linked.end(), s.item)) { reason(s, 3); ++s_t.unlinked; continue; }
            if ((int32_t)rw(rdram, s.item + 0x6Cu + diff * 4u) <= 0) { reason(s, 4); ++s_t.dead; continue; }
            if (!cutscene && mips_call(rdram, ctx, kConditionMet, { s.item }).v0 == 0) { reason(s, 5); ++s_t.cond; continue; }
        }
        // addNpcToVisibilityBucket returns 1 only when the view test (transformVec3ToNpcLocalWithScale 0x8001DC34) passed and the
        // node was linked into the view's list (a linked list: no fixed bucket capacity, code read s7624); 0 = culled.
        // s7625: ROGUESQ_STANDINS_FAR=<m> (default = the draw distance; 1 or 0 = retail far) widens the view test's far bound
        // for this call only; =tog applies it in even seconds (same-run A/B).
        static const double s_far = [] {
            const char* e = std::getenv("ROGUESQ_STANDINS_FAR");
            if (e && !std::strcmp(e, "tog")) return -1.0;
            if (e && *e) { const double v = std::atof(e); return v > 1.0 ? v : 1.0; }
            const char* d = std::getenv("ROGUESQ_DRAW_DISTANCE");
            const double v = d ? std::atof(d) : 1.0;
            return v > 1.0 ? v : 1.0;
        }();
        static const double s_dd = [] { const char* d = std::getenv("ROGUESQ_DRAW_DISTANCE"); const double v = d ? std::atof(d) : 1.0; return v > 1.0 ? v : 1.0; }();
        const bool far_on = s_far > 0 || !(((long long)now) & 1);
        rs64_vt_farmul = (float)(s_far > 0 ? s_far : (far_on ? s_dd : 1.0));
        if (far_on && s_far < 0) ++s_t.faron;
        rs64_vt_on = s_log ? 3 : (s_near != 0 ? 2 : 0);  // s7679: bit 2 = depth only (no tally), so the near release works without logging
        rs64_vt_lastd = -1.0;
        // s7690: addNpcToVisibilityBucket slices its view test over two frames. On odd game frames (*0x8013889C & 1, lui 0x8014 / lw -0x7764) an instance with
        // flag 0x80 skips the test and reuses its cached 0x200 bit, on even frames one with 0x100 does; the group is assigned at the
        // first call by balancing 0x801394E2/E4, so neighbouring stand-ins alternate groups and which one gets which varies per run.
        // STANDINS=frame calls only on alternate frames, so half the stand-ins were never re-tested and kept their first (culled)
        // result for good (s7689 "pair partner" loss: odd index, si_novt). In frame mode put the instance in the group that is
        // tested this frame. ROGUESQ_S7690_PARITY=0 = old behaviour (same-run control: mismatches still counted).
        static const bool s_par7690 = [] { const char* e = std::getenv("ROGUESQ_S7690_PARITY"); return !(e && *e == '0'); }();
        {
            const uint16_t f8 = rh(rdram, s.inst + 8u);
            const uint16_t want = (rw(rdram, 0x8013889Cu) & 1u) ? 0x100u : 0x80u;
            const bool mism = (f8 & 0x180u) != 0 && (f8 & 0x180u) != want;
            if (mism) { ++s.par_mism; ++s_par_mism; }
            if (m == 3 && s_par7690 && mism) { wh(rdram, s.inst + 8u, (uint16_t)((f8 & ~0x180u) | want)); ++s.par_fix; ++s_par_fix; }
        }
        rs64_bk_self = 1;
        const uint32_t add_v0 = mips_call(rdram, ctx, kAddToBucket, { view, s.inst, s.state, s.scale }).v0;
        rs64_bk_self = 0;
        if (planted) { ++s.held; if (add_v0 == 1) ++s.held_ok; else ++s.si_cls[vt_class()]; }
        if (planted && s_near != 0 && (s_near > 0 || odd) && s.real_call < 0 && rs64_vt_lastd >= 0 && rs64_vt_lastd < std::fabs(s_near)) {
            s.released = true;
            std::fprintf(stderr, "[s7679-rel] item %08X sub %04X depth=%.2f age=%lld held_ok=%u\n", s.item, (unsigned)s.sub, rs64_vt_lastd,
                         (long long)((int64_t)s_calls - s.spawn_f), s.held_ok);
        }
        if (rs64_bk_vt_n && rs64_vt_lastd >= 0) {
            if (planted && (s.si_dmin < 0 || rs64_vt_lastd < s.si_dmin)) s.si_dmin = rs64_vt_lastd;
            if (planted && (s.si_dall < 0 || rs64_vt_lastd < s.si_dall)) s.si_dall = rs64_vt_lastd;
            if (s.spawn_d < 0 && s.spawn_f >= 0) s.spawn_d = rs64_vt_lastd;
        }
        rs64_vt_on = s_log ? 2 : 0;
        rs64_vt_farmul = 1.0f;
        ++s.par_try[s_calls & 1u];
        if (s_log && !s.par_logged && s.par_try[0] + s.par_try[1] >= 120) {
            s.par_logged = true;
            std::fprintf(stderr, "[s7690-par] item %08X sub %04X idx=%u grp=%03X mism=%u fix=%u tries=%u adds=%u\n", s.item, (unsigned)s.sub, s.idx,
                         (unsigned)(rh(rdram, s.inst + 8u) & 0x180u), s.par_mism, s.par_fix, s.par_try[0] + s.par_try[1], s.par_add[0] + s.par_add[1] + (add_v0 == 1 ? 1u : 0u));
        }
        if (add_v0 == 1) ++s.par_add[s_calls & 1u];
        reason(s, add_v0 == 1 ? 0 : 1);
        if (add_v0 == 1) {
            s.last_si = s_calls;
            if (s.real_last == (int64_t)s_calls) ++s.overlap;  // real call came first this frame
            ++s_t.added;
            if (cutscene) ++s_t.cutadded;
            if (s.first_add < 0) s.first_add = now;
            s.last_add = now;
            ++s.adds;
            if (rs64_bk_vt_n && rs64_vt_lastd >= 0 && (s.add_dmin < 0 || rs64_vt_lastd < s.add_dmin)) s.add_dmin = rs64_vt_lastd;
            if (s_log && rs64_vt_lastd > 0) { float r; std::memcpy(&r, &s.scale, 4); px_note(s.sub, r, rs64_vt_lastd); }
        }
        ++s_t.submits;
    }
}
