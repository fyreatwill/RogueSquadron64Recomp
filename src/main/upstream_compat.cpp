// Upstream-librecomp gap-filler: libultra _recomp bindings that the
// recompiled game calls but upstream librecomp doesn't provide. Stubbed
// to safe defaults — none of these primitives have meaningful semantics
// on a non-N64 host (cache management, controller pak access, etc.).
//
// All taken verbatim from MikeSemicolonD/N64ModernRuntime fork additions.
// Lifted into our repo so we don't have to maintain a librecomp fork.

#include "rs64_apf.h"  // s7359 class AJ
#include <cmath>
#include <chrono>
#include <exception> // s7607: std::uncaught_exceptions in ~Rs64Cf0Delay
extern "C" volatile uint32_t rs64_vi_n_g;  // s7514
extern "C" unsigned long long osGetTime();  // s7514 (ultramodern timer.cpp, OSTime = u64)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdarg>
#include <thread>
#include <mutex>
#include <set>
#include <map>
#include <deque>
#include <vector>
#include <tuple>
#include <string>
#include <chrono>
#include <ctime>
#ifdef __APPLE__
#include <mach/mach_time.h>
#endif
#include <pthread.h>
#include <unistd.h>
#if !defined(_WIN32)
#include <dlfcn.h>
#endif

#ifdef _WIN32
// For RtlCaptureStackBackTrace + GetCurrentThreadId in the task-submit
// stack-trace gate. Keep these out of broader code so we don't pull in
// windows.h elsewhere.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <dbghelp.h>
#include <timeapi.h>
#pragma comment(lib, "dbghelp.lib")
#pragma comment(lib, "winmm.lib")
#else
#include "win_compat.h"
#include "rs64_rdram_peek.h"
#endif

#include <algorithm>
#include <atomic>
#include <execinfo.h>
#include <mach-o/dyld.h>

#include "recomp.h"
#include "hle/rt64_vi.h"

extern "C" uint32_t g_s6491[4]; // s6491 terrain-grid call/list/chain counters
extern "C" uint32_t g_s6489[8]; // s6489 cumulative cell-gate exit counters (patched funcs_10.c)
extern "C" uint32_t rs64_phase_ord(void);
// s6718 G1d: widened 640x340 mission-intro width (0 = off) and "live video state is the 640x340 intro"; set by fixup patches.
// s6898: letterbox overlay right edge follows the widened frame, tools/apply_s6898_letterbox.py. ROGUESQ_G1D_LETTERBOX=0 = old, =tog = odd mach seconds fixed.
extern "C" void rs64_frame_trig_lb(void);  // s7166: dpc_bridge.cpp ROGUESQ_G5B_FRAME_TRIG_LB ring trigger (letterbox overlay call)
extern "C" uint32_t rs64_s6898_ovl_x1(uint32_t x1, uint32_t w) {
    rs64_frame_trig_lb();
    static int mode = -1, fbw = 0;
    if (mode < 0) { const char* e = getenv("ROGUESQ_G1D_LETTERBOX"); mode = (e && *e == '0') ? 0 : (e && *e == 't') ? 2 : 1; const char* b = getenv("ROGUESQ_FB_WIDTH"); fbw = b ? atoi(b) : 0; }
    if (!mode || fbw <= 512 || (int)w != fbw || x1 >= w) return x1;
    if (mode == 2 && !((mach_absolute_time() / 24000000ull) & 1)) return x1;
    return w;
}
extern "C" { double rs64_s6879_fpk = 1.0; } // s6879: footprint x factor of this frame, tools/apply_s6879_fpdepth.py
// s6880: wide frames get the s6049 span-table store bound, tools/apply_s6880_widebound.py. ROGUESQ_G1D_SPANBOUND=0 = old.
extern "C" int rs64_s6880_wide(void) { static int on = -1; if (on < 0) { const char* e = getenv("ROGUESQ_G1D_SPANBOUND"); on = !(e && *e == '0'); } return on && rs64_s6879_fpk != 1.0; }
// s6882: narrow the span fill x loops where the s6049/s6880 bound runs (tools/apply_s6882_spannarrow.py). ROGUESQ_G1D_SPANNARROW=0 = old.
// s6903 G5d: dd levers apply to levels 0..18 only; 0x13/0x14 are sentinels (boot cinematic is 0x13). ROGUESQ_DD_CINE_GATE=0 old, =tog gate on in odd 4 s blocks.
extern "C" volatile int g_rs64_dd_scene = 1;
// s6904 G5e: fog words hook at 0x8001726C, f4 = fm, f0 = fo. See tools/apply_s6904_fog.py. The level's fog distances do not follow dd, but the
// switch to the fog blender does, so past retail's ramp extended terrain drew unfogged, then flipped to solid fog colour. Default at dd>1: ramp
// start x max(1, 0.375 dd), end x 0.8 dd, and the s6418 cutoff pulled in to the ramp start, at most to (dd/2)^2, so the ramp runs on fogged cells. ROGUESQ_DD_FOG=<ks>,<ke> sets the ramp,
// =0 old, =tog 4 s blocks of the default. ROGUESQ_DD_FARCLIP_MUL still overrides the cutoff. dd1 and sentinel scenes untouched.
static double s6904_ks = 0, s6904_ke = 0, s6904_dd = 1.0, s6904_s = 0; static int s6904_tog = 0, s6904_lg = -1;
static void s6904_init() {
    const char *e = std::getenv("ROGUESQ_G5E_FOGP"), *f = std::getenv("ROGUESQ_DD_FOG"), *d = std::getenv("ROGUESQ_DRAW_DISTANCE");
    const double dd = d && *d ? atof(d) : 1.0;
    s6904_dd = dd;
    if (dd > 1.0) { s6904_ks = 0.375 * dd < 1.0 ? 1.0 : 0.375 * dd; s6904_ke = 0.8 * dd; } // never hazier than retail
    if (f && *f == 't') s6904_tog = 1;
    else if (f && *f) { double a = 0, b = 0; if (sscanf(f, "%lf,%lf", &a, &b) == 2 && a > 0 && b > 0) { s6904_ks = a; s6904_ke = b; } else s6904_ks = s6904_ke = 0; }
    s6904_lg = e && *e && *e != '0';
}
static int s6904_on() { if (s6904_lg < 0) s6904_init(); return s6904_ks > 0 && (!s6904_tog || ((mach_absolute_time() / 96000000ull) & 1)); }
// s7302 G5e far band: ROGUESQ_DD_FOG_ALT=<ks>,<ke> uses that ramp on rs64_tog_odd seconds (same [s7010-clk] split as R_TOG), the default
// ramp otherwise, so one run A/Bs two ramps. The alt cutoff floor is 1/dd^2 (cutoff never nearer than retail) instead of (dd/2)^2, so
// a ramp starting nearer than 0.375 dd can still pull the fog-blender switch in to its start. =<ks>,<ke>,1 = alt every second.
static double s7302_ks = 0, s7302_ke = 0; static int s7302_all = 0;
extern "C" int rs64_tog_odd(uint64_t mt); extern "C" void rs64_tog_anchor(uint64_t mt);
static int s7302_alt() {
    static int init = 0;
    if (!init) { init = 1; const char *a = std::getenv("ROGUESQ_DD_FOG_ALT"); double x = 0, y = 0; int z = 0;
        if (a && sscanf(a, "%lf,%lf,%d", &x, &y, &z) >= 2 && x > 0 && y > 0) { s7302_ks = x; s7302_ke = y; s7302_all = z == 1; }
        if (s7302_ks > 0) fprintf(stderr, "[s7302] fog alt ks=%g ke=%g all=%d\n", s7302_ks, s7302_ke, s7302_all); }
    if (s7302_ks <= 0) return 0;
    const uint64_t mt = mach_absolute_time(); rs64_tog_anchor(mt);
    return s7302_all || rs64_tog_odd(mt);
}
// The cutoff only needs to sit inside the ramp start. Seam distance (fog units) ~ 24 x cutoff factor on lvl1/lvl4; 26 leaves a margin. Clamped between
// a total of (dd/2)^2 and no pull. Levels 1/4/5 all have s ~34, so this is 0.43 at dd2, 0.25 at dd3 and dd4 there.
extern "C" float rs64_s6904_clipmul(float v) {
    if (v > 0.0f) return v;
    if (!s6904_on()) return 1.0f;
    const int alt = s7302_alt(); const double ks = alt ? s7302_ks : s6904_ks, lo = alt ? 1.0 / (s6904_dd * s6904_dd) : 0.25;
    const double r = s6904_s * ks / (26.0 * s6904_dd), m = r * r;
    return s6904_s <= 0 ? (float)lo : (float)(m < lo ? lo : m > 1.0 ? 1.0 : m);
}
// s6919 G5h: tools/apply_s6919_cutlive.py. ROGUESQ_CUT_LIVE (default on, =0 old, =tog odd seconds) leaves the game's far cutoff 0x8009DEB4 alone where the dd scale is off.
// ROGUESQ_DD_CUT_LIVE=1|tog (default off): where it is on, scale the game's value, not the one latched at boot. Writes are remembered so a frame without a game write cannot compound.
static int s6919_mode(const char *n, int def) { const char *e = getenv(n); return !(e && *e) ? def : e[0] == 't' ? 2 : e[0] != '0'; }
static inline int s6919_live(int m) { return m == 1 || (m == 2 && ((mach_absolute_time() / 24000000ull) & 1)); }
extern "C" { uint32_t g_rs64_s6919[12]; }
static uint32_t s6919_lastw = 0, s6919_lastb = 0, s6919_org = 0;
// s7567 19d witness: ROGUESQ_S7567_CUTW=1 prints every 300 s6418-block passes: passes, dda passes, keep passes, our writes of
// 0x8009DEB4 (all of them go through rs64_s6919_wrote), passes where the game's live value differs from the boot latch, and the values.
static int s7567_keep = 0; static uint32_t s7567_n[6]; static uint32_t s7567_cur = 0;
static int s7567_on() { static int on = -1; if (on < 0) { const char *e = getenv("ROGUESQ_S7567_CUTW"); on = e && *e && *e != '0'; } return on; }
static void s7567_tick(uint32_t org, uint32_t cur, int dda) {
    if (!s7567_on()) return;
    s7567_n[0]++; s7567_n[1] += dda != 0; s7567_n[2] += s7567_keep != 0; s7567_n[4] += (s6919_org ? s6919_org : org) != cur; s7567_cur = cur;
    if (s7567_n[0] % 300 == 0) { union { uint32_t u; float f; } a, b, c; a.u = cur; b.u = s6919_org ? s6919_org : org; c.u = s6919_lastw;
        fprintf(stderr, "[s7567] pass=%u dda=%u keep=%u writes=%u livediff=%u cur=%g org=%g lastw=%g\n", s7567_n[0], s7567_n[1], s7567_n[2], s7567_n[3], s7567_n[4], a.f, b.f, c.f); }
}
extern "C" int rs64_s6919_keep(int dda) {
    static int m = -1; if (m < 0) m = s6919_mode("ROGUESQ_CUT_LIVE", 1);
    const int live = s6919_live(m); g_rs64_s6919[11] = (uint32_t)live;
    s7567_keep = live && !dda; return s7567_keep;
}
extern "C" uint32_t rs64_s6919_base(uint32_t org, uint32_t cur, int dda) {
    static int m = -1; if (m < 0) m = s6919_mode("ROGUESQ_DD_CUT_LIVE", 0);
    s7567_tick(org, cur, dda);
    if (!s6919_org) s6919_org = org;
    if (!dda || !s6919_live(m)) return s6919_org;
    if (cur != s6919_lastw) s6919_lastb = cur;
    return s6919_lastb ? s6919_lastb : s6919_org;
}
extern "C" void rs64_s6919_wrote(uint32_t v) { s6919_lastw = v; s7567_n[3]++; }
extern "C" void rs64_s6919_cut(uint8_t *rdram, uint32_t node) {
    static int on = -1; if (on < 0) { const char *e = getenv("ROGUESQ_G5H_BAND"); on = e && *e; }
    if (!on) return;
    const auto w = [&](uint32_t a) { return (uint32_t)MEM_W(0, (int64_t)(int32_t)a); };
    g_rs64_s6919[0] = w(node + 8); g_rs64_s6919[1] = w(0x8009DEB4u); g_rs64_s6919[2] = w(node + 0xC); g_rs64_s6919[3] = w(node + 0x10);
    for (uint32_t i = 0; i < 3; i++) g_rs64_s6919[4 + i] = w(0x80130C10u + 4 * i);
    for (uint32_t i = 0; i < 4; i++) g_rs64_s6919[7 + i] = w(0x80132DB0u + 4 * i);
}
extern "C" void rs64_s6904_fog(uint8_t *rdram, recomp_context *ctx) {
    const int want = s6904_on(); const int alt = want && s7302_alt(); const double ks = alt ? s7302_ks : s6904_ks, ke = alt ? s7302_ke : s6904_ke; const int lg = s6904_lg;
    auto rf = [&](uint32_t a) { uint32_t v = (uint32_t)MEM_W(0, (int64_t)(int32_t)a); float f; memcpy(&f, &v, 4); return f; };
    const float s = rf(0x8011A878u), e = rf(0x8011A87Cu), D = rf(0x8011A8CCu), A = rf(0x8011A7D4u), B = rf(0x801163C0u);
    s6904_s = s <= D ? D : s;
    extern volatile int g_rs64_dd_scene;
    const int on = want && g_rs64_dd_scene;
    { extern float g_rs64_s7030_fe; g_rs64_s7030_fe = (float)((e <= D ? D : e) * (on ? ke : 1.0) * 0.5); } /* s7030: fog end, grid units (cell = 2 world) */
    if (on) {
        auto zf = [&](double dist) { const double z = (double)A + (double)B / dist; return z < -1.0 ? 0.0 : (z + 1.0) / 2.0; };
        double f6 = zf((double)(s <= D ? D : s) * 256.0 * ks), f4 = zf((double)(e <= D ? D : e) * 256.0 * ke);
        if (f4 <= f6) f6 = f4 - 0.0001;
        ctx->f4.fl = (float)(0.5 / (f4 - f6) * 65536.0); ctx->f0.fl = (float)((0.5 - f6) / (f4 - f6) * 65536.0);
    }
    if (lg) {
        static unsigned n = 0; static float last[5];
        const float c[5] = { s, e, D, A, B };
        if (memcmp(c, last, sizeof c) && n < 4000) { memcpy(last, c, sizeof c); n++; fprintf(stderr, "[fogp] n=%u s=%g e=%g D=%g A=%.9g B=%.9g on=%d fm=%.1f fo=%.1f mul=%.3f\n", n, s, e, D, A, B, on, ctx->f4.fl, ctx->f0.fl, rs64_s6904_clipmul(0.0f)); }
    }
}

// s7030 G1c fogged-cell cull (tools/apply_s7030_fogcull.py). ROGUESQ_DD_FOGCULL=<k> culls, in the terrain stream, cells whose
// near-edge forward depth is past k x fog end; =tog3 cycles k over ROGUESQ_DD_FOGCULL_K=a,b,c (default 0,1,0.5) on (mach/24e6)%3 s.
// Every phase keeps a histogram of cell depth / fog end (20 bins of 0.1, last = >=1.9) over cells reaching the call path.
extern "C" void rs64_tog_anchor(uint64_t mt);
extern "C" { int g_rs64_s7030 = [] { const char* e = getenv("ROGUESQ_DD_FOGCULL"), *o = getenv("ROGUESQ_DD_OFFMAPCULL");
                 return ((e && *e && (*e == 't' || atof(e) > 0.0)) || (o && *o)) ? 1 : 0; }(); /* s7031: OFFMAPCULL also arms the hook; s7032: "0.3" armed nothing (old test *e != '0') */
             float g_rs64_s7030_f[2] = {0.0f, 1.0f}; float g_rs64_s7030_fe = 0.0f; }
static float s7030_k[3] = {0.0f, 1.0f, 0.5f}; static int s7030_tog3 = 0, s7030_ph = 0; static float s7030_thr = 0.0f, s7030_fe = 0.0f;
// s7031 off-map census (tools/apply_s7031_offmap.py): per phase, off-map cells per depth bin, ring distance outside the map edge (all
// off-map cells and those in the 0.5-1.0 fog-end band), and ROGUESQ_DD_OFFMAPCULL=<R>|tog3 (_R=a,b,c; R<0 off) culls rings > R.
// s7034 fog-depth condition: ROGUESQ_DD_OFFMAPCULL_K=<k>|a,b,c (tog3 per phase; default 0 = none): an off-map cell past R is culled only if
// its near-edge depth d-0.71 > k * fog end. s7034_kc = culled per depth bin, s7034_kk = past R but kept by K.
static float s7034_k[3] = {0.0f, 0.0f, 0.0f}; static float s7056_base[3] = {0.0f, 0.0f, 0.0f}, s7056_kl[32] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1}; static int s7056_tog = 0; static uint32_t s7056_last = 0xFFFFFFFFu; static uint64_t s7034_kc[3][20], s7034_kk[3];
// s7046 eye-to-edge K gate: ROGUESQ_DD_OFFMAPCULL_KEDGE=<k2>[,N[,phasemask]] (default N=8, mask 7): an off-map cell past R whose clamped
// edge lies on a map side the eye (s7032 latched eye cell) is within N cells of uses K=k2 instead of K. s7046_kc = cells that took k2,
// s7046_ed = per-frame histogram of the eye's min distance to any map side (0..31, 31 = >=31).
// s7047 per-phase form: ROGUESQ_DD_OFFMAPCULL_KEDGE=<k2a>,<Na>;<k2b>,<Nb>;<k2c>,<Nc> (tog3 phase 0/1/2; k2<=0 = gate off that phase), so
// two variants and the plain-K baseline share one hold.
static float s7046_k2[3] = {-1.0f, -1.0f, -1.0f}; static int s7046_n[3] = {8, 8, 8}, s7046_mask = 7; static uint64_t s7046_kc[3], s7046_kcull[3], s7046_ed[3][32];
static int s7031_R[3] = {-1, -1, -1}, s7031_w = 0, s7031_hgt = 0; static uint64_t s7031_off[3][20], s7031_ring[3][18], s7031_rband[3][18], s7031_cull[3];
static uint64_t s7030_h[3][20], s7030_cull[3], s7030_frames[3], s7030_t0 = 0, s7030_last = 0; static double s7030_F[3], s7030_FE[3];
// s7032 eye gate (tools/apply_s7032_eyegate.py): the s7031 ring cull leaves a sky void once the eye is over the off-map plateau
// (frozen-pose arms). The eye cell is x - sgn*off, with the sign whose estimate is consistent across a frame's cells (spread of the
// other is the window width); latched per frame, used next frame. ROGUESQ_DD_OFFMAPCULL_EYE=0 = s7031 ungated.
static int s7032_gate = -1, s7032_eyex = 0, s7032_eyez = 0, s7032_eyering = 0; static float s7032_mn[2][2], s7032_mx[2][2]; static uint64_t s7032_eyeoff[3], s7032_spread_bad = 0;
static void rs64_s7032_frame() {
    if (s7032_gate < 0) { const char* g = getenv("ROGUESQ_DD_OFFMAPCULL_EYE"); s7032_gate = !(g && g[0] == '0'); fprintf(stderr, "[s7032] eyegate=%d\n", s7032_gate); }
    const float sp0 = (s7032_mx[0][0] - s7032_mn[0][0]) + (s7032_mx[0][1] - s7032_mn[0][1]), sp1 = (s7032_mx[1][0] - s7032_mn[1][0]) + (s7032_mx[1][1] - s7032_mn[1][1]);
    if (s7032_mx[0][0] >= s7032_mn[0][0]) { const int s = sp0 <= sp1 ? 0 : 1; if ((s ? sp1 : sp0) > 4.0f) s7032_spread_bad++;
        s7032_eyex = (int)floorf(0.5f * (s7032_mn[s][0] + s7032_mx[s][0])); s7032_eyez = (int)floorf(0.5f * (s7032_mn[s][1] + s7032_mx[s][1]));
        const int dx = s7032_eyex < 0 ? -s7032_eyex : s7032_eyex >= s7031_w ? s7032_eyex - s7031_w + 1 : 0, dz = s7032_eyez < 0 ? -s7032_eyez : s7032_eyez >= s7031_hgt ? s7032_eyez - s7031_hgt + 1 : 0;
        s7032_eyering = dx > dz ? dx : dz; }
    for (int s = 0; s < 2; s++) for (int c = 0; c < 2; c++) { s7032_mn[s][c] = 1e9f; s7032_mx[s][c] = -1e9f; }
}
// s7033 height gate: a cell's byte height range is rec[3..4] of record (hm[z*w+x] & 0x1FFF) * 30 at *(0x80136DC4), hm at *(0x80136DC0)
// (stream 0x80042D6C..DA8); the view span bytes are trunc(y * C / H), C = *(0x8003A4F8), H = *(0x80136DD0) (binPolygonIntoTerrainGrid
// 0x800428A8). "Up" is calibrated per frame from the eye's own (on-map, clamped) cell: the eye is above its ground. An off-map cell past
// the ring R is culled only while the eye is below its clamped edge cell's top by > margin. ROGUESQ_DD_OFFMAPCULL_H=<margin> (default 1),
// =off restores fixed R; =tog applies the gate in tog3 phase 1 only (same-run cost split R=-1 / 2h / 2).
static uint8_t* s7033_rd = nullptr; static int s7033_on = -1, s7033_up = 0; static float s7033_m = 1.0f, s7033_eb = 0.0f, s7033_sc = 0.0f;
static int s7033_emin = 0, s7033_emax = 0; static uint64_t s7033_keep[3], s7033_pass[3], s7033_upc[2];
static void rs64_s7033_hr(int32_t x, int32_t z, int* mn, int* mx) {
    uint8_t* rdram = s7033_rd; if (!rdram || s7031_w <= 0 || s7031_hgt <= 0) { *mn = -128; *mx = 127; return; }
    x = x < 0 ? 0 : x >= s7031_w ? s7031_w - 1 : x; z = z < 0 ? 0 : z >= s7031_hgt ? s7031_hgt - 1 : z;
    const uint32_t hm = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DC0), rt = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DC4);
    const uint32_t i = (uint32_t)MEM_HU(0, (int64_t)(int32_t)(hm + 2u * (uint32_t)(z * s7031_w + x))) & 0x1FFFu;
    *mn = (int)(int8_t)MEM_B(3, (int64_t)(int32_t)(rt + 30u * i)); *mx = (int)(int8_t)MEM_B(4, (int64_t)(int32_t)(rt + 30u * i));
}
static void rs64_s7033_frame(uint8_t* rdram, uint32_t a0) {
    if (s7033_on < 0) { const char* h = getenv("ROGUESQ_DD_OFFMAPCULL_H"); s7033_on = (h && h[0] == 'o') ? 0 : (h && h[0] == 't') ? 2 : 1; if (h && h[0] != 'o' && h[0] != 't' && *h) s7033_m = (float)atof(h); /* =tog: gate in tog3 phase 1 only */
        fprintf(stderr, "[s7033] heightgate=%d margin=%g\n", s7033_on, s7033_m); }
    s7033_rd = rdram;
    auto rf = [&](uint32_t a) { uint32_t v = (uint32_t)MEM_W(0, (int64_t)(int32_t)a); float f; memcpy(&f, &v, 4); return f; };
    const float H = rf(0x80136DD0u); s7033_sc = H != 0.0f ? rf(0x8003A4F8u) / H : 0.0f; s7033_eb = rf(a0 + 4) * s7033_sc;
    rs64_s7033_hr(s7032_eyex, s7032_eyez, &s7033_emin, &s7033_emax);
    s7033_up = s7033_eb >= 0.5f * (s7033_emin + s7033_emax) ? 1 : -1; s7033_upc[s7033_up > 0]++;
}
extern "C" void rs64_s7030_begin(uint8_t *rdram, uint32_t a0) {
    static int init = 0;
    if (!init) { init = 1; const char* e = getenv("ROGUESQ_DD_FOGCULL");
        if (e && e[0] == 't') { s7030_tog3 = 1; const char* k = getenv("ROGUESQ_DD_FOGCULL_K"); float a, b, c;
            if (k && sscanf(k, "%f,%f,%f", &a, &b, &c) == 3) { s7030_k[0] = a; s7030_k[1] = b; s7030_k[2] = c; } }
        else { s7030_k[0] = s7030_k[1] = s7030_k[2] = e ? (float)atof(e) : 0.0f; }
        if (const char* o = getenv("ROGUESQ_DD_OFFMAPCULL")) {
            if (o[0] == 't') { s7030_tog3 = 1; const char* r = getenv("ROGUESQ_DD_OFFMAPCULL_R"); int a, b, c;
                if (r && sscanf(r, "%d,%d,%d", &a, &b, &c) == 3) { s7031_R[0] = a; s7031_R[1] = b; s7031_R[2] = c; } else { s7031_R[1] = 2; s7031_R[2] = 8; }
                if (!(e && e[0] == 't')) s7030_k[0] = s7030_k[1] = s7030_k[2] = e ? (float)atof(e) : 0.0f; }
            else s7031_R[0] = s7031_R[1] = s7031_R[2] = atoi(o); }
        if (const char* k = getenv("ROGUESQ_DD_OFFMAPCULL_K")) { float a, b, c;
            if (sscanf(k, "%f,%f,%f", &a, &b, &c) == 3) { s7034_k[0] = a; s7034_k[1] = b; s7034_k[2] = c; } else s7034_k[0] = s7034_k[1] = s7034_k[2] = (float)atof(k); }
        fprintf(stderr, "[s7034] offmapcull K=%g,%g,%g\n", s7034_k[0], s7034_k[1], s7034_k[2]);
        /* s7056 level-scoped K: ROGUESQ_DD_OFFMAPCULL_KLEVEL=<lvl>:<k>[,<lvl>:<k>...] overrides K on those levels (gCurrentLevel word
           0x80130B70, docs/game-architecture.md). _KLEVEL_TOG=1 (needs tog3): phase 1 ignores it (same-run on/off/on). */
        for (int i = 0; i < 3; i++) s7056_base[i] = s7034_k[i];
        if (const char* kl = getenv("ROGUESQ_DD_OFFMAPCULL_KLEVEL")) { const char* q = kl;
            while (q && *q) { int l = -1; float k = -1; if (sscanf(q, "%d:%f", &l, &k) == 2 && l >= 0 && l < 32) s7056_kl[l] = k; q = strchr(q, ','); if (q) q++; } }
        { const char* t = getenv("ROGUESQ_DD_OFFMAPCULL_KLEVEL_TOG"); s7056_tog = t && t[0] == '1'; }
        fprintf(stderr, "[s7056] klevel=%s tog=%d\n", getenv("ROGUESQ_DD_OFFMAPCULL_KLEVEL") ? getenv("ROGUESQ_DD_OFFMAPCULL_KLEVEL") : "(none)", s7056_tog);
        if (const char* ke = getenv("ROGUESQ_DD_OFFMAPCULL_KEDGE")) {
            if (strchr(ke, ';')) { const char* q = ke; for (int i = 0; i < 3 && q; i++) { float a = -1; int n = 8; const int c = sscanf(q, "%f,%d", &a, &n);
                    if (c >= 1 && a > 0) { s7046_k2[i] = a; s7046_n[i] = c >= 2 ? n : 8; } q = strchr(q, ';'); if (q) q++; } s7046_mask = 7; }
            else { float a = -1; int n = 8, m = 7; const int c = sscanf(ke, "%f,%d,%d", &a, &n, &m);
                if (c >= 1 && a > 0) { for (int i = 0; i < 3; i++) { s7046_k2[i] = a; s7046_n[i] = c >= 2 ? n : 8; } s7046_mask = c >= 3 ? m : 7; } } }
        fprintf(stderr, "[s7046] kedge k2=%g,%g,%g N=%d,%d,%d mask=%d\n", s7046_k2[0], s7046_k2[1], s7046_k2[2], s7046_n[0], s7046_n[1], s7046_n[2], s7046_mask);
        fprintf(stderr, "[s7031] offmapcull R=%d,%d,%d tog3=%d\n", s7031_R[0], s7031_R[1], s7031_R[2], s7030_tog3);
        fprintf(stderr, "[s7030] fogcull tog3=%d k=%g,%g,%g a0=0x%08X\n", s7030_tog3, s7030_k[0], s7030_k[1], s7030_k[2], a0); }
    auto rf = [&](uint32_t a) { uint32_t v = (uint32_t)MEM_W(0, (int64_t)(int32_t)a); float f; memcpy(&f, &v, 4); return f; };
    const float ex = rf(a0), ez = rf(a0 + 8); float fx = 0, fz = 0;
    for (uint32_t i = 0; i < 4; i++) { fx += rf(0x80130C1Cu + 12 * i) - ex; fz += rf(0x80130C1Cu + 12 * i + 8) - ez; }
    const float n = sqrtf(fx * fx + fz * fz); if (n > 1e-6f) { fx /= n; fz /= n; } else { fx = 0; fz = 1; }
    g_rs64_s7030_f[0] = fx; g_rs64_s7030_f[1] = fz;
    { const uint32_t lv = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80130B70); /* s7056: gCurrentLevel */
      for (int i = 0; i < 3; i++) s7034_k[i] = (lv < 32 && s7056_kl[lv] > 0 && !(s7056_tog && i == 1)) ? s7056_kl[lv] : s7056_base[i];
      if (lv != s7056_last) { s7056_last = lv; fprintf(stderr, "[s7056] level=%u k=%g,%g,%g\n", lv, s7034_k[0], s7034_k[1], s7034_k[2]); } }
    s7031_w = (int)(uint16_t)(MEM_W(0, (int64_t)(int32_t)0x80136DF8) >> 16); s7031_hgt = (int)(uint16_t)MEM_W(0, (int64_t)(int32_t)0x80136DF8); /* dims +0x38/+0x3A (BE halves) */
    const uint64_t mt = mach_absolute_time(); s7030_ph = s7030_tog3 ? (int)((mt / 24000000u) % 3u) : 0;
    s7030_fe = g_rs64_s7030_fe; s7030_thr = s7030_k[s7030_ph] > 0 && s7030_fe > 0 ? s7030_k[s7030_ph] * s7030_fe : 0.0f;
    float F = 0; for (uint32_t i = 0; i < 4; i++) F += (rf(0x80130C1Cu + 12 * i) - ex) * fx + (rf(0x80130C1Cu + 12 * i + 8) - ez) * fz;
    rs64_s7032_frame(); rs64_s7033_frame(rdram, a0);
    if (s7031_w > 0 && s7031_hgt > 0 && s7032_eyering == 0) { int e = s7032_eyex; const int ex2 = s7031_w - 1 - s7032_eyex, ez1 = s7032_eyez, ez2 = s7031_hgt - 1 - s7032_eyez;
        if (ex2 < e) e = ex2; if (ez1 < e) e = ez1; if (ez2 < e) e = ez2; s7046_ed[s7030_ph][e < 0 ? 0 : e > 31 ? 31 : e]++; }
    s7030_frames[s7030_ph]++; s7030_F[s7030_ph] += F * 0.25f; s7030_FE[s7030_ph] += s7030_fe;
    if (!s7030_t0) { s7030_t0 = s7030_last = mt; if (s7030_tog3) rs64_tog_anchor(mt); } /* anchor for g5e_cost_by_parity --phases 3 */
    if (mt - s7030_last > 240000000ull) { s7030_last = mt;
        for (int p = 0; p < 3; p++) { const double fr = s7030_frames[p] ? (double)s7030_frames[p] : 1.0; uint64_t tot = 0; for (int b = 0; b < 20; b++) tot += s7030_h[p][b];
            char buf[400]; int o = 0; for (int b = 0; b < 20; b++) o = rs64_apf(buf, sizeof buf, o, "%s%.1f", b ? "," : "", s7030_h[p][b] / fr);
            fprintf(stderr, "[s7030] t=%.0f ph=%d k=%g frames=%llu cells/f=%.1f cull/f=%.1f F=%.1f fe=%.1f hist/f=%s\n", (mt - s7030_t0) / 24e6, p, s7030_k[p],
                    (unsigned long long)s7030_frames[p], tot / fr, s7030_cull[p] / fr, s7030_F[p] / fr, s7030_FE[p] / fr, buf);
            o = 0; for (int b = 0; b < 20; b++) o = rs64_apf(buf, sizeof buf, o, "%s%.1f", b ? "," : "", s7031_off[p][b] / fr);
            char rb[300], rb2[300]; int o1 = 0, o2 = 0; for (int b = 0; b < 18; b++) { o1 = rs64_apf(rb, sizeof rb, o1, "%s%.1f", b ? "," : "", s7031_ring[p][b] / fr);
                o2 = rs64_apf(rb2, sizeof rb2, o2, "%s%.1f", b ? "," : "", s7031_rband[p][b] / fr); }
            fprintf(stderr, "[s7033] t=%.0f ph=%d eb=%.2f sc=%.4f eyecell=%d..%d up=%d upc=%llu/%llu keep/f=%.1f pass/f=%.1f\n", (mt - s7030_t0) / 24e6, p, s7033_eb, s7033_sc,
                    s7033_emin, s7033_emax, s7033_up, (unsigned long long)s7033_upc[1], (unsigned long long)s7033_upc[0], s7033_keep[p] / fr, s7033_pass[p] / fr);
            { char kb[300]; int ok = 0; for (int b = 0; b < 20; b++) ok = rs64_apf(kb, sizeof kb, ok, "%s%.1f", b ? "," : "", s7034_kc[p][b] / fr);
              fprintf(stderr, "[s7034] t=%.0f ph=%d K=%g kept/f=%.1f chist/f=%s\n", (mt - s7030_t0) / 24e6, p, s7034_k[p], s7034_kk[p] / fr, kb); }
            { char eb[300]; int oe = 0; uint64_t en = 0; for (int b = 0; b < 32; b++) en += s7046_ed[p][b]; const double ed = en ? (double)en : 1.0;
              for (int b = 0; b < 32; b++) oe = rs64_apf(eb, sizeof eb, oe, "%s%.2f", b ? "," : "", s7046_ed[p][b] / ed);
              fprintf(stderr, "[s7046] t=%.0f ph=%d k2=%g N=%d on=%d k2cells/f=%.1f k2cull/f=%.1f eyeedge=%s\n", (mt - s7030_t0) / 24e6, p, s7046_k2[p], s7046_n[p],
                      (s7046_k2[p] > 0 && ((s7046_mask >> p) & 1)) ? 1 : 0, s7046_kc[p] / fr, s7046_kcull[p] / fr, eb); }
            fprintf(stderr, "[s7032] t=%.0f ph=%d eye=%d,%d ring=%d eyeoff_cells/f=%.1f spread_bad=%llu\n", (mt - s7030_t0) / 24e6, p, s7032_eyex, s7032_eyez, s7032_eyering, s7032_eyeoff[p] / fr, (unsigned long long)s7032_spread_bad);
            fprintf(stderr, "[s7031] t=%.0f ph=%d R=%d dims=%dx%d win=%d,%d ocull/f=%.1f off/f=%s ring/f=%s rband/f=%s\n", (mt - s7030_t0) / 24e6, p, s7031_R[p], s7031_w, s7031_hgt,
                    (int32_t)MEM_W(0, (int64_t)(int32_t)0x80132DB0), (int32_t)MEM_W(0, (int64_t)(int32_t)0x80132DB8), s7031_cull[p] / fr, buf, rb, rb2); } }
}
extern "C" int rs64_s7030_cell(float d);
extern "C" int rs64_s7031_cell(float d, int32_t x, int32_t z);
extern "C" int rs64_s7032_cell(float ox, float oz, float d, int32_t x, int32_t z) {
    { const int R = s7031_R[s7030_ph];
      if ((s7033_on == 1 || (s7033_on == 2 && s7030_ph == 1)) && R >= 0 && (x < 0 || x >= s7031_w || z < 0 || z >= s7031_hgt)) {
        const int dx = x < 0 ? -x : x >= s7031_w ? x - s7031_w + 1 : 0, dz = z < 0 ? -z : z >= s7031_hgt ? z - s7031_hgt + 1 : 0;
        if ((dx > dz ? dx : dz) > R) { int mn, mx; rs64_s7033_hr(x, z, &mn, &mx); const int top = s7033_up > 0 ? mx : mn;
            if (((float)top - s7033_eb) * (float)s7033_up > s7033_m) s7033_pass[s7030_ph]++; /* eye below the top: cull stands */
            else { s7033_keep[s7030_ph]++; s7031_R[s7030_ph] = -1; const int r = rs64_s7031_cell(d, x, z); s7031_R[s7030_ph] = R; return r; } } } }
    const float e0x = (float)x - ox, e0z = (float)z - oz, e1x = (float)x + ox, e1z = (float)z + oz;
    if (e0x < s7032_mn[0][0]) s7032_mn[0][0] = e0x; if (e0x > s7032_mx[0][0]) s7032_mx[0][0] = e0x; if (e0z < s7032_mn[0][1]) s7032_mn[0][1] = e0z; if (e0z > s7032_mx[0][1]) s7032_mx[0][1] = e0z;
    if (e1x < s7032_mn[1][0]) s7032_mn[1][0] = e1x; if (e1x > s7032_mx[1][0]) s7032_mx[1][0] = e1x; if (e1z < s7032_mn[1][1]) s7032_mn[1][1] = e1z; if (e1z > s7032_mx[1][1]) s7032_mx[1][1] = e1z;
    if (s7032_gate > 0 && s7032_eyering > 0) { s7032_eyeoff[s7030_ph]++; const int R = s7031_R[s7030_ph]; s7031_R[s7030_ph] = -1; const int r = rs64_s7031_cell(d, x, z); s7031_R[s7030_ph] = R; return r; }
    return rs64_s7031_cell(d, x, z);
}
extern "C" int rs64_s7031_cell(float d, int32_t x, int32_t z) {
    const float dn = d - 0.71f; const int p = s7030_ph;
    const int b = s7030_fe > 0 ? (int)(dn / s7030_fe * 10.0f) : 0; const int bc = b < 0 ? 0 : b > 19 ? 19 : b;
    const int off = x < 0 || x >= s7031_w || z < 0 || z >= s7031_hgt;
    if (off) { const int dx = x < 0 ? -x : x >= s7031_w ? x - s7031_w + 1 : 0, dz = z < 0 ? -z : z >= s7031_hgt ? z - s7031_hgt + 1 : 0;
        const int r = dx > dz ? dx : dz; const int rc = r > 17 ? 17 : r; s7031_off[p][bc]++; s7031_ring[p][rc]++; if (bc >= 5 && bc < 10) s7031_rband[p][rc]++;
        if (s7031_R[p] >= 0 && r > s7031_R[p]) {
            float K = s7034_k[p]; int k2 = 0;
            if (s7046_k2[p] > 0 && ((s7046_mask >> p) & 1) && s7032_eyering == 0) { /* s7046: near-side cells use k2 */
                const int N = s7046_n[p]; if ((x < 0 && s7032_eyex < N) || (x >= s7031_w && s7031_w - 1 - s7032_eyex < N) ||
                                            (z < 0 && s7032_eyez < N) || (z >= s7031_hgt && s7031_hgt - 1 - s7032_eyez < N)) { K = s7046_k2[p]; k2 = 1; s7046_kc[p]++; } }
            if (K > 0 && !(s7030_fe > 0 && dn > K * s7030_fe)) s7034_kk[p]++; /* s7034: too near, keep */
            else { s7030_h[p][bc]++; s7031_cull[p]++; s7034_kc[p][bc]++; if (k2) s7046_kcull[p]++; return 1; } } }
    return rs64_s7030_cell(d);
}
extern "C" int rs64_s7030_cell(float d) {
    d -= 0.71f; /* near edge of a unit cell */
    if (s7030_fe > 0) { int b = (int)(d / s7030_fe * 10.0f); b = b < 0 ? 0 : b > 19 ? 19 : b; s7030_h[s7030_ph][b]++; }
    if (s7030_thr > 0 && d > s7030_thr) { s7030_cull[s7030_ph]++; return 1; }
    return 0;
}
extern "C" int rs64_dd_scene_update(int level) {
    static int mode = -1, last = -1, last_level = -1000;
    if (mode < 0) { const char* e = getenv("ROGUESQ_DD_CINE_GATE"); mode = !(e && *e) ? 1 : (e[0] == 't' ? 2 : (e[0] != '0')); }
    int gate = mode == 1 || (mode == 2 && ((mach_absolute_time() / 96000000u) & 1u));
    int on = !(gate && (level < 0 || level > 18));
    if (on != last || level != last_level) { fprintf(stderr, "[ddscene] level=%d gate=%d on=%d\n", level, gate, on); last = on; last_level = level; }
    return on;
}
// s7009 G5e widewin (tools/apply_s7009_widewin.py): the dd>1 terrain window may grow to N cells per axis, with the span/slot tables
// moved to 0x83000000 at a 128 stride. g_rs64_ww is latched per binPolygonIntoTerrainGrid call. ROGUESQ_DD_WIDEWIN=1|tog, _N=64..128.
// s7017: same-run tog arm of a mach second. The s7010 plain parity (sec & 1) is biased by the harness autopilot's 2 s press cycle
// (a, sl, a, sr: an 8 s cycle; A/A null odd-even rsp -0.55..-0.70 ms in 3/3 runs). xor8 = (sec ^ sec>>3) & 1 still alternates every
// second but flips the pattern every 8 s, so any 8 s-periodic load cancels exactly over 16 s (same A/A runs offline: |delta| <= 0.11 ms
// at every shift). ROGUESQ_TOG_SPLIT=parity restores the old split. rs64_tog_anchor prints the one [s7010-clk] line, carrying split=.
extern "C" int rs64_tog_xor8(void) { static int m = -1; if (m < 0) { const char* e = getenv("ROGUESQ_TOG_SPLIT"); m = (e && *e == 'p') ? 0 : 1; } return m; }
extern "C" int rs64_tog_odd(uint64_t mt) { const uint64_t s = mt / 24000000u; return (int)((rs64_tog_xor8() ? (s ^ (s >> 3)) : s) & 1u); }
extern "C" void rs64_tog_anchor(uint64_t mt) {
    static std::atomic<int> once{0}; if (once.exchange(1)) return;
    const long long su = (long long)std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
    fprintf(stderr, "[s7010-clk] steady_us=%lld mach=%llu split=%s\n", su, (unsigned long long)mt, rs64_tog_xor8() ? "xor8" : "parity");
}
// s7021 G1c: force the gated e9prov route counters back on in the owner-path ucode arms (tools/fixup_factor5_ucode.py s7021 block).
// ROGUESQ_E9PROV_FORCE=1 always, =tog odd xor8 seconds (same [s7010-clk] anchor), default 0. Updated once per gfx task (main.cpp).
extern "C" { int rs64_e9prov_force = 0; }
extern "C" void rs64_e9prov_force_update(void) {
    static int m = -1;
    if (m < 0) { const char* e = getenv("ROGUESQ_E9PROV_FORCE"); m = !(e && *e) ? 0 : (e[0] == 't' ? 2 : (e[0] != '0'));
        fprintf(stderr, "[s7021] e9prov_force mode=%d\n", m); }
    if (m == 2) { const uint64_t mt = mach_absolute_time(); static int anc = 0; if (!anc) { anc = 1; rs64_tog_anchor(mt); }
        rs64_e9prov_force = rs64_tog_odd(mt); }
    else rs64_e9prov_force = m;
}
extern "C" { int g_rs64_ww = 0; }
extern "C" int rs64_s7009_arm(void) {
    static int m = -1; if (m < 0) { const char* e = getenv("ROGUESQ_DD_WIDEWIN"); m = !(e && *e) ? 0 : (e[0] == 't' ? (e[3] == '3' ? 3 : 2) : (e[0] != '0')); }
    if (m == 3) return 1; /* s7012 tog3: window always wide, rs64_s7012_cap cycles the area cap */
    if (m == 2) { static int last = -1; const uint64_t mt = mach_absolute_time(); const int on = rs64_tog_odd(mt);
        if (last < 0) rs64_tog_anchor(mt); /* s7010: clock anchor so steady_clock-stamped rings (G1E_TL) can be split by tog arm */
        if (on != last) { last = on; } return on; }
    return m;
}
// s7011 G5e lodmul (tools/apply_s7011_lodmul.py): LOD tier thresholds 0x8009DE94..A0 x ROGUESQ_DD_LODMUL in flight at dd>1;
// ROGUESQ_DD_LODMUL_TOG=1 = odd mach seconds only (same parity + [s7010-clk] anchor as WIDEWIN=tog).
extern "C" int rs64_s7011_en(void) { static int en = -1; if (en < 0) { const char* e = getenv("ROGUESQ_DD_LODMUL"); en = (e && *e && atof(e) > 0.0) ? 1 : 0; } return en; }
extern "C" float rs64_s7011_lodmul(void) {
    static float m = -1.0f; static int tg = -1;
    if (m < 0.0f) { const char* e = getenv("ROGUESQ_DD_LODMUL"); m = (e && *e) ? (float)atof(e) : 1.0f; if (m <= 0.0f) m = 1.0f;
        const char* g = getenv("ROGUESQ_DD_LODMUL_TOG"); tg = (g && *g && *g != '0') ? 1 : 0; fprintf(stderr, "[s7011] lodmul=%g tog=%d\n", m, tg); }
    if (!tg) return m;
    const uint64_t mt = mach_absolute_time(); static int anc = 0;
    if (!anc) { anc = 1; rs64_tog_anchor(mt); }
    return rs64_tog_odd(mt) ? m : 1.0f;
}
// s7012 G5e (tools/apply_s7012_widewin_cap.py): ROGUESQ_DD_WIDEWIN_CAP=a[,b,c] caps the wide window's cell area; with
// ROGUESQ_DD_WIDEWIN=tog3 the cap cycles a/b/c on (mach/24e6) % 3 seconds. 0 = no host cap.
extern "C" int rs64_s7012_cap(void) {
    /* s7374 class AR: was two plain lazy-init blocks (n=-1 / clinit=0) publishing v[], tog3, cl[], cltog; reached from the guest
       thread and the gfx thread (factor5_gfx_runner under S7026, rs64_g1e_tring_push under G1B), so a second thread could see
       n/clinit set with v[]/cl[] still zero, or race v[n++] past v[2]. Now one thread-safe magic static, same values. */
    struct Cfg { int n = 0; int v[3] = {0, 0, 0}; int tog3 = 0; int cl[32] = {0}; int cltog = 0; };
    static const Cfg cfg = [] { Cfg c; const char* e = getenv("ROGUESQ_DD_WIDEWIN_CAP");
        while (e && *e && c.n < 3) { c.v[c.n++] = atoi(e); const char* q = strchr(e, ','); e = q ? q + 1 : nullptr; }
        const char* w = getenv("ROGUESQ_DD_WIDEWIN"); c.tog3 = (w && w[0] == 't' && w[1] && w[2] && w[3] == '3');
        fprintf(stderr, "[s7012] widewin cap n=%d %d,%d,%d tog3=%d\n", c.n, c.v[0], c.v[1], c.v[2], c.tog3);
        /* s7061 level-scoped cap: ROGUESQ_DD_WIDEWIN_CAPLEVEL=<lvl>:<cells>[,...] caps those levels (gCurrentLevel as latched by
           rs64_s7030_begin, s7056_last). _CAPLEVEL_TOG=1 (needs WIDEWIN=tog3): phase 1 ignores it (same-run on/off/on). */
        if (const char* q = getenv("ROGUESQ_DD_WIDEWIN_CAPLEVEL")) while (q && *q) { int l = -1, k = 0;
            if (sscanf(q, "%d:%d", &l, &k) == 2 && l >= 0 && l < 32 && k > 0) c.cl[l] = k; q = strchr(q, ','); if (q) q++; }
        { const char* g = getenv("ROGUESQ_DD_WIDEWIN_CAPLEVEL_TOG"); c.cltog = g && g[0] == '1'; }
        fprintf(stderr, "[s7061] widewin caplevel=%s tog=%d\n", getenv("ROGUESQ_DD_WIDEWIN_CAPLEVEL") ? getenv("ROGUESQ_DD_WIDEWIN_CAPLEVEL") : "(none)", c.cltog);
        return c; }();
    const int n = cfg.n, tog3 = cfg.tog3, cltog = cfg.cltog; const int* v = cfg.v; const int* cl = cfg.cl;
    int ph = 0;
    if (tog3) { const uint64_t mt = mach_absolute_time(); static std::atomic<int> anc{0};
        if (!anc.exchange(1)) rs64_tog_anchor(mt);  /* tog3 cycles on sec %% 3, not on the s7017 split; s7374 once across threads */
        ph = (int)((mt / 24000000u) % 3u); }
    const int base = n == 0 ? 0 : (tog3 ? v[ph % n] : v[0]);
    const uint32_t lv = s7056_last;
    if (lv < 32 && cl[lv] > 0 && !(cltog && tog3 && ph == 1) && (base == 0 || cl[lv] < base)) return cl[lv];
    return base;
}
// s7022 G1c (tools/apply_s7022_streamtime.py): per-call timing of streamTerrainGridCellsByDistance, ROGUESQ_S7022_ST=1.
// Buckets by the s7012 cap value (tog3 phase); prints one [s7022-st] line per bucket per 256 calls. Ticks are mach (24 MHz here).
extern "C" { int g_rs64_s7022 = [] { const char* e = getenv("ROGUESQ_S7022_ST"); return (e && *e && *e != '0') ? 1 : 0; }(); }
extern "C" void rs64_s7022_st(unsigned long long t0, unsigned long long t1, unsigned long long t2, unsigned it, unsigned rw) {
    struct B { int cap; unsigned n; unsigned long long su, lo, it, rw, w0, w1; };
    static B b[4]; static int nb = 0; static double tb = 0;
    if (tb == 0) { mach_timebase_info_data_t i; mach_timebase_info(&i); tb = (double)i.numer / i.denom; }
    const int cap = rs64_s7012_cap(); int k = 0;
    while (k < nb && b[k].cap != cap) k++;
    if (k == nb) { if (nb == 4) return; b[nb++] = B{cap, 0, 0, 0, 0, 0, 0, 0}; }
    B& x = b[k]; if (!t1) t1 = t2;
    if (!x.n) x.w0 = t0;
    x.n++; x.su += t1 - t0; x.lo += t2 - t1; x.it += it; x.rw += rw; x.w1 = t2;
    if (x.n == 256) {
        const double n = x.n;
        fprintf(stderr, "[s7022-st] cap=%d calls=%u span_s=%.2f setup_us=%.2f loop_us=%.2f tot_us=%.2f cells=%.1f rows=%.1f ns_per_cell=%.2f\n",
                x.cap, x.n, (x.w1 - x.w0) * tb * 1e-9, x.su * tb * 1e-3 / n, x.lo * tb * 1e-3 / n, (x.su + x.lo) * tb * 1e-3 / n,
                x.it / n, x.rw / n, x.it ? x.lo * tb / x.it : 0.0);
        x.n = 0; x.su = x.lo = x.it = x.rw = 0;
    }
}
// s7023 G1c (tools/apply_s7023_calleetime.py): callee/self split of the same loop, same switch. v[0..3] = getGridCellValueAt /
// processGridCellByDistance ticks + calls, v[4..5] call-path region ticks + entries, v[6..9] per-call deltas of g_s6493 [3] poolcap,
// [4] spaneq skip, [5] span reject, [6] call path. ovh_ns = one back-to-back mach_absolute_time pair (calibrated once): every timed
// span carries ~1 ovh; the summariser subtracts it. One [s7023-cs] line per cap bucket per 256 calls.
extern "C" int rs64_s6963_active(); extern "C" int rs64_s7025_both(); // s7024/s7025 bucket key
extern "C" { unsigned long long g_s7024[3][10]; }
/* s7025 (tools/apply_s7025_clampsplit.py): clampGridCellLookup split. [0,1] calls/ticks, [2,3] create path n/ticks, [4] retries,
   [5] pre calls, [6] pre ticks, [7] entry->answer ticks, [8] snapshot ticks, [9] snapshots, [10] snapshot records, [11] get ticks,
   [12] validate ticks, [13] hits, [14] misses, [15] ival, [16] sum r, [17] max r, [18] sum |r - r_prev|, [19] hits r >= 32768. */
/* [20] create pg ticks, [21] create gv-alloc ticks, [22] pg calls inside creates, [23] sendServiceMessage n, [24] its ticks, [25] sends inside creates */
extern "C" { unsigned long long g_s7025[32]; int g_s7025_in = 0; } // s7024 (tools/apply_s7024_gvbranch.py): [n, mach ticks, walk iters][branch]
extern "C" void rs64_s7023_cs(const unsigned long long* v) {
    struct B { int cap; unsigned n; unsigned long long a[10]; };
    static B b[4]; static int nb = 0; static double tb = 0, ovh = 0;
    if (tb == 0) { mach_timebase_info_data_t i; mach_timebase_info(&i); tb = (double)i.numer / i.denom;
        unsigned long long s = 0; for (int k = 0; k < 100000; k++) { unsigned long long a = mach_absolute_time(); s += mach_absolute_time() - a; }
        ovh = s * tb / 100000.0; }
    const int cap = rs64_s7012_cap() * 10 + rs64_s6963_active() + 1000000 * rs64_s7025_both(); int k = 0;  /* s7024: cap*10 + cellidx mode; s7025: +1e6 when CREATE_BOTH */
    while (k < nb && b[k].cap != cap) k++;
    if (k == nb) { if (nb == 4) return; b[nb] = B{}; b[nb].cap = cap; nb++; }
    B& x = b[k]; x.n++; for (int j = 0; j < 10; j++) x.a[j] += v[j];
    static unsigned long long s25[4][32]; for (int j = 0; j < 32; j++) { if (j == 17) { if (g_s7025[j] > s25[k][j]) s25[k][j] = g_s7025[j]; } else s25[k][j] += g_s7025[j]; g_s7025[j] = 0; }
    static unsigned long long s[4][3][10]; // s7024: per-branch getGridCellValueAt totals, flushed into this cap bucket
    for (int r = 0; r < 3; r++) for (int j = 0; j < 10; j++) { s[k][r][j] += g_s7024[r][j]; g_s7024[r][j] = 0; }
    if (x.n == 256) {
        { const double n = x.n; char buf[512]; int o = snprintf(buf, sizeof buf, "[s7024-gv] cap=%d calls=%u", x.cap, x.n);
          for (int j = 1; j < 10; j++) if (s[k][0][j]) o = rs64_apf(buf, sizeof buf, o, " b%d=%.1f/%.1fns/w%.2f", j, s[k][0][j] / n,
              s[k][1][j] * tb / s[k][0][j], (double)s[k][2][j] / s[k][0][j]);
          fprintf(stderr, "%s\n", buf); for (int r = 0; r < 3; r++) for (int j = 0; j < 10; j++) s[k][r][j] = 0; }
        { const unsigned long long* q = s25[k]; const double n = x.n; auto ns = [&](int a, int b) { return q[b] ? q[a] * tb / q[b] : 0.0; };
          fprintf(stderr, "[s7025-cl] cap=%d calls=%u cl_n=%.1f cl_ns=%.1f cr_n=%.1f cr_ns=%.1f retry=%.1f pre_n=%.1f pre_ns=%.1f ent_ns=%.1f snap_n=%.2f snap_us=%.2f snap_rec=%.1f get_ns=%.1f val_ns=%.1f hit=%.1f miss=%.1f ival=%.2f r_mean=%.0f r_max=%llu r_step=%.0f r_hi=%.3f\n",
                  x.cap, x.n, q[0] / n, ns(1, 0), q[2] / n, ns(3, 2), q[4] / n, q[5] / n, ns(6, 5), ns(7, 5), q[9] / n, q[9] ? q[8] * tb * 1e-3 / q[9] : 0.0,
                  q[9] ? (double)q[10] / q[9] : 0.0, ns(11, 5), ns(12, 13), q[13] / n, q[14] / n, q[15] / n, q[13] ? (double)q[16] / q[13] : 0.0, q[17],
                  q[13] ? (double)q[18] / q[13] : 0.0, q[13] ? (double)q[19] / q[13] : 0.0);
          fprintf(stderr, "[s7025-cr] cap=%d calls=%u cr_n=%.1f cr_pg_ns=%.1f cr_gv_ns=%.1f cr_pgcalls=%.2f send_n=%.1f send_ns=%.1f send_in_cr=%.2f\n", x.cap, x.n,
                  q[2] / n, ns(20, 2), ns(21, 2), q[2] ? (double)q[22] / q[2] : 0.0, q[23] / n, ns(24, 23), q[2] ? (double)q[25] / q[2] : 0.0);
          for (int j = 0; j < 32; j++) s25[k][j] = 0; }
        const double n = x.n;
        fprintf(stderr, "[s7023-cs] cap=%d calls=%u ovh_ns=%.2f gv_us=%.2f gv_n=%.1f pg_us=%.2f pg_n=%.1f cp_us=%.2f cp_n=%.1f poolcap=%.1f spaneq=%.1f rej=%.1f callp=%.1f\n",
                x.cap, x.n, ovh, x.a[0] * tb * 1e-3 / n, x.a[1] / n, x.a[2] * tb * 1e-3 / n, x.a[3] / n, x.a[4] * tb * 1e-3 / n, x.a[5] / n,
                x.a[6] / n, x.a[7] / n, x.a[8] / n, x.a[9] / n);
        x.n = 0; for (int j = 0; j < 10; j++) x.a[j] = 0;
    }
}
extern "C" int rs64_s7009_n(void) {
    static int n = -1; if (n < 0) { const char* e = getenv("ROGUESQ_DD_WIDEWIN_N"); n = (e && *e) ? atoi(e) : 128; if (n < 64) n = 64; if (n > 128) n = 128; }
    return n;
}
// s7233 G1c (tools/apply_s7233_widewin_r.py): WIDEWIN-only eye-distance limit. ROGUESQ_DD_WIDEWIN_R=<cells> (0/unset = off),
// _R_TOG=1 = only on rs64_tog_odd seconds (same [s7010-clk] anchor). rs64_s7233_win is called once per wide placement with the
// retail-equivalent window (min(w,64) x min(d,64), same fwdwin rule) and the eye in cell units; rs64_s7233_cell is asked for every
// non-empty cell of the stream loop and returns 1 = skip (cell outside the retail-equivalent window AND centre > R from the eye).
// One [s7233] line per 128 placements per phase: wide-only non-empty cells per call by 8-cell eye-distance bin, and skipped per call.
extern "C" { int g_rs64_s7233_r = 0; int g_rs64_s7233_wr = 0; }
namespace { int s7233_x0, s7233_x1, s7233_z0, s7233_z1; float s7233_ex, s7233_ez; int s7233_ph; unsigned long long s7233_h[2][17], s7233_sk[2], s7233_in[2]; unsigned s7233_n[2]; int s7233_lp; }
extern "C" void rs64_s7233_win(int x0, int x1, int z0, int z1, float ex, float ez) {
    static int r = -1, tg = 0, r3[3] = {0, 0, 0};
    if (r < 0) { const char* e = getenv("ROGUESQ_DD_WIDEWIN_R"); r = (e && *e) ? atoi(e) : 0; if (r < 0) r = 0;
        const char* g = getenv("ROGUESQ_DD_WIDEWIN_R_TOG"); tg = (g && *g == '1') ? 1 : (g && *g == '3') ? 3 : 0;
        /* s7270: _R_TOG=3 cycles R over ROGUESQ_DD_WIDEWIN_R3=a,b,c on (mach s)%3 (the s7030/s7039 tog3 clock, g5h_toggle_rank3);
           a phase with R<=0 is the off phase (tally only). r becomes the largest phase value so the tally gate stays armed. */
        if (tg == 3) { const char* v = getenv("ROGUESQ_DD_WIDEWIN_R3"); if (v) sscanf(v, "%d,%d,%d", &r3[0], &r3[1], &r3[2]);
            r = 0; for (int i = 0; i < 3; i++) { if (r3[i] < 0) r3[i] = 0; if (r3[i] > r) r = r3[i]; } }
        fprintf(stderr, "[s7233] widewin_r=%d tog=%d r3=%d,%d,%d\n", r, tg, r3[0], r3[1], r3[2]); }
    int ph = 1, rr = r;
    /* s7287: level-scoped R, ROGUESQ_DD_WIDEWIN_RLEVEL=<lvl>:<R>[,...] (gCurrentLevel latched as s7056_last, as _CAPLEVEL does).
       Only with a plain R (tg 0) in force. s7287 (L12 16:9 dd6, AC, control ctl STACK=0+DUTY flat 30 for 120 s PASS): r88 win77-97
       49.1/s 15.53 ms, flat 30 t=77-84 (s7286 the same, 2 runs) vs r48 60.0/s 10.95 ms at equal cells/call (3521 vs 3509). */
    { static int rl[32]; static int rlinit = 0; static uint32_t rllast = 0xFFFFFFFFu;
      if (!rlinit) { rlinit = 1; for (int i = 0; i < 32; i++) rl[i] = 0;
          if (const char* q = getenv("ROGUESQ_DD_WIDEWIN_RLEVEL")) while (q && *q) { int l = -1, v = 0;
              if (sscanf(q, "%d:%d", &l, &v) == 2 && l >= 0 && l < 32 && v > 0) rl[l] = v; q = strchr(q, ','); if (q) q++; }
          fprintf(stderr, "[s7287] widewin rlevel=%s\n", getenv("ROGUESQ_DD_WIDEWIN_RLEVEL") ? getenv("ROGUESQ_DD_WIDEWIN_RLEVEL") : "(none)"); }
      const uint32_t lv = s7056_last;
      if (tg == 0 && r > 0 && lv < 32 && rl[lv] > 0) rr = rl[lv];
      if (lv != rllast) { rllast = lv; fprintf(stderr, "[s7287] level=%u widewin_r=%d\n", lv, rr); } }
    if (tg == 1) { const uint64_t mt = mach_absolute_time(); static int anc = 0; if (!anc) { anc = 1; rs64_tog_anchor(mt); } ph = rs64_tog_odd(mt); }
    else if (tg == 3) { const uint64_t mt = mach_absolute_time(); static int anc = 0; if (!anc) { anc = 1; rs64_tog_anchor(mt); }
        rr = r3[(mt / 24000000u) % 3u]; ph = rr > 0; }

    /* the tally runs whenever the knob is configured (r > 0), so the off phase is histogrammed too */
    /* s7236: flush per phase every 2 s of host time (or 128 calls), calls=<actual>. The s7233 fixed 128-call flush never fired: placements
       are far rarer than VIs (s7233 r40: 521 wr=40 VIs, 0 [s7233] lines), so the soak's positive control would have read empty. The
       counts accumulated here belong to the PREVIOUS placement (cells are asked after win()), which is why the flush precedes the latch. */
    if (r > 0) { static uint64_t last[2] = {0, 0}; const uint64_t now = mach_absolute_time(); const int lp = s7233_lp;
        if (s7233_n[lp] && (s7233_n[lp] >= 128 || now - last[lp] >= 48000000ull)) {
            const double n = (double)s7233_n[lp];
            char buf[512]; int o = snprintf(buf, sizeof buf, "[s7233] ph=%d r=%d calls=%u in=%.1f skip=%.1f wide_by_d8=", lp, lp ? r : 0, s7233_n[lp], s7233_in[lp] / n, s7233_sk[lp] / n);
            for (int i = 0; i < 17; i++) o = rs64_apf(buf, sizeof buf, o, "%s%.1f", i ? "," : "", s7233_h[lp][i] / n);
            fprintf(stderr, "%s\n", buf); s7233_n[lp] = 0; s7233_sk[lp] = s7233_in[lp] = 0; for (int i = 0; i < 17; i++) s7233_h[lp][i] = 0; last[lp] = now; }
        if (!last[ph]) last[ph] = now; }
    s7233_x0 = x0; s7233_x1 = x1; s7233_z0 = z0; s7233_z1 = z1; s7233_ex = ex; s7233_ez = ez; s7233_ph = s7233_lp = ph;
    g_rs64_s7233_r = (rr > 0 && ph) ? rr : 0; g_rs64_s7233_wr = g_rs64_s7233_r;
    if (r > 0) { s7233_n[ph]++; g_rs64_s7233_r = g_rs64_s7233_r ? g_rs64_s7233_r : -1; } /* -1 = tally only (off phase) */
}
extern "C" int rs64_s7233_cell(int wx, int wz) {
    const int r = g_rs64_s7233_r; if (!r) return 0;
    const int ph = s7233_ph;
    if (wx >= s7233_x0 && wx < s7233_x1 && wz >= s7233_z0 && wz < s7233_z1) { s7233_in[ph]++; return 0; }
    const float dx = (float)wx + 0.5f - s7233_ex, dz = (float)wz + 0.5f - s7233_ez; const float dd = sqrtf(dx * dx + dz * dz);
    int b = dd < 128.0f ? (int)(dd / 8.0f) : 16; /* [s7347] NaN / huge dd -> bin 16 (no (int)NaN index) */ s7233_h[ph][b]++;
    if (r > 0 && dd > (float)r) { s7233_sk[ph]++; return 1; }
    return 0;
}
// s7240 G1c (tools/apply_s7239_widewin_merge.py, design docs/WIDEWIN-MERGE-PLAN.md): WIDEWIN far-terrain 2x2 merge mesh.
// ROGUESQ_DD_WIDEWIN_MERGE=<frac> (0/unset = off), _MERGE_TOG=1 = only on rs64_tog_odd seconds. While g_rs64_ww is set, four flat lod-2
// cells of one face group forming an aligned 2x2 block (anchor floor(x/V0), floor(z/V0) even; same V0/material/w0 bits), all with node
// dist2 >= frac^2 * farcut (0x8009DEB4, the game's own far cutoff in dist2 units, compared at 0x800434E0), become ONE TRI_GEN: partners are
// captured at H3 and dropped at H4, the anchor is rewritten at H5 (rebased heights, partner corner colours, spacing 2*V0). Groups with the
// 0x40000000 patch-table flag are never touched. One [s7239] line per phase every 2 s (counts since the last line).
extern "C" { int g_rs64_s7239_on = 0; int g_rs64_s7239_act = 0; int g_rs64_s7239_skip = 0; int g_rs64_s7239_wm = 0; }
namespace {
inline uint32_t s7239_rw(const uint8_t* rd, uint32_t a) { return *reinterpret_cast<const uint32_t*>(rd + (a - 0x80000000u)); }
inline uint16_t s7239_rh(const uint8_t* rd, uint32_t a) { return *reinterpret_cast<const uint16_t*>(rd + ((a - 0x80000000u) ^ 2u)); }
inline uint8_t s7239_rb(const uint8_t* rd, uint32_t a) { return rd[(a - 0x80000000u) ^ 3u]; }
inline bool s7239_ok(uint32_t a) { return a >= 0x80000000u && a < 0x84000000u; }
constexpr uint32_t S7239_HN = 1u << 17;
uint32_t s7239_he[S7239_HN]; float s7239_hd[S7239_HN]; uint32_t s7239_hg[S7239_HN]; uint32_t s7239_hcnt; unsigned long long s7239_hclr;
// s7242: per-build-pass generation. H1 after any H2 starts a new pass; an entry from an older pass is a counted miss (stale), never a merge input.
uint32_t s7239_gen = 1; int s7239_emitted = 0; float s7239_pmax = 0.f;
inline uint32_t s7239_hash(uint32_t e) { return ((e >> 2) * 2654435761u) >> 15; }
bool s7239_dist(uint32_t e, float* d, bool* stale) {
    uint32_t h = s7239_hash(e);
    for (int k = 0; k < 64; k++, h = (h + 1) & (S7239_HN - 1)) { if (s7239_he[h] == e) { if (s7239_hg[h] != s7239_gen) { *stale = true; return false; } *d = s7239_hd[h]; return true; } if (!s7239_he[h]) return false; }
    return false; }
float s7239_frac = 0.f; int s7239_tg = 0; int s7239_m3[3] = {0, 1, 1};
struct S7239E { uint32_t e; int32_t x, z, yb, v; uint16_t mat; uint8_t b21, b2e, flat, role, dup, cap; int8_t h[4]; int32_t p[3]; uint32_t cmd; uint32_t w[10]; };
std::vector<S7239E> s7239_l; std::vector<std::pair<uint64_t, int32_t>> s7239_key, s7239_el;
enum { T_GRP, T_NOWW, T_FLAG, T_EL, T_FLAT, T_CAND, T_ANC, T_DROP, T_OVF, T_MISS, T_NEAR, T_UNM, T_DUP, T_MERGED, T_STALE, T_FLATE, T_FLATC, T_SHMIS, T_DH0, T_DH1, T_DH2, T_DH3, T_DH4, T_DH5, T_DH6, T_DH7, T_N };
// s7246 flatness gate: E = max |y_mid - avg(ends)| (emitted units, abs y = 16*(ybase+h)) over the 4 merged-edge midpoints (the T-junction
// gap a crack opens), C = centre vs both diagonals (view-dependent split, F5Rogue.cpp TriGen02). Defaults: E=0 (exact), C=E.
int32_t s7246_E = 0, s7246_C = 0;
struct S7246Init { S7246Init() { const char* e = getenv("ROGUESQ_DD_WIDEWIN_MERGE_E"); if (e && *e) s7246_E = atoi(e);
    const char* c = getenv("ROGUESQ_DD_WIDEWIN_MERGE_C"); s7246_C = (c && *c) ? atoi(c) : s7246_E; } } s7246_init;
// histogram edges of the edge deviation (emitted units) for candidates that pass every other gate, both phases: 0,8,16,32,64,128,256,inf
inline int s7246_bin(int32_t d) { const int32_t lim[7] = {0, 8, 16, 32, 64, 128, 256}; for (int i = 0; i < 7; i++) if (d <= lim[i]) return i; return 7; }
unsigned long long s7239_t[2][T_N]; int s7239_ph = 1; float s7239_farcut = 0.f, s7239_maxd2[2], s7239_thr = 0.f;
int32_t s7239_find(const std::vector<std::pair<uint64_t, int32_t>>& v, uint64_t k) {
    size_t lo = 0, hi = v.size(); while (lo < hi) { size_t m = (lo + hi) / 2; if (v[m].first < k) lo = m + 1; else hi = m; }
    return (lo < v.size() && v[lo].first == k) ? v[lo].second : -1; }
inline uint64_t s7239_k(int32_t x, int32_t z, int32_t v) { return ((uint64_t)(uint32_t)x << 40) ^ ((uint64_t)(uint32_t)(z & 0xFFFFF) << 20) ^ (uint64_t)(v & 0xFFFFF); }
inline int32_t s7239_fdiv(int32_t a, int32_t b) { int32_t q = a / b; if ((a % b) && ((a < 0) != (b < 0))) q--; return q; }
struct S7239Init { S7239Init() { const char* e = getenv("ROGUESQ_DD_WIDEWIN_MERGE"); s7239_frac = (e && *e) ? (float)atof(e) : 0.f;
    const char* g = getenv("ROGUESQ_DD_WIDEWIN_MERGE_TOG"); s7239_tg = (g && *g == '1') ? 1 : (g && *g == '3') ? 3 : 0;
    /* s7270: _MERGE_TOG=3 = merge on in the (mach s)%3 phases flagged by ROGUESQ_DD_WIDEWIN_MERGE3=a,b,c (default 0,1,1) */
    if (s7239_tg == 3) { const char* v = getenv("ROGUESQ_DD_WIDEWIN_MERGE3"); if (v) sscanf(v, "%d,%d,%d", &s7239_m3[0], &s7239_m3[1], &s7239_m3[2]); }
    if (s7239_frac > 0.f) { g_rs64_s7239_on = 1; fprintf(stderr, "[s7239] widewin_merge frac=%.3f tog=%d m3=%d,%d,%d\n", s7239_frac, s7239_tg, s7239_m3[0], s7239_m3[1], s7239_m3[2]); } } };
}
namespace { S7239Init s7239_init; }
// s7258: the dd6 bundle (main.cpp rs64_g1c_apply_dd_policy) setenvs the WIDEWIN stack after these static initialisers ran;
// re-read MERGE / MERGE_E so the auto values take effect (R is read lazily on first rs64_s7233_win call, no reinit needed).
extern "C" void rs64_s7258_merge_reinit() { S7239Init a; S7246Init b; (void)a; (void)b; }
extern "C" void rs64_s7239_node(uint32_t e, uint32_t d2bits) {
    if (s7239_emitted) { s7239_gen++; s7239_emitted = 0; s7239_pmax = 0.f; }
    if (s7239_hcnt > S7239_HN / 2) { memset(s7239_he, 0, sizeof s7239_he); s7239_hcnt = 0; s7239_hclr++; }
    float d2; memcpy(&d2, &d2bits, 4); if (d2 > s7239_pmax) s7239_pmax = d2;
    uint32_t h = s7239_hash(e);
    for (int k = 0; k < 64; k++, h = (h + 1) & (S7239_HN - 1)) {
        if (s7239_he[h] == e) { s7239_hd[h] = d2; s7239_hg[h] = s7239_gen; return; }
        if (!s7239_he[h]) { s7239_he[h] = e; s7239_hd[h] = d2; s7239_hg[h] = s7239_gen; s7239_hcnt++; return; } } }
extern "C" void rs64_s7239_end(uint8_t* rd);
static void s7239_flush(uint64_t now) {
    static uint64_t last = 0; if (!last) last = now; if (now - last < 48000000ull) return; last = now;
    for (int p = 0; p < 2; p++) { const unsigned long long* t = s7239_t[p]; if (!t[T_GRP] && !t[T_NOWW]) continue;
        fprintf(stderr, "[s7239] ph=%d frac=%.2f farcut=%.4g maxd2=%.4g thr=%.4g grp=%llu noww=%llu flag=%llu el=%llu flat=%llu cand=%llu anc=%llu drop=%llu merged=%llu ovf=%llu miss=%llu near=%llu unm=%llu dup=%llu stale=%llu hclr=%llu E=%d C=%d flatrej=%llu ctrrej=%llu shmis=%llu dh=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\n",
            p, s7239_frac, s7239_farcut, s7239_maxd2[p], s7239_thr, t[T_GRP], t[T_NOWW], t[T_FLAG], t[T_EL], t[T_FLAT], t[T_CAND], t[T_ANC], t[T_DROP], t[T_MERGED],
            t[T_OVF], t[T_MISS], t[T_NEAR], t[T_UNM], t[T_DUP], t[T_STALE], s7239_hclr, (int)s7246_E, (int)s7246_C, t[T_FLATE], t[T_FLATC], t[T_SHMIS],
            t[T_DH0], t[T_DH1], t[T_DH2], t[T_DH3], t[T_DH4], t[T_DH5], t[T_DH6], t[T_DH7]);
        memset(s7239_t[p], 0, sizeof s7239_t[p]); s7239_maxd2[p] = 0.f; } }
extern "C" void rs64_s7239_group(uint8_t* rd, uint32_t s1, uint32_t s0, int ww) {
    if (g_rs64_s7239_act) rs64_s7239_end(rd);
    s7239_emitted = 1;
    const uint64_t now = mach_absolute_time();
    int ph = 1;
    if (s7239_tg) { static int anc = 0; if (!anc) { anc = 1; rs64_tog_anchor(now); } ph = s7239_tg == 3 ? (s7239_m3[(now / 24000000u) % 3u] != 0) : rs64_tog_odd(now); }
    s7239_ph = ph; g_rs64_s7239_wm = ph; s7239_flush(now);
    if (!ww) { s7239_t[ph][T_NOWW]++; return; }
    s7239_t[ph][T_GRP]++;
    if (!s7239_ok(s1) || (s7239_rw(rd, s1 + 0x2C) & 0x40000000u)) { s7239_t[ph][T_FLAG]++; return; }
    uint32_t fc = s7239_rw(rd, 0x8009DEB4u); memcpy(&s7239_farcut, &fc, 4);
    // s7244: the gate is frac of this build pass's FARTEST node, in distance: dist2 >= frac^2 * pmax. The s7239 gate used
    // frac^2 * farcut, but node+8 (H1) reaches 7116 while farcut is 117.4 (s7240 soak, every arm), so the units differ and the
    // gate passed ~all candidates (near 216..7627 of ~2M at frac 0.4..0.7). All nodes of a pass precede its emits (s7242
    // generation contract; stale=0 in the s7240 soak), so pmax is complete here.
    const float thr = s7239_frac * s7239_frac * s7239_pmax; s7239_thr = thr;
    s7239_l.clear(); s7239_key.clear(); s7239_el.clear();
    for (uint32_t e = s0, n = 0; s7239_ok(e) && n < 40000; e = s7239_rw(rd, e), n++) {
        S7239E c{}; c.e = e; s7239_t[ph][T_EL]++;
        const uint32_t hp = s7239_rw(rd, e + 0x24);
        c.flat = s7239_rb(rd, e + 0x10) == 2 && s7239_rh(rd, e + 0x16) == 0 && (s7239_rw(rd, e + 0x10) & 0xFFFFFFu) == 0x020202u &&
                 s7239_rb(rd, e + 0x14) == 2 && !(s7239_rh(rd, e + 0x18) | s7239_rh(rd, e + 0x1A) | s7239_rh(rd, e + 0x1C) | s7239_rh(rd, e + 0x1E)) && s7239_ok(hp);
        if (c.flat) {
            c.x = (int16_t)s7239_rh(rd, e + 0x08); c.yb = (int16_t)s7239_rh(rd, e + 0x0A); c.z = (int16_t)s7239_rh(rd, e + 0x0C);
            c.v = (int32_t)(((uint32_t)(int32_t)(int16_t)s7239_rh(rd, e + 0x22) << 2) & 0xFFFFu);
            c.mat = s7239_rh(rd, e + 0x2C); c.b21 = s7239_rb(rd, e + 0x21); c.b2e = s7239_rh(rd, e + 0x2E) & 1;
            c.h[0] = (int8_t)s7239_rb(rd, hp + 0x00); c.h[1] = (int8_t)s7239_rb(rd, hp + 0x04); c.h[2] = (int8_t)s7239_rb(rd, hp + 0x14); c.h[3] = (int8_t)s7239_rb(rd, hp + 0x18);
            if (c.v <= 0 || c.v > 0x3FFF) c.flat = 0; }
        s7239_el.push_back({(uint64_t)e, (int32_t)s7239_l.size()});
        if (c.flat) { s7239_t[ph][T_FLAT]++; s7239_key.push_back({s7239_k(c.x, c.z, c.v), (int32_t)s7239_l.size()}); }
        s7239_l.push_back(c); }
    std::sort(s7239_key.begin(), s7239_key.end()); std::sort(s7239_el.begin(), s7239_el.end());
    for (size_t i = 1; i < s7239_key.size(); i++) if (s7239_key[i].first == s7239_key[i - 1].first) { s7239_l[s7239_key[i].second].dup = s7239_l[s7239_key[i - 1].second].dup = 1; }
    for (size_t i = 1; i < s7239_el.size(); i++) if (s7239_el[i].first == s7239_el[i - 1].first) { s7239_l[s7239_el[i].second].dup = s7239_l[s7239_el[i - 1].second].dup = 1; }
    int anchors = 0;
    for (size_t i = 0; i < s7239_l.size(); i++) {
        S7239E& a = s7239_l[i]; if (!a.flat || a.role) continue;
        if (a.dup) { s7239_t[ph][T_DUP]++; continue; }
        if ((s7239_fdiv(a.x, a.v) & 1) || (s7239_fdiv(a.z, a.v) & 1)) continue;
        const int32_t px[3] = {a.x + a.v, a.x, a.x + a.v}, pz[3] = {a.z, a.z + a.v, a.z + a.v}; int32_t pi[3]; bool ok = true;
        for (int k = 0; k < 3 && ok; k++) {
            if (px[k] > 32767 || pz[k] > 32767) { ok = false; break; }
            pi[k] = s7239_find(s7239_key, s7239_k(px[k], pz[k], a.v));
            if (pi[k] < 0) { ok = false; break; }
            const S7239E& p = s7239_l[pi[k]];
            if (p.dup || p.role || p.mat != a.mat || p.b21 != a.b21 || p.b2e != a.b2e) ok = false; }
        if (!ok) continue;
        float d[4]; bool st = false, hit = s7239_dist(a.e, &d[0], &st); for (int k = 0; k < 3; k++) hit = hit && s7239_dist(s7239_l[pi[k]].e, &d[k + 1], &st);
        if (!hit) { s7239_t[ph][T_MISS]++; if (st) s7239_t[ph][T_STALE]++; continue; }
        bool far = true; for (int k = 0; k < 4; k++) { if (d[k] > s7239_maxd2[ph]) s7239_maxd2[ph] = d[k]; if (!(d[k] >= thr)) far = false; }
        if (!far) { s7239_t[ph][T_NEAR]++; continue; }
        const int32_t hb = s7239_l[pi[0]].h[1] + s7239_l[pi[0]].yb - a.yb, hc = s7239_l[pi[1]].h[2] + s7239_l[pi[1]].yb - a.yb, hd = s7239_l[pi[2]].h[3] + s7239_l[pi[2]].yb - a.yb;
        if (hb < -2048 || hb > 2047 || hc < -2048 || hc > 2047 || hd < -2048 || hd > 2047) { s7239_t[ph][T_OVF]++; continue; }
        {   const S7239E &B = s7239_l[pi[0]], &C = s7239_l[pi[1]], &D = s7239_l[pi[2]];
            const int32_t A0 = a.yb + a.h[0], A4 = a.yb + a.h[1], A20 = a.yb + a.h[2], A24 = a.yb + a.h[3];
            const int32_t B4 = B.yb + B.h[1], B24 = B.yb + B.h[3], C20 = C.yb + C.h[2], C24 = C.yb + C.h[3], D24 = D.yb + D.h[3];
            // shared corners must agree between partners, or the retail mesh itself is open there
            if (B.yb + B.h[0] != A4 || C.yb + C.h[0] != A20 || D.yb + D.h[0] != A24 || B.yb + B.h[2] != A24 || C.yb + C.h[1] != A24 ||
                D.yb + D.h[1] != B24 || D.yb + D.h[2] != C24) s7239_t[ph][T_SHMIS]++;
            auto g = [](int32_t m, int32_t e1, int32_t e2) { const int32_t v = 2 * m - e1 - e2; return 8 * (v < 0 ? -v : v); };
            int32_t de = g(A4, A0, B4); de = std::max(de, g(A20, A0, C20)); de = std::max(de, g(C24, C20, D24)); de = std::max(de, g(B24, B4, D24));
            const int32_t dc = std::max(g(A24, A0, D24), g(A24, B4, C20));
            s7239_t[ph][T_DH0 + s7246_bin(de)]++;
            if (de > s7246_E) { s7239_t[ph][T_FLATE]++; continue; }
            if (dc > s7246_C) { s7239_t[ph][T_FLATC]++; continue; } }
        if (!ph) { s7239_t[ph][T_CAND]++; continue; }
        a.role = 1; for (int k = 0; k < 3; k++) { a.p[k] = pi[k]; s7239_l[pi[k]].role = 2; }
        anchors++; s7239_t[ph][T_ANC]++; }
    g_rs64_s7239_act = anchors > 0; g_rs64_s7239_skip = 0; }
extern "C" void rs64_s7239_cmd(uint8_t* rd, uint32_t e, uint32_t cmd) {
    const int32_t i = s7239_find(s7239_el, (uint64_t)e); if (i < 0) return;
    S7239E& c = s7239_l[i];
    if (c.role == 1) c.cmd = cmd;
    else if (c.role == 2 && s7239_ok(cmd)) { for (int k = 0; k < 10; k++) c.w[k] = s7239_rw(rd, cmd + 4u * k); c.cap = 1; g_rs64_s7239_skip = 1; s7239_t[s7239_ph][T_DROP]++; } }
extern "C" void rs64_s7239_end(uint8_t* rd) {
    const int ph = s7239_ph;
    for (S7239E& a : s7239_l) {
        if (a.role != 1) continue;
        const S7239E &b = s7239_l[a.p[0]], &c = s7239_l[a.p[1]], &d = s7239_l[a.p[2]];
        if (!a.cmd || !b.cap || !c.cap || !d.cap) { s7239_t[ph][T_UNM]++; continue; }
        uint32_t* w = reinterpret_cast<uint32_t*>(rd + (a.cmd - 0x80000000u));
        const int32_t nb = (int16_t)(b.w[1] & 0xFFFFu) + ((b.yb - a.yb) * 16), nc = (int16_t)(c.w[2] >> 16) + ((c.yb - a.yb) * 16), nd = (int16_t)(d.w[2] & 0xFFFFu) + ((d.yb - a.yb) * 16);
        w[1] = (w[1] & 0xFFFF0000u) | ((uint32_t)nb & 0xFFFFu);
        w[2] = (((uint32_t)nc & 0xFFFFu) << 16) | ((uint32_t)nd & 0xFFFFu);
        w[4] = b.w[4]; w[5] = c.w[5]; w[6] = d.w[6];
        w[9] = (w[9] & 0xFFFF0000u) | ((uint32_t)(2 * a.v) & 0xFFFFu);
        s7239_t[ph][T_MERGED]++; }
    s7239_l.clear(); g_rs64_s7239_act = 0; g_rs64_s7239_skip = 0; }
extern "C" int rs64_s6882_on(void) { static int on = -1; if (on < 0) { const char* e = getenv("ROGUESQ_G1D_SPANNARROW"); const char* d = getenv("ROGUESQ_DRAW_DISTANCE"); on = (e && *e == '0') ? 0 : (d && *d && atof(d) != 1.0) ? 2 : 1; } return on == 2 || (on == 1 && rs64_s6880_wide()); }
// s6883: span scan edge rows past 80 and span cells outside 64x64 (tools/apply_s6883_spancell.py). ROGUESQ_G1D_SPANCELL (default 3 where the s6882 gate runs, =0 old) bits 1 = rows >= 80 in host arrays, 2 = 64x64 cell bound,
// 4 = control, blank rows 20..23. ROGUESQ_G1D_SPANLOG=1 logs [spancell]; ROGUESQ_G1D_SPANDUMP=<prefix> writes both tables at each POSE_FREEZE.
namespace {
constexpr uint32_t S6883_N = 4096;
int16_t s6883_e[2][S6883_N];
struct { uint64_t calls, rows, r80, r80diff, r80vis, yneg, y64, xneg, x64, wrong, spill, bad7f80, bad7flt; int maxi, ymin, ymax, xmin, xmax; } s6883;
uint32_t s6883_hw, s6883_ne, s6883_win[4];
uint8_t s6883_snap[0x2000];
int s6883_mode(void) { static int m = -1; if (m < 0) { const char* e = getenv("ROGUESQ_G1D_SPANCELL"); m = e ? atoi(e) : 3; } return m; }
int s6883_log(void) { static int m = -1; if (m < 0) { const char* e = getenv("ROGUESQ_G1D_SPANLOG"); m = (e && *e == '1') ? 1 : 0; } return m; }
void s6883_print(const char* tag) {
    auto& s = s6883;
    fprintf(stderr, "[%s] calls=%llu rows=%llu r80=%llu r80diff=%llu r80vis=%llu yneg=%llu y64=%llu xneg=%llu x64=%llu wrong=%llu spill=%llu bad7f80=%llu bad7flt=%llu maxi=%d y=%d..%d x=%d..%d win=%d,%d,%d,%d ne=%u hw=%08X\n", tag,
        (unsigned long long)s.calls, (unsigned long long)s.rows, (unsigned long long)s.r80, (unsigned long long)s.r80diff, (unsigned long long)s.r80vis, (unsigned long long)s.yneg, (unsigned long long)s.y64,
        (unsigned long long)s.xneg, (unsigned long long)s.x64, (unsigned long long)s.wrong, (unsigned long long)s.spill, (unsigned long long)s.bad7f80, (unsigned long long)s.bad7flt,
        s.maxi, s.ymin, s.ymax, s.xmin, s.xmax, (int)s6883_win[0], (int)s6883_win[1], (int)s6883_win[2], (int)s6883_win[3], s6883_ne, s6883_hw);
    s.maxi = 0; s.ymin = s.xmin = 1 << 30; s.ymax = s.xmax = -(1 << 30);
}
}
extern "C" int rs64_s6883_edge(int w, uint32_t addr, int32_t v) {
    if (!rs64_s6882_on()) return 0;
    const uint32_t i = (addr - (w ? 0x80130D10u : 0x80130C70u)) >> 1;
    if (i < 80 || i >= S6883_N) return 0;
    s6883_e[w][i] = (int16_t)v;
    return s6883_mode() & 1;
}
extern "C" int rs64_s6883_edgerd(int w, uint32_t addr, int32_t* v) {
    if (!(s6883_mode() & 1) || !rs64_s6882_on()) return 0;
    const uint32_t i = (addr - (w ? 0x80130D10u : 0x80130C70u)) >> 1;
    if (i < 80 || i >= S6883_N) return 0;
    *v = s6883_e[w][i];
    return 1;
}
extern "C" void rs64_s6883_row(uint32_t a3, int32_t y, int32_t t4, int64_t* x0, int64_t* x1) {
    const uint32_t i = (a3 - 0x80130C70u) >> 1; const int m = s6883_mode(), lg = s6883_log(); const bool deep = i >= 80 && i < S6883_N;
    const int64_t g0 = *x0, g1 = *x1, t0 = deep ? s6883_e[0][i] : g0, t1 = deep ? s6883_e[1][i] : g1;
    if ((m & 1) && deep) { *x0 = t0; *x1 = t1; }
    if (m & 2) { const int L7009 = g_rs64_ww ? 127 : 63; /* s7009 widewin: 128-stride tables */
        if (y < 0 || y > L7009) *x1 = *x0 - 1;
        else { if (*x0 < 0) *x0 = 0; if (*x1 > L7009) *x1 = L7009; }
    }
    if (!lg) return;
    auto& s = s6883; s.rows++;
    if ((int)i > s.maxi) s.maxi = (int)i;
    if (y < s.ymin) s.ymin = y;
    if (y > s.ymax) s.ymax = y;
    if (t1 >= t0) { if (t0 < s.xmin) s.xmin = (int)t0; if (t1 > s.xmax) s.xmax = (int)t1; }
    if (g1 == 0x7F7F) { if (deep) s.bad7f80++; else s.bad7flt++; }
    if (deep) { s.r80++; if (g0 != t0 || g1 != t1) s.r80diff++; if (y >= 0 && y < 64 && t1 >= 0 && t0 <= 63 && t1 >= t0) s.r80vis++; }
    if (y < 0) s.yneg++;
    if (y > 63) s.y64++;
    if (t0 < 0) s.xneg++;
    if (t1 > 63) s.x64++;
    // stores the byte bound lets through, and how many of them are not this row's own 64 cells
    const int64_t rel = (int64_t)t4 + ((int64_t)y << 6) - (int64_t)(int32_t)0x80130DB0;
    int64_t lo = *x0 < -rel ? -rel : *x0, hi = *x1 > 0x1FFF - rel ? 0x1FFF - rel : *x1, n = hi >= lo ? hi - lo + 1 : 0, good = 0;
    if (y >= 0 && y < 64) { const int64_t l = *x0 < 0 ? 0 : *x0, h = *x1 > 63 ? 63 : *x1; good = h >= l ? h - l + 1 : 0; }
    s.wrong += (uint64_t)(n - good);
    if ((y < 0 || y > 63) && n) s.spill++;
}
extern "C" void rs64_s6883_tables(uint8_t* rdram) {
    if (!rs64_s6882_on()) return;
    if (s6883_mode() & 4) for (int r = 20; r < 24; r++) { memset(rdram + 0x130DB0u + r * 64, 0x80, 64); memset(rdram + 0x131DB0u + r * 64, 0x80, 64); }
    if (!s6883_log()) return;
    for (int k = 0; k < 4; k++) s6883_win[k] = *reinterpret_cast<const uint32_t*>(rdram + 0x132DB0u + 4 * k);
    for (uint32_t k = 0; k < 0x2000; k++) s6883_snap[k] = rdram[(0x130DB0u + k) ^ 3];
    const int w = (int)s6883_win[1] > 64 ? 64 : (int)s6883_win[1], h = (int)s6883_win[3] > 64 ? 64 : (int)s6883_win[3];
    uint32_t hw = 2166136261u, ne = 0;
    for (int r = 0; r < h; r++) for (int c = 0; c < w; c++) {
        const uint8_t a = s6883_snap[r * 64 + c], b = s6883_snap[0x1000 + r * 64 + c];
        hw = (hw ^ a) * 16777619u; hw = (hw ^ b) * 16777619u; ne += !(a == 0x80 && b == 0x80);
    }
    s6883_hw = hw; s6883_ne = ne;
    if (!(++s6883.calls & 127)) s6883_print("spancell");
}
extern "C" void rs64_s6883_freeze(unsigned k) {
    if (!s6883_log()) return;
    char tag[32]; snprintf(tag, sizeof tag, "spancell-freeze k=%u", k); s6883_print(tag);
    if (const char* p = getenv("ROGUESQ_G1D_SPANDUMP")) {
        char fn[512]; snprintf(fn, sizeof fn, "%s.k%u.bin", p, k);
        if (FILE* f = fopen(fn, "wb")) { fwrite(s6883_snap, 1, sizeof s6883_snap, f); fclose(f); }
    }
}
// s6926 G5h: 512x300 (SHOWROOM family) joins the wide lists; tools/apply_s6926_showroom.py. ROGUESQ_G1D_SHOWROOM=0 = old.
extern "C" { int rs64_g1d_pfm_h = 0; int rs64_s6926_on(void) { static const int on = [] { const char* e = std::getenv("ROGUESQ_G1D_SHOWROOM"); return !(e && *e == '0'); }(); return on; } }
extern "C" { int rs64_g1d_intro_w = 0; int rs64_g1d_vs_intro = 0; int rs64_g1d_title_vi = 0; int rs64_g1d_vi_epoch = 0; uint32_t rs64_last_vi_mode = 0; }  // s6720: title_vi = wide title mode live
extern "C" volatile int g_rs64_dd_blk; // s6583: dd toggle state, tagged on [fbdump]
extern "C" void rs64_m5_host_write_census(uint8_t* rdram,
                                             uint32_t phys,
                                             uint32_t len,
                                             const char* api);
extern "C" void rs64_f5_host_write_begin(const uint8_t* rdram,
                                           uint32_t phys, uint32_t len,
                                           const char* api);
#include "librecomp/helpers.hpp"
#include "ultramodern/ultramodern.hpp"

// The guest publishes the voice-array base/count from the allocator while the
// audio mixer scans the same pair on another host thread.
static std::mutex g_rs64_s4985_voice_mutex;
extern "C" void rs64_s4985_voice_lock() {
    g_rs64_s4985_voice_mutex.lock();
}
extern "C" void rs64_s4985_voice_unlock() {
    g_rs64_s4985_voice_mutex.unlock();
}

extern "C" bool rs64_audio_current_route_snapshot(
    uint32_t* phase, uint32_t* width, uint32_t* origin, uint32_t* ordinal,
    uint32_t* row, int* exit_reason, const char** arm);
extern "C" void rs64_m5_audio_dma_identity(
    uint64_t* source_event, uint64_t* task_generation,
    uint32_t* latest_route_seq, uint32_t* latest_route_ordinal,
    uint32_t* latest_route_row);
extern "C" uint64_t rs64_m5_route_handoff_event(
    const char* edge, uint32_t site, uint32_t active, const char* arm,
    uint32_t phase, uint32_t width, uint32_t origin, uint32_t ordinal,
    uint32_t row, uint32_t value0, uint32_t value1, uint32_t value2);
extern "C" uint64_t rs64_m5_latest_audio_generation();

extern "C" uint32_t rs64_phase_ord(void);
extern "C" volatile uint32_t g_rs64_last_guest_pc;
extern "C" uint64_t rs64_m5_clear_branch_source_sequence(void);
extern "C" void rs64_m5_vi_commit_handoff(uint32_t caller, uint32_t requested_width,
                                            uint32_t mode_ptr);
extern "C" void rs64_m5_audio_transition_commit(uint32_t width,
                                                   uint32_t origin,
                                                   uint32_t phase);

namespace {

struct M5ViCommitSnapshot {
    std::atomic<uint32_t> next_sequence{0};
    std::atomic<uint32_t> latest_sequence{0xFFFFFFFFu};
    std::atomic<uint32_t> caller{0};
    std::atomic<uint32_t> requested_width{0};
    std::atomic<uint32_t> width{0};
    std::atomic<uint32_t> origin{0};
    std::atomic<uint32_t> phase{0};
};

static M5ViCommitSnapshot g_m5_vi_commit;

enum class ViBoundaryEdge : uint32_t {
    Swap = 0,
    Commit = 1,
    Screen = 2,
};

static bool vi_boundary_log_enabled() {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* specific = std::getenv("ROGUESQ_LOG_VI_COMMIT");
        return (all && *all && *all != '0') ||
               (specific && *specific && *specific != '0');
    }();
    return enabled;
}

static std::atomic<uint32_t> g_vi_boundary_ordinal{0};
static std::atomic<uint32_t> g_vi_boundary_rows[3][2]{};
static std::atomic<uint32_t> g_vi_boundary_summary_armed{0};
static std::atomic<uint32_t> g_vi_screen_request{0};

static void vi_boundary_summary() {
    static const char* edges[] = {"swap", "commit", "screen"};
    static const uint32_t origins[] = {0x00696100u, 0x00696600u};
    std::fprintf(stderr, "[vi-boundary-summary] begin\n");
    for (uint32_t edge = 0; edge < 3; ++edge) {
        for (uint32_t origin = 0; origin < 2; ++origin) {
            uint32_t rows = g_vi_boundary_rows[edge][origin].load(std::memory_order_relaxed);
            if (rows > 64u) rows = 64u;
            std::fprintf(stderr,
                "[vi-boundary-summary] edge=%s origin=0x%06X rows=%u cap=64\n",
                edges[edge], origins[origin], rows);
        }
    }
    std::fprintf(stderr, "[vi-boundary-summary] end\n");
    std::fflush(stderr);
}

static bool vi_boundary_target(uint32_t origin, uint32_t* origin_index) {
    origin &= 0x00FFFFFFu;
    if (origin == 0x00696100u) {
        *origin_index = 0;
        return true;
    }
    if (origin == 0x00696600u) {
        *origin_index = 1;
        return true;
    }
    return false;
}

}

extern "C" void rs64_vi_boundary_set_screen_request(uint32_t framebuffer) {
    g_vi_screen_request.store(framebuffer, std::memory_order_relaxed);
}

extern "C" uint32_t rs64_vi_boundary_screen_request() {
    return g_vi_screen_request.load(std::memory_order_relaxed);
}

extern "C" void rs64_vi_boundary_log(const char* edge, uint32_t requested_fb,
                                      uint32_t committed_origin, uint32_t width) {
    if (!vi_boundary_log_enabled() || width != 640u) return;

    ViBoundaryEdge edge_id;
    if (std::strcmp(edge, "swap") == 0) {
        edge_id = ViBoundaryEdge::Swap;
    }
    else if (std::strcmp(edge, "commit") == 0) {
        edge_id = ViBoundaryEdge::Commit;
    }
    else if (std::strcmp(edge, "screen") == 0) {
        edge_id = ViBoundaryEdge::Screen;
    }
    else {
        return;
    }

    uint32_t origin_index = 0;
    const uint32_t origin = committed_origin & 0x00FFFFFFu;
    if (!vi_boundary_target(origin, &origin_index)) return;

    if (g_vi_boundary_summary_armed.exchange(1, std::memory_order_relaxed) == 0) {
        std::atexit(vi_boundary_summary);
        std::at_quick_exit(vi_boundary_summary);
    }

    const uint32_t edge_index = static_cast<uint32_t>(edge_id);
    const uint32_t row = g_vi_boundary_rows[edge_index][origin_index].fetch_add(
        1, std::memory_order_relaxed);
    if (row >= 64u) return;

    const uint32_t ordinal = g_vi_boundary_ordinal.fetch_add(1, std::memory_order_relaxed);
    const uint32_t request = requested_fb & 0x00FFFFFFu;
    std::fprintf(stderr,
        "[vi-boundary] edge=%s origin=0x%06X requested_fb=0x%06X "
        "committed_origin=0x%06X width=%u phase=%u row=%u ordinal=%u\n",
        edge, origin, request, origin, width, rs64_phase_ord(), row, ordinal);
    std::fflush(stderr);
}

extern "C" void __osContRamRead_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    _return<s32>(ctx, -1);  // no rumble pak
}

extern "C" void __osContRamWrite_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    _return<s32>(ctx, -1);  // no rumble pak
}

extern "C" void __osPfsSelectBank_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    _return<s32>(ctx, 1);  // PFS_ERR_NOPACK — no memory pak
}

extern "C" void rs64_s7491_hst(uint32_t a, uint32_t w, const char* kind);  /* s7491 class EP */
extern "C" void osDpGetCounters_recomp(uint8_t* rdram, recomp_context* ctx) {
    // Zero out the 8 DP counters. buf_ptr stays gpr (64-bit) so the
    // sign-extended MIPS address survives MEM_W's KSEG0 unmasking.
    gpr buf_ptr = ctx->r4;
    // Guest-pointer arg: refuse a buffer outside KSEG0 RDRAM (a wild r4 would
    // write host memory out of bounds through MEM_W).
    {
        const uint32_t lo = (uint32_t)buf_ptr;
        const bool sext = (int64_t)buf_ptr == (int64_t)(int32_t)lo;
        if (!sext || lo < 0x80000000u || 32u > (rs64_ram_top - 0x80000000u) - (lo - 0x80000000u)) {
            static std::atomic<uint32_t> bad{0};
            if (bad++ < 8) fprintf(stderr, "[osDpGetCounters] wild buf 0x%llX ignored\n", (unsigned long long)buf_ptr);
            return;
        }
    }
    for (int i = 0; i < 8; i++) {
        MEM_W(i * 4, buf_ptr) = 0;
    }
    rs64_s7491_hst((uint32_t)buf_ptr, 32, "os_dpcounters");  /* s7491 class EP */
}

extern "C" void osViGetCurrentField_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    ctx->r2 = 0;  // always field 0 (progressive / non-interlaced)
}

// Override upstream's `assert(false)` in ultra_translation.cpp:32. The real
// libultra osYieldThread voluntarily yields to the scheduler. On the host
// the closest equivalent is std::this_thread::yield(); blocking briefly is
// fine — the game only calls this from idle/wait paths.
//
// This symbol is defined in upstream librecomp too (with the assert), but
// the linker picks our definition first because /FORCE:MULTIPLE is enabled
// (already used for the patches/heap_guards.c override). Same trick.
extern "C" { bool rs64_s7381_on(); uint64_t rs64_s7381_now(); void rs64_s7381_yield(uint32_t ra, uint64_t ns); }
extern "C" void osYieldThread_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    if (rs64_s7381_on()) { const uint64_t t0 = rs64_s7381_now(); std::this_thread::yield(); rs64_s7381_yield((uint32_t)ctx->r31, rs64_s7381_now() - t0); return; }
    std::this_thread::yield();
}
// s7381 positive control for the guest-yield histogram: ROGUESQ_S7381_SPIN_CTL=1 calls the real osYieldThread_recomp with a
// marked return address (0x8000C7C0) from the barrier-stall path; the [s7381] dump must show "yield ra=8000C7C0".
extern "C" void rs64_s7381_yield_ctl() { recomp_context c{}; c.r31 = (gpr)(int32_t)0x8000C7C0u; osYieldThread_recomp(nullptr, &c); }

// RS64 fix: game calls osViBlack(1) twice during boot at funcs_0.c:2083 and
// :2142 and never osViBlack(0). That keeps ultramodern's VI_STATE_BLACK set
// forever → hStart forced to 0 → VI::visible() returns false in RT64 →
// PresentEarly matcher fails → no presents fire. Override the recomp wrapper
// so the game's calls are no-ops (visibility stays on by default).
// s7512 class FI: the real defect was ultramodern osViSetMode never resetting the VI state (retail ROM 0x800352D0 stores
// __osViNext->state = 1, clearing BLACK). With ROGUESQ_VI_BLACK_RETAIL (default on, events.cpp) that reset exists, so
// osViBlack is honoured exactly as libultra does it; =0 restores the no-op (the retail shadow still tracks it for the census).
extern "C" int rs64_vi_black_retail_on();
extern "C" void rs64_vi_black_shadow(uint8_t active);
extern "C" void osViBlack(uint8_t active);
extern "C" void osViBlack_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    static int s_count = 0;
    int n = ++s_count;
    const int honored = rs64_vi_black_retail_on();
    if (n <= 8) {
        fprintf(stderr, "[osViBlack #%d] active=%u (%s)\n",
                n, (uint32_t)ctx->r4, honored ? "honoured, s7512 retail" : "ignored — RS64 fix");
        fflush(stderr);
    }
    if (honored) osViBlack((uint8_t)ctx->r4); else rs64_vi_black_shadow((uint8_t)ctx->r4);
}

// Diagnostic: log osViSwapBuffer calls. The game tells VI which fb to display
// via this call. If the address doesn't match any prior SET_COLOR_IMAGE
// address, RT64 has no rendered content for it → black screen.
extern "C" uint32_t rs64_vi_committed_width();
extern "C" uint32_t rs64_vi_committed_origin();
extern "C" void rs64_s4899_swap(uint32_t fb, uint32_t width);
extern "C" void rs64_g1d_join_swap(uint32_t frame, uint32_t fb,
                                     uint32_t vi_width, uint32_t vi_origin);
static std::atomic<uint8_t*> g_rs64_g1d_rdram{nullptr};
extern "C" void rs64_g1d_copy_to_ram_trace(uint32_t rowStart, uint32_t rowEnd,
                                             uint32_t width, uint8_t siz,
                                             uint8_t *destination,
                                             const uint8_t *source,
                                             uint32_t bytes,
                                             uint32_t sourceTarget,
                                             uint32_t sourceWidth,
                                             uint32_t sourceHeight) {
    static int enabled = -1;
    static uint32_t phase_seen = UINT32_MAX;
    static uint32_t rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_G1D_COPY");
        enabled = (e && *e && *e != '0') ? 1 : 0;
    }
    if (!enabled || source == nullptr || bytes == 0) return;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (phase < 4u || phase > 4u || rows++ >= 400u) return;
    uint8_t* rdram = g_rs64_g1d_rdram.load(std::memory_order_relaxed);
    if (rdram == nullptr) return;
    const uintptr_t base = reinterpret_cast<uintptr_t>(rdram);
    const uintptr_t dst = reinterpret_cast<uintptr_t>(destination);
    const uint32_t phys = dst >= base ? static_cast<uint32_t>(dst - base) : 0xFFFFFFFFu;
    uint64_t before = 1469598103934665603ull;
    uint64_t host = 1469598103934665603ull;
    uint64_t beforeCenter = 1469598103934665603ull;
    uint64_t hostCenter = 1469598103934665603ull;
    uint64_t beforeOuter = 1469598103934665603ull;
    uint64_t hostOuter = 1469598103934665603ull;
    const uint32_t rowBytes = width << siz >> 1;
    const uint32_t centerLo = rowBytes / 4u;
    const uint32_t centerHi = rowBytes - centerLo;
    for (uint32_t i = 0; i < bytes; ++i) {
        const uint8_t hb = source[i];
        host = (host ^ hb) * 1099511628211ull;
        if (phys != 0xFFFFFFFFu) {
            const uint8_t bb = rdram[(phys + i) ^ 3u];
            before = (before ^ bb) * 1099511628211ull;
        }
        const bool center = (i % rowBytes) >= centerLo && (i % rowBytes) < centerHi;
        if (center) {
            hostCenter = (hostCenter ^ hb) * 1099511628211ull;
            if (phys != 0xFFFFFFFFu) {
                const uint8_t bb = rdram[(phys + i) ^ 3u];
                beforeCenter = (beforeCenter ^ bb) * 1099511628211ull;
            }
        } else {
            hostOuter = (hostOuter ^ hb) * 1099511628211ull;
            if (phys != 0xFFFFFFFFu) {
                const uint8_t bb = rdram[(phys + i) ^ 3u];
                beforeOuter = (beforeOuter ^ bb) * 1099511628211ull;
            }
        }
    }
    std::fprintf(stderr,
        "[g1d-copy] phase=%u row=%u-%u width=%u siz=%u phys=0x%06X bytes=%u "
        "target=0x%06X targetWH=%ux%u before=%016llX host=%016llX "
        "beforeCenter=%016llX hostCenter=%016llX beforeOuter=%016llX hostOuter=%016llX\n",
        phase, rowStart, rowEnd, width, siz, phys, bytes,
        sourceTarget, sourceWidth, sourceHeight,
        (unsigned long long)before, (unsigned long long)host,
        (unsigned long long)beforeCenter, (unsigned long long)hostCenter,
        (unsigned long long)beforeOuter, (unsigned long long)hostOuter);
    std::fflush(stderr);
}
// s5078: per-(pc,addr) count of instrumented stores into 0x9DE80..0x9DF00, fed by
// rs64_m5_writer_parity (apply_s5078_flight_writer_census.py), printed per swap under WATCH_LOG.
static std::mutex g_s5078_mu;
static std::map<std::pair<uint32_t, uint32_t>, uint64_t> g_s5078_counts;
extern "C" void rs64_s5078_flight_store(uint32_t pc, uint32_t addr) {
    std::lock_guard<std::mutex> lk(g_s5078_mu);
    ++g_s5078_counts[{pc, addr}];
}

extern std::atomic<int> g_rs64_swap_n;
extern "C" void rs64_store_diag_tick(void);
extern "C" void rs64_s7503_swap(int, uint32_t);
extern "C" int rs64_diag_fprintf(FILE* f, const char* fmt, ...);  // s7432
extern "C" void rs64_s7520_swap(uint8_t* rdram);  // s7520 class FQ (librecomp overlays.cpp)
extern "C" int rs64_standins_dump_left, rs64_standins_fb_on, rs64_standins_fb_win;  // s7624 G6c (rs64_standins.cpp)
extern "C" uint32_t rs64_standins_fb_call;
extern "C" void osViSwapBuffer_recomp(uint8_t* rdram, recomp_context* ctx) {
    g_rs64_g1d_rdram.store(rdram, std::memory_order_relaxed);
    rs64_s7520_swap(rdram);
    static int s_count = 0;
    int n = ++s_count;
    g_rs64_swap_n.store(n, std::memory_order_relaxed);
    rs64_s7503_swap(n, (uint32_t)ctx->r4); // s7503 class FA (main.cpp)
    rs64_store_diag_tick(); // s6698 same-run A/B
    {
        // s4727: per-frame poll of the colour-image-struct site 0x1F0D70..80
        // (+ control: hangar state word 0xCC3E4, which retail/port both move).
        static const bool poll_on = [] {
            const char* own = std::getenv("ROGUESQ_LOG_S4727_IMG_WATCH");
            return own && own[0] && own[0] != '0';
        }();
        if (poll_on) {
            static uint32_t last[5] = {~0u, ~0u, ~0u, ~0u, ~0u};
            static const uint32_t offs[5] = {0x1F0D70u, 0x1F0D74u, 0x1F0D78u, 0x1F0D7Cu, 0xCC3E4u};
            for (int i = 0; i < 5; i++) {
                uint32_t v = 0;
                for (uint32_t k = 0; k < 4; k++) v = (v << 8) | rdram[(offs[i] + k) ^ 3u];
                if (v != last[i]) {
                    std::fprintf(stderr, "[s4727-%s] frame=%d phase=%u vi_w=%u vi_org=0x%06X phys=0x%06X old=0x%08X new=0x%08X\n",
                        i == 4 ? "ctl" : "img", n, rs64_phase_ord(), rs64_vi_committed_width(),
                        rs64_vi_committed_origin() & 0xFFFFFFu, offs[i], last[i], v);
                    std::fflush(stderr);
                    last[i] = v;
                }
            }
            // s4728: extent of change across 0x1F0000..0x1F1000 each frame.
            static uint32_t snap[0x400];
            static bool snap_init = false;
            static int ext_events = 0;
            uint32_t first = ~0u, lastw = 0, cnt = 0, firstval = 0;
            for (uint32_t w = 0; w < 0x400; w++) {
                uint32_t a = 0x1F0000u + w * 4u, v = 0;
                for (uint32_t k = 0; k < 4; k++) v = (v << 8) | rdram[(a + k) ^ 3u];
                if (snap_init && v != snap[w]) {
                    if (first == ~0u) { first = w; firstval = v; }
                    lastw = w; cnt++;
                }
                snap[w] = v;
            }
            snap_init = true;
            if (cnt && ext_events < 400) {
                ext_events++;
                std::fprintf(stderr, "[s4728-extent] frame=%d phase=%u words=%u first=0x%06X last=0x%06X span=0x%X firstval=0x%08X\n",
                    n, rs64_phase_ord(), cnt, 0x1F0000u + first * 4u, 0x1F0000u + lastw * 4u,
                    (lastw - first + 1) * 4u, firstval);
                std::fflush(stderr);
            }
        }
    }
    uint32_t fb = (uint32_t)ctx->r4;

    static int s_log_callers = -1;
    if (s_log_callers < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_VI_CALLERS");
        s_log_callers = ((all && *all && *all != '0') ||
                         (own && *own && *own != '0')) ? 1 : 0;
    }
    {
        const auto* vi = ultramodern::renderer::get_vi_regs();
        rs64_vi_boundary_log("swap", fb,
                             vi->VI_ORIGIN_REG & 0x00FFFFFFu,
                             vi->VI_WIDTH_REG);
        rs64_g1d_join_swap((uint32_t)n, fb, vi->VI_WIDTH_REG,
                           vi->VI_ORIGIN_REG);
    }
    if (s_log_callers) {
        struct CallerRow {
            uint32_t caller;
            uintptr_t host_ra;
            uint32_t fb_phys;
            uint32_t width;
            uint32_t origin;
            uint32_t count;
        };
        static CallerRow rows[128]{};
        static uint32_t row_count = 0;
        const uint32_t caller = static_cast<uint32_t>(ctx->r31 - 8u);
        const uintptr_t host_ra = reinterpret_cast<uintptr_t>(__builtin_return_address(0));
        const uintptr_t self_addr = reinterpret_cast<uintptr_t>(&osViSwapBuffer_recomp);
        const uint32_t guest_pc = static_cast<uint32_t>(g_rs64_last_guest_pc);
        const uint32_t fb_phys = fb & 0x00FFFFFFu;
        const auto* vi = ultramodern::renderer::get_vi_regs();
        const uint32_t width = vi->VI_WIDTH_REG;
        const uint32_t origin = vi->VI_ORIGIN_REG & 0x00FFFFFFu;
        const uint32_t phase = rs64_phase_ord();
        const char* host_symbol = "?";
#if !defined(_WIN32)
        Dl_info host_info{};
        if (dladdr(reinterpret_cast<void*>(host_ra), &host_info) && host_info.dli_sname) {
            host_symbol = host_info.dli_sname;
        }
#endif
        if (n <= 16) {
            std::fprintf(stderr,
                "[vi-callers-control] n=%d caller=0x%08X guest_pc=0x%08X "
                "host_ra=0x%llX host_symbol=%s self=0x%llX fb=0x%06X width=%u "
                "origin=0x%06X phase=%u\n",
                n, caller, guest_pc, (unsigned long long)host_ra, host_symbol,
                (unsigned long long)self_addr, fb_phys, width, origin, phase);
            std::fflush(stderr);
        }
        if (width == 640u && (origin == 0x00696100u || origin == 0x00696600u)) {
            uint32_t index = row_count;
            for (uint32_t i = 0; i < row_count; ++i) {
                if (rows[i].caller == caller && rows[i].host_ra == host_ra &&
                    rows[i].fb_phys == fb_phys &&
                    rows[i].width == width && rows[i].origin == origin) {
                    index = i;
                    break;
                }
            }
            if (index == row_count && row_count < 128u) {
                rows[row_count++] = {caller, host_ra, fb_phys, width, origin, 0u};
            }
            if (index < row_count) {
                const uint32_t count = ++rows[index].count;
                if (count <= 16u || (count % 128u) == 0u) {
                    std::fprintf(stderr,
                        "[vi-callers] phase=%u caller=0x%08X guest_pc=0x%08X "
                        "host_ra=0x%llX host_symbol=%s fb=0x%06X width=%u "
                        "origin=0x%06X count=%u\n",
                        phase, caller, guest_pc, (unsigned long long)host_ra,
                        host_symbol, fb_phys, width, origin, count);
                    std::fflush(stderr);
                }
            }
        }
    }

    // EXPERIMENT 2026-05-13: ROGUESQ_FB_REDIRECT_HIRES — if the game asks VI
    // to display a lo-res fb (0x806BA000 / 0x806DD000 are 320×224 buffers,
    // ~0x23000 apart), redirect to the hi-res scratch fb at 0x8062B800
    // instead. Tests the hypothesis that attribution text lives in the
    // hi-res scratch but VI is swapping to an empty lo-res target.
    //
    // Empirically: SET_CIMG fires for both fb classes per frame, but ALL
    // texrects target 0x62B800 — the lo-res buffers only receive fillRect
    // clears. So this redirect should pull the actual drawn content into
    // VI's sampling stream.
    static int s_redirect = -1;
    if (s_redirect < 0) {
        const char* v = std::getenv("ROGUESQ_FB_REDIRECT_HIRES");
        s_redirect = (v && *v && v[0] != '0') ? 1 : 0;
        if (s_redirect) {
            fprintf(stderr, "[fb-redirect] lo-res VI swaps will be redirected to 0x8062B800 (hi-res scratch)\n");
            fflush(stderr);
        }
    }
    if (s_redirect) {
        const uint32_t phys = fb & 0x00FFFFFF;
        // Lo-res-fb signature: addresses 0x6BA000 / 0x6DD000 / 0x7DD000
        // (under (rs64_ram_top - 0x80000000u), in the small-fb cluster). Hi-res scratch is at
        // 0x62B800 — leave that untouched; redirect anything else in the
        // "expected VI fb" range to the hi-res scratch.
        if ((phys == 0x6BA000) || (phys == 0x6DD000) || (phys == 0x7DD000)) {
            uint32_t orig = fb;
            fb = 0x8062B800;
            if (n <= 8 || (n & 63) == 0) {
                fprintf(stderr, "[fb-redirect #%d] 0x%08X -> 0x%08X\n", n, orig, fb);
                fflush(stderr);
            }
        }
    }

    {   // s6117 G1d: ROGUESQ_FB_WIDTH flight swaps pass flip+0x400 (one 512-px line); at width 683 that is not a line start, RT64 finds no matching colour image.
        static const uint32_t fbw = [] { const char* e = std::getenv("ROGUESQ_FB_WIDTH"); return (e && *e) ? (uint32_t)std::atoi(e) : 0u; }();
        static const bool fix = [] { const char* e = std::getenv("ROGUESQ_FB_ORIGIN_FIX"); return e && *e && *e != '0'; }();
        if (fbw > 0) {
            static uint32_t seen[24]; static int ns;
            bool known = false; for (int i = 0; i < ns; ++i) known |= (seen[i] == fb);
            if (!known && ns < 24) { seen[ns++] = fb; fprintf(stderr, "[fbw] swap#%d new fb=0x%08X fix=%d\n", n, fb, (int)fix); }
            (void)fix;
        }
    }
    rs64_s4899_swap(fb, rs64_vi_committed_width()); // s4900
    if (n <= 16 || (n & 63) == 0) {
        fprintf(stderr, "[osViSwapBuffer #%d] fb=0x%08X\n", n, fb);
        fflush(stderr);
    }
    // ROGUESQ_LOG_VI_FB_CONTENT=1: sample a few non-zero bytes from the fb
    // RDRAM to verify whether the game is writing attribution pixels into it
    // (vs the fb being empty and attribution rendering happening elsewhere).
    static int s_dump_fb = -1;
    if (s_dump_fb < 0) {
        const char* v = std::getenv("ROGUESQ_LOG_VI_FB_CONTENT");
        s_dump_fb = (v && *v && v[0] != '0') ? 1 : 0;
    }
    if (s_dump_fb && (n <= 64 || (n & 31) == 0)) {
        auto scan_fb = [&](uint32_t target_addr, const char* label) {
            const uint32_t phys = target_addr & 0x00FFFFFF;
            size_t nonzero = 0;
            uint32_t first_nz_off = 0xFFFFFFFFu;
            uint32_t first_nz_val = 0;
            const uint32_t scan = 320u * 224u * 2u;
            for (uint32_t i = 0; i < scan; i += 2) {
                uint32_t off = phys + i;
                uint8_t b0 = rdram[(off & 0xFFFFFFu) ^ 3];
                uint8_t b1 = rdram[((off + 1) & 0xFFFFFFu) ^ 3];
                if (b0 || b1) {
                    if (first_nz_off == 0xFFFFFFFFu) {
                        first_nz_off = i;
                        first_nz_val = (uint32_t)((b0 << 8) | b1);
                    }
                    ++nonzero;
                }
            }
            fprintf(stderr, "[vi-fb-content #%d %s] addr=0x%08X nz_px=%zu/%u first@%u=0x%04X\n",
                    n, label, target_addr, nonzero, scan / 2u, first_nz_off, first_nz_val);
        };
        scan_fb(fb, "VI");
        // Also scan the hi-res scratch fb (0x8062B800) so we can see if
        // experimental op_02 output landed there.
        scan_fb(0x8062B800u, "hiRes");
        fflush(stderr);
    }
    // ROGUESQ_FB_HASH=1 (s5069): FNV-1a of the 320x224 RGBA16 fb on EVERY swap,
    // so windows of a single run can be compared offline for frame variance.
    static int s_fb_hash = -1;
    if (s_fb_hash < 0) {
        const char* v = std::getenv("ROGUESQ_FB_HASH");
        s_fb_hash = (v && *v && v[0] != '0') ? 1 : 0;
    }
    if (s_fb_hash) {
        const uint32_t phys = fb & 0x00FFFFFF;
        uint64_t h = 1469598103934665603ull;
        for (uint32_t i = 0; i < 320u * 224u * 2u; ++i) {
            h = (h ^ rdram[((phys + i) & 0xFFFFFFu) ^ 3]) * 1099511628211ull;
        }
        (fprintf)(stderr, "[fbhash #%d] fb=0x%08X h=%016llx\n", n, fb, (unsigned long long)h);
    }
    static const char* s_fbd = std::getenv("ROGUESQ_FB_DUMP_DIR");
    static const int s_fbd_every = [] { const char* e = std::getenv("ROGUESQ_FB_DUMP_EVERY"); int v = e ? atoi(e) : 0; return v > 0 ? v : 500; }();
    static const int s_fbd_phase = [] { const char* e = std::getenv("ROGUESQ_FB_DUMP_PHASE"); return (e && *e) ? std::atoi(e) : -1; }();
    static int s_fbd_phase_left = 1;
    const bool phase_gate = s_fbd_phase >= 0;
    const bool phase_ok = !phase_gate || ((int)rs64_phase_ord() == s_fbd_phase && s_fbd_phase_left > 0);
    // s6727 G1d: ROGUESQ_FB_DUMP_EPOCH=<e> dumps EVERY swap while rs64_g1d_vi_epoch == e (first ROGUESQ_FB_DUMP_EPOCH_N, 160),
    // instead of the n % EVERY cadence: catches 1-swap transients such as the game-over backdrop's tile-by-tile entry.
    static const int s_fbd_epoch = [] { const char* e = std::getenv("ROGUESQ_FB_DUMP_EPOCH"); return (e && *e) ? std::atoi(e) : -1; }();
    static int s_fbd_epoch_left = [] { const char* e = std::getenv("ROGUESQ_FB_DUMP_EPOCH_N"); return (e && *e) ? std::atoi(e) : 160; }();
    // s6734 G3: ROGUESQ_FB_DUMP_MODE=<mode_ptr hex> instead keys the epoch dump on the last osViSetMode mode_ptr (epoch numbers
    // drift run to run: the mission-start 0x80128C90 load swap was epoch 42 in one run, 43 in the next), from swap
    // ROGUESQ_FB_DUMP_MIN_SWAP on (default 0). Shares the EPOCH_N cap.
    static const uint32_t s_fbd_mode = [] { const char* e = std::getenv("ROGUESQ_FB_DUMP_MODE"); return (e && *e) ? (uint32_t)strtoul(e, nullptr, 16) : 0u; }();
    static const int s_fbd_min_swap = [] { const char* e = std::getenv("ROGUESQ_FB_DUMP_MIN_SWAP"); return (e && *e) ? std::atoi(e) : 0; }();
    const bool epoch_hit = s_fbd_mode
        ? (__atomic_load_n(&rs64_last_vi_mode, __ATOMIC_RELAXED) == s_fbd_mode && n >= s_fbd_min_swap && s_fbd_epoch_left > 0)
        : (s_fbd_epoch >= 0 && __atomic_load_n(&rs64_g1d_vi_epoch, __ATOMIC_RELAXED) == s_fbd_epoch && s_fbd_epoch_left > 0);
    // s7624 G6c step 3: ROGUESQ_STANDINS_DUMP windows (src/main/rs64_standins.cpp) dump every swap, tagged with the stand-in state.
    const bool si_hit = rs64_standins_dump_left > 0;
    if (s_fbd && *s_fbd && (si_hit || (phase_ok && ((s_fbd_epoch >= 0 || s_fbd_mode) ? epoch_hit : (phase_gate || n % s_fbd_every == 0))))) {
        if (si_hit) {
            --rs64_standins_dump_left;
            fprintf(stderr, "[standins-fb] n=%d win=%d on=%d call=%u\n", n, rs64_standins_fb_win, rs64_standins_fb_on, rs64_standins_fb_call);
        } else {
        if (phase_gate) --s_fbd_phase_left;
        if (epoch_hit) --s_fbd_epoch_left;
        }
        [&] {
            char path[512];
            const auto regs = *ultramodern::renderer::get_vi_regs();
            RT64::VI vi{};
            vi.status.word = regs.VI_STATUS_REG;
            vi.origin = regs.VI_ORIGIN_REG;
            vi.width = regs.VI_WIDTH_REG;
            vi.vCurrentLine = regs.VI_V_CURRENT_LINE_REG;
            vi.hRegion.word = regs.VI_H_START_REG;
            vi.vRegion.word = regs.VI_V_START_REG;
            vi.xTransform.word = regs.VI_X_SCALE_REG;
            vi.yTransform.word = regs.VI_Y_SCALE_REG;
            if (!vi.width || !vi.xTransform.xScale || !vi.yTransform.yScale ||
                vi.hRegion.hEnd <= vi.hRegion.hStart || vi.vRegion.vEnd <= vi.vRegion.vStart ||
                vi.fbSiz() < 2) return;
            const auto size = vi.fbSize();
            const uint32_t dw = size.x, dh = size.y;
            const uint32_t stride = dw;
            const uint32_t bpp = 1u << (vi.fbSiz() - 1);
            static const bool s_fbd_vi = [] { const char* e = std::getenv("ROGUESQ_FB_DUMP_VI"); return e && *e && e[0] != '0'; }();
            const uint32_t phys = (s_fbd_vi ? vi.fbAddress() : fb) & 0x00FFFFFFu;
            if (!dw || !dh || uint64_t(phys) + uint64_t(dw) * dh * bpp > 0x1000000u) return;
            snprintf(path, sizeof path, "%s/fb_%07d_w%u.ppm", s_fbd, n, stride);
            fprintf(stderr, "[fbdump] n=%d fb=0x%08X stride=%u dd=%d phase=%u origin=0x%08X source=0x%08X width=%u height=%u bpp=%u vi_width=%u base=%s\n",
                    n, fb, stride, g_rs64_dd_blk, rs64_phase_ord(), vi.origin, phys,
                    dw, dh, bpp, vi.width, s_fbd_vi ? "vi-fbAddress" : "swap");
            { // s6489: cumulative buildGridCellMesh exit counters (e7 = cell passed all gates); defined in patched funcs_10.c
                fprintf(stderr, "[cellcum] n=%d e0=%u e1=%u e2=%u e3=%u e4=%u e5=%u e6=%u e7pass=%u\n", n,
                        g_s6489[0], g_s6489[1], g_s6489[2], g_s6489[3], g_s6489[4], g_s6489[5], g_s6489[6], g_s6489[7]);
            }
            fprintf(stderr, "[gridcum] n=%d calls=%u listnz=%u chainnz=%u\n", n, g_s6491[0], g_s6491[1], g_s6491[2]);
            { extern uint32_t g_s6492[12]; fprintf(stderr, "[forface] n=%d iter=%u jal=%u lastexit=%u lastnear=%u pass=%u headset=%u epi=%u epi_s5zero=%u entries=%u a0zero=%u\n", n, g_s6492[0], g_s6492[1], g_s6492[2], g_s6492[3], g_s6492[4], g_s6492[5], g_s6492[6], g_s6492[7], g_s6492[8], g_s6492[9]); }
            { extern uint32_t g_s6493[16]; fprintf(stderr, "[streamcum] n=%d entries=%u zearly=%u xskip=%u poolcap=%u spaneq=%u r3=%u r4=%u sbDB4=%u sbDC0=%u nonode=%u empty=%u nonempty=%u sumz=%u sumx=%u\n", n, g_s6493[0], g_s6493[1], g_s6493[2], g_s6493[3], g_s6493[4], g_s6493[5], g_s6493[6], g_s6493[7], g_s6493[8], g_s6493[9], g_s6493[10], g_s6493[11], g_s6493[12], g_s6493[13]); }
            auto write_dump = [&](const char* filename, uint32_t height, bool tail_reference) {
                if (uint64_t(phys) + uint64_t(stride) * height * bpp > 0x1000000u) return;
                if (FILE* f = fopen(filename, "wb")) {
                    fprintf(f, "P6\n# source=rdram-readback-not-window vi_width=%u phase=%u origin=0x%X base=0x%X stride_bytes=%u source_height=%u outside_source_tail=%u\n%u %u\n255\n",
                            vi.width, rs64_phase_ord(), vi.origin, phys, stride * bpp, dh,
                            tail_reference ? height - dh : 0u, dw, height);
                    for (uint32_t i = 0; i < dw * height; ++i) {
                        const uint32_t o = phys + i * bpp;
                        unsigned char rgb[3];
                        if (bpp == 2) {
                            const uint16_t px = (uint16_t(rdram[o ^ 3]) << 8) | rdram[(o + 1) ^ 3];
                            rgb[0] = ((px >> 11) & 31) * 255 / 31;
                            rgb[1] = ((px >> 6) & 31) * 255 / 31;
                            rgb[2] = ((px >> 1) & 31) * 255 / 31;
                        } else {
                            for (uint32_t c = 0; c < 3; ++c) rgb[c] = rdram[(o + c) ^ 3];
                        }
                        fwrite(rgb, 1, 3, f);
                    }
                    fclose(f);
                }
            };
            write_dump(path, dh, false);
            static const uint32_t tail_rows = [] { const char* e = std::getenv("ROGUESQ_FB_DUMP_TAIL_ROWS"); return e ? uint32_t(std::clamp(atoi(e), 0, 448)) : 0u; }();
            if (tail_rows) {
                snprintf(path, sizeof path, "%s/fb_%07d_w%u_tail-reference.ppm", s_fbd, n, stride);
                write_dump(path, dh + tail_rows, true);
            }
        }();
    }
    // ROGUESQ_TRAP_AT_SWAP=N (s5466): print the host address of guest RDRAM and raise a debugger trap once at swap N,
    // so an attached lldb can arm hardware write-watchpoints on guest words (only set this under lldb).
    static const int s_trap_at = [] { const char* e = std::getenv("ROGUESQ_TRAP_AT_SWAP"); return e ? atoi(e) : 0; }();
    if (s_trap_at > 0 && n == s_trap_at) {
        fprintf(stderr, "[trap-at-swap #%d] rdram=%p (guest word at phys P is the LE u32 at rdram+P)\n", n, (const void*)rdram);
        fflush(stderr);
        // no trap: the driver script sends `process interrupt` to lldb when it sees this line
    }
    // ROGUESQ_RDRAM_DUMP_DIR=<dir> (s5465): raw RDRAM[0..0x680000) (host byte order, ^3 swapped) at swaps
    // n%COARSE==0 (default 500) and, inside [FROM,TO], n%EVERY==0 (default 50). For the results-entry state diff.
    static const char* s_rd = std::getenv("ROGUESQ_RDRAM_DUMP_DIR");
    if (s_rd && *s_rd) {
        auto ev = [](const char* k, int d) { const char* e = std::getenv(k); int v = e ? atoi(e) : 0; return v > 0 ? v : d; };
        static const int s_every = ev("ROGUESQ_RDRAM_DUMP_EVERY", 50), s_coarse = ev("ROGUESQ_RDRAM_DUMP_COARSE", 500),
                         s_from = ev("ROGUESQ_RDRAM_DUMP_FROM", 6000), s_to = ev("ROGUESQ_RDRAM_DUMP_TO", 8600);
        if (n % s_coarse == 0 || (n >= s_from && n <= s_to && n % s_every == 0)) {
            char path[512];
            snprintf(path, sizeof path, "%s/rdram_%07d_fb%08X.bin", s_rd, n, fb);
            static const int s_bytes = ev("ROGUESQ_RDRAM_DUMP_BYTES", 0x680000);  /* s7317: 0x1400000 covers OSMEM 12 heap + 0x81000000 spill arena */
            if (FILE* f = fopen(path, "wb")) { fwrite(rdram, 1, (size_t)(s_bytes > 0x1400000 ? 0x1400000 : s_bytes), f); fclose(f); }
            { extern void rs64_s7317_write(const char*); snprintf(path, sizeof path, "%s/alloc_%07d.txt", s_rd, n); rs64_s7317_write(path); }
        }
    }
    // s7514 class FK (time shape): ROGUESQ_LOG_TIME_SHAPE=1 prints every 30th swap one [s7514-time] row: swap, VI ordinal,
    // host steady ns, osGetTime(), the game's last VI-retrace stamp 0x80128ED8 and frame interval 0x80128EB4, the gfx task
    // duration 0x80128D34, osClockRate lo 0x80039104 and the profiler-bar gate byte 0x80038CE0 (ROM 1, mainGameLoop clears it;
    // emitProfilerBarSegment 0x80023D40 draws host-time-length bars only while it is set). ROGUESQ_TIME_SHAPE_CTL=<swap>
    // positive control: sets the gate to 1 for swaps [ctl, ctl+120) then restores 0, so the bars must appear in fb dumps there.
    {
        static const bool s_ts = [] { const char* e = std::getenv("ROGUESQ_LOG_TIME_SHAPE"); return e && *e == '1'; }();
        static const int s_ts_ctl = [] { const char* e = std::getenv("ROGUESQ_TIME_SHAPE_CTL"); return e ? atoi(e) : 0; }();
        if (s_ts || s_ts_ctl > 0) {
            auto b = [&](uint32_t a) { return (unsigned)rdram[a ^ 3]; };
            auto w = [&](uint32_t a) { return (b(a) << 24) | (b(a + 1) << 16) | (b(a + 2) << 8) | b(a + 3); };
            if (s_ts_ctl > 0 && n == s_ts_ctl) rdram[0x38CE0 ^ 3] = 1;
            if (s_ts_ctl > 0 && n == s_ts_ctl + 120) rdram[0x38CE0 ^ 3] = 0;
            if (s_ts && (n % 30 == 0 || n == s_ts_ctl || n == s_ts_ctl + 60 || n == s_ts_ctl + 120)) {
                const long long ns = (long long)std::chrono::duration_cast<std::chrono::nanoseconds>(
                    std::chrono::steady_clock::now().time_since_epoch()).count();
                fprintf(stderr, "[s7514-time] n=%d vi=%u ns=%lld ostime=%llu vit=%u fint=%u gfxd=%u clk=%u gate=%u ctl=%d\n", n,
                        (unsigned)rs64_vi_n_g, ns, (unsigned long long)osGetTime(), w(0x128ED8), w(0x128EB4), w(0x128D34),
                        w(0x39104), b(0x38CE0), (s_ts_ctl > 0 && n >= s_ts_ctl && n < s_ts_ctl + 120) ? 1 : 0);
            }
        }
    }
    // ROGUESQ_WATCH_LOG=1 (s5076): per-swap log of the stick struct (0x80130B88 port0),
    // the readControllerInputs gate byte 0x130B56, and candidate flight-state words.
    static int s_watch = -1;
    if (s_watch < 0) {
        const char* v = std::getenv("ROGUESQ_WATCH_LOG");
        s_watch = (v && *v && v[0] != '0') ? 1 : 0;
    }
    if (s_watch) {
        {
            std::lock_guard<std::mutex> lk(g_s5078_mu);
            std::string wr;
            for (auto& kv : g_s5078_counts) {
                char t[48];
                snprintf(t, sizeof t, " %08X@%05X:%llu", kv.first.first, kv.first.second, (unsigned long long)kv.second);
                wr += t;
            }
            fprintf(stderr, "[watch-wr #%d]%s\n", n, wr.c_str());
        }
        auto b = [&](uint32_t a) { return (unsigned)rdram[a ^ 3]; };
        auto w = [&](uint32_t a) { return (b(a) << 24) | (b(a + 1) << 16) | (b(a + 2) << 8) | b(a + 3); };
        auto hr = [&](uint32_t lo, uint32_t hi) {
            uint64_t h = 1469598103934665603ull;
            for (uint32_t a = lo; a < hi; ++a) h = (h ^ rdram[a ^ 3]) * 1099511628211ull;
            return (unsigned long long)h;
        };
        fprintf(stderr,
                "[watch #%d] fb=0x%08X gate=%02X stick=%02X%02X%02X%02X%02X%02X cand9DEAC=%08X %08X %08X %08X h10C0F0=%016llx h9DE=%016llx\n",
                n, fb, b(0x130B56), b(0x130B88), b(0x130B89), b(0x130B8A), b(0x130B8B), b(0x130B8C), b(0x130B8D),
                w(0x9DEAC), w(0x9DEB0), w(0x9DEB4), w(0x9DEB8), hr(0x10C0F0, 0x10C340), hr(0x9DE80, 0x9DF00));
        // s5080: computeGridLayerScrollOffset (0x800455C8) lerps on x = *(*(0x80138D1C)+0x50)
        // between thresholds 0x130C5C/60 into outputs 0x130C54/58 -> 0x9DEAC.
        const uint32_t optr = w(0x138D1C);
        const uint32_t oph = optr & 0xFFFFFFu;
        const bool ok = (optr >> 28) == 8 && oph < 0x7FFFA0;
        fprintf(stderr, "[watch2 #%d] objptr=%08X x50=%08X obj48..58=%08X %08X %08X %08X %08X thrA=%08X thrB=%08X y0=%08X y1=%08X acc40=%08X\n",
                n, optr, ok ? w(oph + 0x50) : 0u, ok ? w(oph + 0x48) : 0u, ok ? w(oph + 0x4C) : 0u,
                ok ? w(oph + 0x50) : 0u, ok ? w(oph + 0x54) : 0u, ok ? w(oph + 0x58) : 0u,
                w(0x130C5C), w(0x130C60), w(0x130C54), w(0x130C58), w(0x130C40));
    }
    // ROGUESQ_RDRAM_SNAP_DIR=<dir> (s5069): if <dir>/trigger exists, its first line names a
    // snapshot; dump 8 MB RDRAM (byte-swapped back to big-endian order) to <dir>/<name>.bin.
    static const char* s_snap_dir = std::getenv("ROGUESQ_RDRAM_SNAP_DIR");
    if (s_snap_dir && *s_snap_dir && (n & 3) == 0) {
        std::string trig = std::string(s_snap_dir) + "/trigger";
        if (FILE* t = fopen(trig.c_str(), "r")) {
            char name[128] = {0};
            if (!fgets(name, sizeof name, t)) name[0] = 0;
            fclose(t);
            remove(trig.c_str());
            for (char* c = name; *c; ++c) if (*c == '\n' || *c == '/') *c = 0;
            if (name[0]) {
                std::string out = std::string(s_snap_dir) + "/" + name + ".bin";
                if (FILE* o = fopen(out.c_str(), "wb")) {
                    std::vector<uint8_t> buf((rs64_ram_top - 0x80000000u));
                    for (uint32_t i = 0; i < (rs64_ram_top - 0x80000000u); ++i) buf[i] = rdram[i ^ 3];
                    fwrite(buf.data(), 1, buf.size(), o);
                    fclose(o);
                    fprintf(stderr, "[rdram-snap] %s n=%d\n", name, n);
                }
            }
        }
    }
    extern void osViSwapBuffer(uint8_t* rdram, int32_t frameBufPtr);
    osViSwapBuffer(rdram, (int32_t)fb);
}

// Diagnostic: log osViSetMode calls + decode the OS_VI_MODE struct contents.
// OS_VI_MODE layout (libultra):
//   type      u32 at +0x00
//   comRegs.ctrl/width/burst/vSync/hSync/leap/hStart/xScale/vCurrent (9 u32) +0x04
//     → width at +0x08, xScale at +0x20
//   fldRegs[0].origin/yScale/vStart/vBurst/vIntr (5 u32) at +0x28
//     → yScale at +0x2C
//   fldRegs[1] at +0x3C (same layout)
// Total 80 bytes. We dump the first 80 bytes raw + key fields decoded so we
// can tell which mode is lo-res (width=320, xScale~0x200) vs hi-res
// (width=640, xScale~0x400).
// s6808 G3: host time spent in osViSetMode_recomp (count + cumulative us), stamped per VI by ROGUESQ_VI_WALL.
extern "C" { volatile uint32_t rs64_vimode_n_g = 0; volatile uint64_t rs64_vimode_us_g = 0; }
extern "C" void osViSetMode_recomp(uint8_t* rdram, recomp_context* ctx) {
    struct VimodeTimer {
        std::chrono::steady_clock::time_point t0 = std::chrono::steady_clock::now();
        ~VimodeTimer() {
            rs64_vimode_us_g += (uint64_t)std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::steady_clock::now() - t0).count();
            rs64_vimode_n_g++;
        }
    } vimode_timer;
    static int s_count = 0;
    int n = ++s_count;
    static int selector_control = -1;
    if (selector_control < 0) {
        const char* rs64_la = std::getenv("ROGUESQ_LOG_ALL"); // s7728: LOG_ALL, as the s802 probe
        const char* e = std::getenv("ROGUESQ_LOG_VI_SELECTOR");
        selector_control = ((rs64_la && *rs64_la && *rs64_la != '0') || (e && *e && *e != '0')) ? 1 : 0;
    }
    if (selector_control && n == 1) {
        fprintf(stderr, "[vi-selector-positive] osViSetMode_recomp is live\n");
        fflush(stderr);
    }
    uint32_t mode_ptr = (uint32_t)ctx->r4;
    {   // s6724 G1d: a new VI mode starts a new pillar-draw epoch (dpc_bridge rs64_g1d_pillar_scan).
        static uint32_t s_last_mode = 0;
        if (mode_ptr != s_last_mode) { s_last_mode = mode_ptr; __atomic_add_fetch(&rs64_g1d_vi_epoch, 1, __ATOMIC_RELAXED); }
        __atomic_store_n(&rs64_last_vi_mode, mode_ptr, __ATOMIC_RELAXED);  // s6734: FB_DUMP_MODE trigger
    }
    uint32_t rdram_off = mode_ptr & 0x00FFFFFF;
    if ((mode_ptr & 0x1FFFFFFFu) >= 0x01000000u) {  // s7339 class N: an OSViMode above 16 MB would fold onto phys 0x00xxxxxx
        static std::atomic<uint32_t> s_hi{0};
        const uint32_t c = s_hi.fetch_add(1, std::memory_order_relaxed) + 1;
        if (c <= 8 || (c & (c - 1)) == 0) fprintf(stderr, "[s7339] vimode hi n=%u mode=%08X\n", c, mode_ptr);
    }
    {   static std::atomic<uint32_t> s_seen{0};  // s7339: distinct-ish mode pointers seen (positive control: >0 lines)
        if (s_seen.fetch_add(1, std::memory_order_relaxed) < 4) fprintf(stderr, "[s7339] vimode ptr=%08X\n", mode_ptr); }
    auto read_u32 = [&](uint32_t off) -> uint32_t {
        uint32_t v = 0;
        for (int i = 0; i < 4; ++i) {
            v = (v << 8) | rdram[((rdram_off + off + i) & 0xFFFFFFu) ^ 3];
        }
        return v;
    };
    uint32_t type    = read_u32(0x00);
    uint32_t ctrl    = read_u32(0x04);
    uint32_t width   = read_u32(0x08);
    uint32_t xScale  = read_u32(0x20);
    uint32_t yScale  = read_u32(0x2C);
    uint32_t ra      = (uint32_t)ctx->r31;
    const char* site = "?";
#if !defined(_WIN32)
    {   // s7067: dladdr walks the symbol table (~70 us/call, 96% of this function's host cost, ~7.4k calls a run);
        // the call sites are a handful of generated functions, so cache name by return address. ROGUESQ_DLADDR_CACHE=0 = old path.
        static const bool cache_on = [] { const char* e = std::getenv("ROGUESQ_DLADDR_CACHE"); return !(e && *e == '0'); }();
        void* ra_host = __builtin_return_address(0);
        static std::mutex s_m; static void* s_ra[16]{}; static const char* s_name[16]{}; static int s_n = 0;
        bool hit = false;
        if (cache_on) {
            std::lock_guard<std::mutex> lk(s_m);
            for (int i = 0; i < s_n; ++i) if (s_ra[i] == ra_host) { site = s_name[i]; hit = true; break; }
        }
        if (!hit) {
            Dl_info di{};
            if (dladdr(ra_host, &di) && di.dli_sname) site = di.dli_sname;  // dli_sname points into the image: stable
            if (cache_on) { std::lock_guard<std::mutex> lk(s_m); if (s_n < 16) { s_ra[s_n] = ra_host; s_name[s_n] = site; ++s_n; } }
        }
    }
#endif
    rs64_diag_fprintf(stderr,
        "[osViSetMode #%d] mode_ptr=0x%08X  type=0x%08X ctrl=0x%08X "
        "width=%u xScale=0x%08X yScale=0x%08X ra=0x%08X site=%s\n",
        n, mode_ptr, type, ctrl, width, xScale, yScale, ra, site);
    fflush(stderr);
    {
        auto guest_u8 = [rdram](uint32_t guest) -> uint32_t {
            if (guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFu;
            return rdram[(guest - 0x80000000u) ^ 3u];
        };
        auto guest_u32 = [&guest_u8](uint32_t guest) -> uint32_t {
            return (guest_u8(guest) << 24) | (guest_u8(guest + 1u) << 16) |
                   (guest_u8(guest + 2u) << 8) | guest_u8(guest + 3u);
        };
        const uint32_t slot0 = guest_u32(0x80128D50u + 8u);
        const uint32_t slot1 = guest_u32(0x80128DA0u + 8u);
        const uint32_t slot2 = guest_u32(0x80128DF0u + 8u);
        const uint32_t slot3 = guest_u32(0x80128E40u + 8u);
        const uint32_t pendingA = guest_u32(0x80128E94u);
        const uint32_t pendingB = guest_u32(0x80128E90u);
        rs64_diag_fprintf(stderr,
            "[vi-mode-table] call=%d mode_ptr=0x%08X requested_width=%u "
            "slot0=%u slot1=%u slot2=%u slot3=%u "
            "pendingA=0x%08X pendingB=0x%08X pending_mask9=0x%X "
            "sel=%02X/%02X/%02X\n",
            n, mode_ptr, width, slot0, slot1, slot2, slot3,
            pendingA, pendingB, (pendingA | pendingB) & 0x9u,
            guest_u8(0x8011A865u), guest_u8(0x8011A864u),
            guest_u8(0x8011A862u));
        fflush(stderr);
    }
    static const bool log_transition = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_VI_TRANSITION");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (log_transition) {
        static bool phase_640_seen = false;
        const uint32_t committed_width = ultramodern::renderer::get_vi_regs()->VI_WIDTH_REG;
        if (committed_width >= 640) {
            phase_640_seen = true;
        }
        if (phase_640_seen) {
            fprintf(stderr,
                "[vi-transition-producer] call=%d committed_width=%u requested_width=%u mode_ptr=0x%08X\n",
                n, committed_width, width, mode_ptr);
            fflush(stderr);
        }
    }
    {   // s6113 G1d: ROGUESQ_FB_WIDTH=<w> pairs with the fixup'd video-state patch; widen the 512-wide flight VI mode to w (same output span, xScale scaled).
        static const uint32_t fbw = [] { const char* e = std::getenv("ROGUESQ_FB_WIDTH"); return (e && *e) ? (uint32_t)std::atoi(e) : 0u; }();
        // s6718 G1d: the 640x340 mission-intro state is widened to rs64_g1d_intro_w (set by the pfm fixup); widen its 640 VI mode to match.
        const uint32_t base = (fbw > 0 && width == 512u) ? 512u : (rs64_g1d_intro_w > 640 && width == 640u) ? 640u : 0u;
        rs64_g1d_title_vi = 0;
        const uint32_t tw = base == 512u ? fbw : (uint32_t)rs64_g1d_intro_w;
        // s6723 G1d: the mission debrief (abort / end -> MISSION FAILED + stats) uses mode 0x80128DA0, 512 wide, yScale
        // 0x800; rs64_g1d_title_vi = 2 marks it for the RDP-stage pillar handling in dpc_bridge (rs64_g1d_debrief).
        const bool debrief = base == 512u && mode_ptr == 0x80128DA0u && yScale == 0x800u && fbw > 512u;
        if (base) {
            auto write_u32 = [&](uint32_t off, uint32_t v) {
                for (int i = 0; i < 4; ++i) rdram[((rdram_off + off + i) & 0xFFFFFFu) ^ 3] = (uint8_t)(v >> (24 - 8 * i));
            };
            const uint32_t nx = (uint32_t)((uint64_t)xScale * tw / base);
            write_u32(0x08, tw);
            write_u32(0x20, nx);
            // s6117: fldRegs[0/1].origin (+0x28/+0x3C) is the second-field line offset = width*2 bytes; scale it with the width (else VI origin = fb+0x400 misses the 683-wide colour image).
            for (uint32_t off : {0x28u, 0x3Cu}) {
                uint32_t o = 0; for (int i = 0; i < 4; ++i) o = (o << 8) | rdram[((rdram_off + off + i) & 0xFFFFFFu) ^ 3];
                if (o) { write_u32(off, (uint32_t)((uint64_t)o * tw / base)); fprintf(stderr, "[fbw] fld origin +0x%X %u->%u\n", off, o, (uint32_t)((uint64_t)o * tw / base)); }
            }
            fprintf(stderr, "[fbw] osViSetMode mode_ptr=0x%08X width %u->%u xScale 0x%X->0x%X\n", mode_ptr, width, tw, xScale, nx);
            width = tw;
            if (debrief) rs64_g1d_title_vi = 2;
        } else if (fbw > 512u && width == 1024u && xScale <= 0x333u) {
            // s6720 G1d: the interlaced 512x448 title/menu mode has width 1024 = TWO 512-px lines (field stride),
            // xScale 0x333 (retail 4:3 logs the same). At wide aspect its colour image is fbw wide (title rects
            // centred at 256..768 of 1024), but the mode kept the 512-based stride/xScale/field offsets, so the VI
            // showed fb x 0..~512 across the screen (black left half, still 2x in the right half). Rescale all three
            // like the 512 path: width 2*fbw, xScale*fbw/512, field origins*fbw/512. ROGUESQ_G1D_TITLE_VI=0 = old.
            static const bool on = [] { const char* e = std::getenv("ROGUESQ_G1D_TITLE_VI"); return !(e && *e == '0'); }();
            if (on) {
                auto rd_u32 = [&](uint32_t off) { uint32_t v = 0; for (int i = 0; i < 4; ++i) v = (v << 8) | rdram[((rdram_off + off + i) & 0xFFFFFFu) ^ 3]; return v; };
                auto write_u32 = [&](uint32_t off, uint32_t v) {
                    for (int i = 0; i < 4; ++i) rdram[((rdram_off + off + i) & 0xFFFFFFu) ^ 3] = (uint8_t)(v >> (24 - 8 * i));
                };
                const uint32_t tw = 2u * fbw, nx = (uint32_t)((uint64_t)xScale * fbw / 512u);
                const uint32_t f0 = rd_u32(0x28), f1 = rd_u32(0x3C);
                write_u32(0x08, tw);
                write_u32(0x20, nx);
                write_u32(0x28, (uint32_t)((uint64_t)f0 * fbw / 512u));
                write_u32(0x3C, (uint32_t)((uint64_t)f1 * fbw / 512u));
                fprintf(stderr, "[fbw] title-vi mode_ptr=0x%08X width %u->%u xScale 0x%X->0x%X fld %u/%u -> %u/%u\n", mode_ptr, width, tw, xScale, nx,
                        f0, f1, (uint32_t)((uint64_t)f0 * fbw / 512u), (uint32_t)((uint64_t)f1 * fbw / 512u));
                width = tw;
                rs64_g1d_title_vi = 1;
            }
        }
    }
    extern void osViSetMode(uint8_t* rdram, int32_t modePtr);
    osViSetMode(rdram, (int32_t)ctx->r4);
    rs64_m5_vi_commit_handoff(static_cast<uint32_t>(g_rs64_last_guest_pc), width, mode_ptr);
}

extern "C" uint32_t rs64_vi_committed_width() {
    static const bool log_post_consumer = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_POST_CONSUMER");
        const char* own = std::getenv("ROGUESQ_LOG_ALL");
        return (all && *all && *all != '0') ||
               (own && *own && *own != '0');
    }();
    if (log_post_consumer) {
        const uint32_t pc = static_cast<uint32_t>(g_rs64_last_guest_pc);
        if (pc >= 0x800356ACu && pc < 0x80035B00u) {
            const auto* vi = ultramodern::renderer::get_vi_regs();
            const uint32_t width = vi->VI_WIDTH_REG;
            const uint32_t origin = vi->VI_ORIGIN_REG & 0x00FFFFFFu;
            const bool target = (width == 1024u && origin == 0x00790400u) ||
                                (width == 512u && origin == 0x006AB400u);
            static uint32_t last_phase = 0xFFFFFFFFu;
            static uint32_t rows = 0;
            const uint32_t phase = rs64_phase_ord();
            if (phase != last_phase) {
                last_phase = phase;
                rows = 0;
            }
            if (target && rows++ < 32u) {
                std::fprintf(stderr,
                    "[m5-post-consumer] pc=0x%08X width=%u origin=0x%06X phase=%u row=%u\n",
                    pc, width, origin, phase, rows - 1u);
                std::fflush(stderr);
            }
        }
    }
    return ultramodern::renderer::get_vi_regs()->VI_WIDTH_REG;
}

extern "C" uint32_t rs64_vi_committed_origin() {
    return ultramodern::renderer::get_vi_regs()->VI_ORIGIN_REG;
}

extern "C" void rs64_vi_fb_wh(uint32_t *out_w, uint32_t *out_h) {
    uint32_t w = 0, h = 0;
    if (out_w != nullptr && out_h != nullptr) {
        const auto regs = *ultramodern::renderer::get_vi_regs();
        RT64::VI vi{};
        vi.status.word = regs.VI_STATUS_REG;
        vi.origin = regs.VI_ORIGIN_REG;
        vi.width = regs.VI_WIDTH_REG;
        vi.vCurrentLine = regs.VI_V_CURRENT_LINE_REG;
        vi.hRegion.word = regs.VI_H_START_REG;
        vi.vRegion.word = regs.VI_V_START_REG;
        vi.xTransform.word = regs.VI_X_SCALE_REG;
        vi.yTransform.word = regs.VI_Y_SCALE_REG;
        if (vi.width && vi.xTransform.xScale && vi.yTransform.yScale &&
            vi.hRegion.hEnd > vi.hRegion.hStart &&
            vi.vRegion.vEnd > vi.vRegion.vStart && vi.fbSiz() >= 2) {
            const auto size = vi.fbSize();
            w = size.x;
            h = size.y;
        }
    }
    if (out_w) *out_w = w;
    if (out_h) *out_h = h;
}

extern "C" uint32_t rs64_phase_ord(void);

extern "C" void rs64_m5_vi_commit_handoff(uint32_t caller,
                                            uint32_t requested_width,
                                            uint32_t mode_ptr) {
    extern void rs64_m5_selector_ai_call_latch_join(uint32_t width,
                                                     uint32_t origin,
                                                     uint32_t phase);
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_TRANSITION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    const auto* vi = ultramodern::renderer::get_vi_regs();
    rs64_m5_selector_ai_call_latch_join(vi->VI_WIDTH_REG,
                                         vi->VI_ORIGIN_REG & 0x00FFFFFFu,
                                         rs64_phase_ord());
    rs64_m5_audio_transition_commit(vi->VI_WIDTH_REG,
                                    vi->VI_ORIGIN_REG & 0x00FFFFFFu,
                                    rs64_phase_ord());
    if (!enabled) return;

    const uint32_t seq = g_m5_vi_commit.next_sequence.fetch_add(1, std::memory_order_relaxed);
    if (seq >= 128u) return;
    g_m5_vi_commit.latest_sequence.store(seq, std::memory_order_release);
    g_m5_vi_commit.caller.store(caller, std::memory_order_relaxed);
    g_m5_vi_commit.requested_width.store(requested_width, std::memory_order_relaxed);
    g_m5_vi_commit.width.store(vi->VI_WIDTH_REG, std::memory_order_relaxed);
    g_m5_vi_commit.origin.store(vi->VI_ORIGIN_REG & 0x00FFFFFFu, std::memory_order_relaxed);
    g_m5_vi_commit.phase.store(rs64_phase_ord(), std::memory_order_relaxed);
    static bool target_control = false;
    if (!target_control && vi->VI_WIDTH_REG >= 640u) {
        std::fprintf(stderr,
            "[m5-port-vi-control] seq=%u caller=0x%08X requested_width=%u "
            "committed_width=%u committed_origin=0x%06X phase=%u\n",
            seq, caller, requested_width, vi->VI_WIDTH_REG,
            vi->VI_ORIGIN_REG & 0x00FFFFFFu, rs64_phase_ord());
        std::fflush(stderr);
        target_control = true;
    }
    if (vi->VI_WIDTH_REG == 1024u &&
        (vi->VI_ORIGIN_REG & 0x00FFFFFFu) == 0x00790400u) {
        std::fprintf(stderr,
            "[m5-port-retail-target] seq=%u caller=0x%08X requested_width=%u "
            "committed_width=%u committed_origin=0x%06X phase=%u\n",
            seq, caller, requested_width, vi->VI_WIDTH_REG,
            vi->VI_ORIGIN_REG & 0x00FFFFFFu, rs64_phase_ord());
        std::fflush(stderr);
    }
    std::fprintf(stderr,
        "[m5-route-transition] edge=vi-commit seq=%u caller=0x%08X "
        "mode_ptr=0x%08X requested_width=%u committed_width=%u "
        "committed_origin=0x%06X phase=%u\n",
        seq, caller, mode_ptr, requested_width, vi->VI_WIDTH_REG,
        vi->VI_ORIGIN_REG & 0x00FFFFFFu, rs64_phase_ord());
    std::fflush(stderr);
}

extern "C" void rs64_m5_route_prepare_handoff(uint32_t prepare_seq,
                                                uint32_t phase,
                                                uint32_t width,
                                                uint32_t origin,
                                                uint32_t accepted) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_TRANSITION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    static std::mutex mutex;
    static uint32_t row_phase = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    std::lock_guard<std::mutex> lock(mutex);
    if (row_phase != phase) {
        row_phase = phase;
        rows = 0;
    }
    if (rows++ >= 32u) return;
    const uint32_t key = (width << 24) ^ (origin & 0x00FFFFFFu);
    const uint32_t commit_key = (g_m5_vi_commit.width.load(std::memory_order_acquire) << 24) ^
                                g_m5_vi_commit.origin.load(std::memory_order_relaxed);
    const uint64_t event = rs64_m5_route_handoff_event(
        "route-prepare", prepare_seq, accepted, "n/a", phase, width,
        origin & 0x00FFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, accepted,
        g_m5_vi_commit.latest_sequence.load(std::memory_order_acquire),
        g_m5_vi_commit.phase.load(std::memory_order_relaxed));
    std::fprintf(stderr,
        "[m5-route-transition] edge=route-prepare seq=%u phase=%u width=%u "
        "origin=0x%06X accepted=%u commit_seq=%u commit_caller=0x%08X "
        "commit_width=%u commit_origin=0x%06X commit_phase=%u key_match=%u "
        "event=%llu\n",
        prepare_seq, phase, width, origin & 0x00FFFFFFu, accepted,
        g_m5_vi_commit.latest_sequence.load(std::memory_order_acquire),
        g_m5_vi_commit.caller.load(std::memory_order_relaxed),
        g_m5_vi_commit.width.load(std::memory_order_relaxed),
        g_m5_vi_commit.origin.load(std::memory_order_relaxed),
        g_m5_vi_commit.phase.load(std::memory_order_relaxed), key == commit_key ? 1u : 0u,
        static_cast<unsigned long long>(event));
    std::fflush(stderr);
}

static thread_local uint32_t g_m5_host_current_seq = 0xFFFFFFFFu;
extern "C" void rs64_m5_host_edge(const char* edge, uint32_t task_seq,
                                    uint32_t data_ptr, uint32_t mq,
                                    uint32_t source, uint32_t sent,
                                    int32_t valid_count, int32_t msg_count);

extern "C" uint32_t rs64_m5_host_action_begin(uint32_t data_ptr) {
    static std::atomic<uint32_t> next_seq{0};
    g_m5_host_current_seq = next_seq.fetch_add(1, std::memory_order_relaxed);
    rs64_m5_host_edge("action-dequeue", g_m5_host_current_seq, data_ptr,
                      0, 0, 1, -1, -1);
    return g_m5_host_current_seq;
}

extern "C" uint32_t rs64_m5_host_send_begin(uint32_t data_ptr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_ORDER");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (enabled) {
        std::fprintf(stderr, "[m5-route-order] edge=send-enter seq=%u data=0x%08X "
                             "phase=%u width=%u origin=0x%06X\n",
                     g_m5_host_current_seq, data_ptr, rs64_phase_ord(),
                     rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu);
        std::fflush(stderr);
    }
    return g_m5_host_current_seq;
}

extern "C" uint32_t rs64_m5_host_current_seq(void) {
    return g_m5_host_current_seq;
}

extern "C" void rs64_m5_host_edge(const char* edge, uint32_t task_seq,
                                    uint32_t data_ptr, uint32_t mq,
                                    uint32_t source, uint32_t sent,
                                    int32_t valid_count, int32_t msg_count) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_ORDER");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (!enabled) return;
    static std::mutex mutex;
    static uint32_t phase = 0xFFFFFFFFu;
    static uint32_t edge_rows[12] = {};
    const uint32_t now_phase = rs64_phase_ord();
    std::lock_guard<std::mutex> lock(mutex);
    if (phase != now_phase) {
        phase = now_phase;
        for (uint32_t& count : edge_rows) count = 0;
    }
    uint32_t edge_index = 11;
    if (edge && std::strcmp(edge, "action-dequeue") == 0) edge_index = 0;
    else if (edge && std::strcmp(edge, "sp-complete-enter") == 0) edge_index = 1;
    else if (edge && std::strcmp(edge, "sp-complete-return") == 0) edge_index = 2;
    else if (edge && std::strcmp(edge, "send-enter") == 0) edge_index = 3;
    else if (edge && std::strcmp(edge, "send-return") == 0) edge_index = 4;
    else if (edge && std::strcmp(edge, "dp-complete") == 0) edge_index = 5;
    else if (edge && std::strcmp(edge, "external-enqueue") == 0) edge_index = 6;
    else if (edge && std::strcmp(edge, "external-delivery") == 0) edge_index = 7;
    else if (edge && std::strcmp(edge, "displaylist-submitted") == 0) edge_index = 8;
    else if (edge && std::strcmp(edge, "displaylist-parsed") == 0) edge_index = 9;
    else if (edge && std::strcmp(edge, "displaylist-completed-enter") == 0) edge_index = 10;
    if (edge_rows[edge_index]++ >= (edge_index == 3 ? 2048u : 512u)) return;
    std::fprintf(stderr,
        "[m5-route-order] edge=%s seq=%u data=0x%08X mq=0x%08X source=%u "
        "sent=%u valid=%d capacity=%d phase=%u width=%u origin=0x%06X\n",
        edge ? edge : "?", task_seq, data_ptr, mq, source, sent,
        valid_count, msg_count, now_phase, rs64_vi_committed_width(),
        rs64_vi_committed_origin() & 0x00FFFFFFu);
    std::fflush(stderr);
}

namespace {

static bool rs64_m5_route_fingerprint_enabled() {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_C88_ROUTE_FINGERPRINT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    return enabled;
}

static std::mutex g_rs64_m5_route_fingerprint_mutex;
static uint32_t g_rs64_m5_route_fingerprint_phase = 0xFFFFFFFFu;
static uint32_t g_rs64_m5_route_fingerprint_width = 0;
static uint32_t g_rs64_m5_route_fingerprint_origin = 0;
static uint32_t g_rs64_m5_route_fingerprint_b40 = 0;
static uint32_t g_rs64_m5_route_fingerprint_route = 0;
static uint32_t g_rs64_m5_route_fingerprint_keyon = 0;
static uint32_t g_rs64_m5_route_fingerprint_last_pc = 0;
static uint32_t g_rs64_m5_route_fingerprint_snapshots = 0;

static bool rs64_m5_route_fingerprint_target(uint32_t width, uint32_t origin) {
    origin &= 0x00FFFFFFu;
    return (width == 640u && (origin == 0x00696100u || origin == 0x00696600u)) ||
           (width == 1024u && origin == 0x00790400u) ||
           (width == 512u && origin == 0x006AB400u);
}

static void rs64_m5_route_fingerprint_reset_locked(uint32_t phase,
                                                    uint32_t width,
                                                    uint32_t origin) {
    g_rs64_m5_route_fingerprint_phase = phase;
    g_rs64_m5_route_fingerprint_width = width;
    g_rs64_m5_route_fingerprint_origin = origin & 0x00FFFFFFu;
    g_rs64_m5_route_fingerprint_b40 = 0;
    g_rs64_m5_route_fingerprint_route = 0;
    g_rs64_m5_route_fingerprint_keyon = 0;
    g_rs64_m5_route_fingerprint_last_pc = 0;
    g_rs64_m5_route_fingerprint_snapshots = 0;
}

// s7715 [s7715-c88]: ROGUESQ_M5_C88_VALUE label = the real 0x8008EC88 store (pass-through unless =0, s2608), so unset
// reads c88=1; the old label (non-'0') said 0 for unset. S7715_C88LBL=0 restores it.
static unsigned rs64_s7715_c88_label(const char* c88) {
    static const int old_label = [] { const char* o = std::getenv("S7715_C88LBL"); return o && o[0] == '0'; }();
    if (old_label) return (c88 && c88[0] && c88[0] != '0') ? 1u : 0u;
    return (c88 && c88[0] == '0') ? 0u : 1u;
}

static void rs64_m5_route_fingerprint_emit_locked(const char* edge) {
    const char* c88 = std::getenv("ROGUESQ_M5_C88_VALUE");
    const unsigned c88_value = rs64_s7715_c88_label(c88);
    std::fprintf(stderr,
        "[m5-route-fingerprint] edge=%s arm=c88_%u c88=%u phase=%u width=%u "
        "origin=0x%06X route_state_count=%u b40_count=%u key_on_count=%u "
        "last_guest_pc=0x%08X snapshot=%u\n",
        edge, c88_value, c88_value, g_rs64_m5_route_fingerprint_phase,
        g_rs64_m5_route_fingerprint_width, g_rs64_m5_route_fingerprint_origin,
        g_rs64_m5_route_fingerprint_route, g_rs64_m5_route_fingerprint_b40,
        g_rs64_m5_route_fingerprint_keyon,
        g_rs64_m5_route_fingerprint_last_pc,
        g_rs64_m5_route_fingerprint_snapshots);
    std::fflush(stderr);
}

static void rs64_m5_route_fingerprint_note_locked(unsigned kind, uint32_t pc) {
    const uint32_t phase = rs64_phase_ord();
    if (g_rs64_m5_route_fingerprint_phase != phase) {
        rs64_m5_route_fingerprint_reset_locked(
            phase, rs64_vi_committed_width(), rs64_vi_committed_origin());
    }
    if (kind == 1u) {
        ++g_rs64_m5_route_fingerprint_b40;
    } else if (kind == 2u) {
        ++g_rs64_m5_route_fingerprint_route;
    } else if (kind == 3u) {
        ++g_rs64_m5_route_fingerprint_keyon;
    }
    if (pc != 0u && pc != 0xFFFFFFFFu) {
        g_rs64_m5_route_fingerprint_last_pc = pc;
    } else if (g_rs64_last_guest_pc != 0u) {
        g_rs64_m5_route_fingerprint_last_pc =
            static_cast<uint32_t>(g_rs64_last_guest_pc);
    }
}

static void rs64_m5_route_fingerprint_note(unsigned kind, uint32_t pc) {
    if (!rs64_m5_route_fingerprint_enabled()) return;
    std::lock_guard<std::mutex> lock(g_rs64_m5_route_fingerprint_mutex);
    rs64_m5_route_fingerprint_note_locked(kind, pc);
}

}

extern "C" void rs64_m5_route_fingerprint_phase(uint32_t width,
                                                   uint32_t origin) {
    if (!rs64_m5_route_fingerprint_enabled()) return;
    std::lock_guard<std::mutex> lock(g_rs64_m5_route_fingerprint_mutex);
    const uint32_t phase = rs64_phase_ord();
    if (g_rs64_m5_route_fingerprint_phase == phase) {
        if (rs64_m5_route_fingerprint_target(
                g_rs64_m5_route_fingerprint_width,
                g_rs64_m5_route_fingerprint_origin)) {
            rs64_m5_route_fingerprint_emit_locked("phase-exit");
        }
    }
    rs64_m5_route_fingerprint_reset_locked(phase + 1u, width, origin);
}

extern "C" void rs64_m5_route_fingerprint_snapshot(uint32_t width,
                                                      uint32_t origin) {
    if (!rs64_m5_route_fingerprint_enabled()) return;
    std::lock_guard<std::mutex> lock(g_rs64_m5_route_fingerprint_mutex);
    const uint32_t phase = rs64_phase_ord();
    if (g_rs64_m5_route_fingerprint_phase != phase) {
        rs64_m5_route_fingerprint_reset_locked(phase, width, origin);
    }
    g_rs64_m5_route_fingerprint_width = width;
    g_rs64_m5_route_fingerprint_origin = origin & 0x00FFFFFFu;
    g_rs64_m5_route_fingerprint_last_pc =
        static_cast<uint32_t>(g_rs64_last_guest_pc);
    const uint32_t snapshot = g_rs64_m5_route_fingerprint_snapshots++;
    if (rs64_m5_route_fingerprint_target(width, origin) &&
        (snapshot < 4u || (snapshot % 64u) == 0u)) {
        rs64_m5_route_fingerprint_emit_locked("snapshot");
    }
}

extern "C" void rs64_m5_route_fingerprint_keyon(uint32_t site) {
    rs64_m5_route_fingerprint_note(3u, site);
}

static std::atomic<uint32_t> g_rs64_m5_b40_route_ordinal{0xFFFFFFFFu};

extern "C" void rs64_m5_b40_route_event(const char* edge, uint32_t pc,
                                         uint32_t b40_stored, uint32_t value,
                                         uint32_t b40_return) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_B40_ROUTE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    rs64_m5_route_fingerprint_note(1u, pc);

    static std::atomic<uint32_t> phase_seen{0xFFFFFFFFu};
    static std::atomic<uint32_t> phase_row{0};
    static std::atomic<uint32_t> last_b40_stored{0xFFFFFFFFu};
    static std::atomic<uint32_t> last_b40_return{0xFFFFFFFFu};
    const uint32_t phase = rs64_phase_ord();
    uint32_t prior = phase_seen.load(std::memory_order_relaxed);
    if (prior != phase && phase_seen.compare_exchange_strong(
            prior, phase, std::memory_order_relaxed)) {
        phase_row.store(0, std::memory_order_relaxed);
    }
    const uint32_t ordinal = phase_row.fetch_add(1, std::memory_order_relaxed);
    g_rs64_m5_b40_route_ordinal.store(ordinal, std::memory_order_relaxed);
    if (ordinal >= 512u) return;

    if (b40_stored != 0xFFFFFFFFu) {
        last_b40_stored.store(b40_stored & 0xFFu, std::memory_order_relaxed);
    }
    if (b40_return != 0xFFFFFFFFu) {
        last_b40_return.store(b40_return, std::memory_order_relaxed);
    }
    const uint32_t stored = last_b40_stored.load(std::memory_order_relaxed);
    const uint32_t returned = last_b40_return.load(std::memory_order_relaxed);
    const char* b40 = std::getenv("ROGUESQ_M5_B40_VALUE");
    const char* c88 = std::getenv("ROGUESQ_M5_C88_VALUE");
    const char* arm = (b40 && b40[0] && b40[0] != '0') ? "treatment" : "control";
    std::fprintf(stderr,
        "[m5-b40-route] arm=%s b40=%u c88=%u ordinal=%u phase=%u width=%u "
        "origin=0x%06X edge=%s pc=0x%08X b40_stored=0x%02X value=0x%08X "
        "b40_return=0x%08X\n",
        arm, (b40 && b40[0] && b40[0] != '0') ? 1u : 0u,
        rs64_s7715_c88_label(c88), ordinal, phase,
        rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu,
        edge ? edge : "?", pc, stored & 0xFFu, value, returned);
    std::fflush(stderr);
}

static thread_local uint32_t g_rs64_m5_route_state_call_ordinal = 0xFFFFFFFFu;
static thread_local uint32_t g_rs64_m5_route_state_entry_a1 = 0xFFFFFFFFu;
static thread_local uint32_t g_rs64_m5_route_state_audio_nonzero = 2u;
static uint32_t rs64_m5_route_state_guest_byte(uint8_t* rdram, uint32_t guest) {
    if (rdram == nullptr || guest < 0x80000000u || guest >= rs64_ram_top) {
        return 0xFFFFFFFFu;
    }
    return rdram[(guest - 0x80000000u) ^ 3u];
}

static void rs64_m5_route_state_log(uint8_t* rdram, const char* edge,
                                     uint32_t pc, uint32_t call_ordinal,
                                     uint32_t a0, uint32_t a1, uint32_t a2,
                                     uint32_t a3, uint32_t a1_gate,
                                     uint32_t audio_nonzero,
                                     uint32_t function_nonzero) {
    const uint32_t phase = rs64_phase_ord();
    rs64_m5_route_fingerprint_note(2u, pc);
    const uint32_t limit = phase == 7u ? 512u : 16u;
    if (call_ordinal >= limit) return;

    const char* b40 = std::getenv("ROGUESQ_M5_B40_VALUE");
    const char* c88 = std::getenv("ROGUESQ_M5_C88_VALUE");
    const uint32_t state_1ad0 = rs64_m5_route_state_guest_byte(rdram, 0x80141AD0u);
    const uint32_t state_3b038 = rs64_m5_route_state_guest_byte(rdram, 0x8013B038u);
    const uint32_t state_1ad1 = rs64_m5_route_state_guest_byte(rdram, 0x80141AD1u);
    const uint32_t audio = audio_nonzero == 0xFFFFFFFFu
        ? g_rs64_m5_route_state_audio_nonzero : audio_nonzero;
    std::fprintf(stderr,
        "[m5-route-state] arm=%s b40=%u c88=%u edge=%s phase=%u target=%u "
        "call_ordinal=%u route_ordinal=%u width=%u origin=0x%06X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X a1_gate=0x%08X "
        "state_1ad0=0x%02X state_3b038=0x%02X state_1ad1=0x%02X "
        "audio_nonzero=%u function_nonzero=%u\n",
        (b40 && b40[0] && b40[0] != '0') ? "treatment" : "control",
        (b40 && b40[0] && b40[0] != '0') ? 1u : 0u,
        rs64_s7715_c88_label(c88),
        edge ? edge : "?", phase, phase == 7u ? 1u : 0u, call_ordinal,
        g_rs64_m5_b40_route_ordinal.load(std::memory_order_relaxed),
        rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu,
        a0, a1, a2, a3, a1_gate, state_1ad0, state_3b038, state_1ad1,
        audio, function_nonzero);
    std::fflush(stderr);
}

extern "C" void rs64_s4714_rec(uint8_t* rdram, uint32_t rec, uint32_t sp, uint32_t a2) {
    static int en = -1;
    if (en < 0) { const char* e = std::getenv("ROGUESQ_LOG_ALLOC_CALLERS"); en = (e && e[0] && e[0] != '0') ? 1 : 0; }
    if (!en) return;
    const uint32_t o = rec & 0x1FFFFFFFu;
    std::fprintf(stderr, "[s4714-rec] rec=0x%08X sp=0x%08X a2=0x%08X w0..3=%08X %08X %08X %08X\n", rec, sp, a2,
        *(uint32_t*)(rdram + o), *(uint32_t*)(rdram + o + 4), *(uint32_t*)(rdram + o + 8), *(uint32_t*)(rdram + o + 12));
    std::fflush(stderr);
}

extern "C" uint32_t rs64_m5_route_state_callsite(uint8_t* rdram,
                                                   uint32_t pc, uint32_t a0,
                                                   uint32_t a1, uint32_t a2,
                                                   uint32_t a3) {
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t next_ordinal = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        next_ordinal = 0;
    }
    g_rs64_m5_route_state_call_ordinal = next_ordinal++;
    g_rs64_m5_route_state_entry_a1 = a1;
    {
        // s4713: guard census. a0..a3 are the mode record at s2: lw 0(s2), lbu 4/5/6(s2).
        static int en = -1;
        if (en < 0) { const char* e = std::getenv("ROGUESQ_LOG_ALLOC_CALLERS"); en = (e && e[0] && e[0] != '0') ? 1 : 0; }
        if (en) {
            static uint32_t n = 0;
            const uint32_t flag = rdram[(0x8010D211u - 0x80000000u) ^ 3u];
            std::fprintf(stderr, "[s4713-rdm-guard] n=%u phase=%u flag8010D211=%u rec_w0=0x%08X b4=%u b5=%u b6=%u\n",
                         ++n, phase, flag, a0, a1, a2, a3);
            std::fflush(stderr);
        }
    }
    g_rs64_m5_route_state_audio_nonzero = 2u;
    const char* all = std::getenv("ROGUESQ_LOG_ALL");
    const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_STATE");
    if ((all && all[0] && all[0] != '0') || (own && own[0] && own[0] != '0')) {
        rs64_m5_route_state_log(rdram, "callsite", pc,
                                g_rs64_m5_route_state_call_ordinal,
                                a0, a1, a2, a3, a1, 0xFFFFFFFFu, 2u);
    }
    return g_rs64_m5_route_state_call_ordinal;
}

extern "C" void rs64_m5_route_state_event(uint8_t* rdram, const char* edge,
                                            uint32_t pc, uint32_t a0,
                                            uint32_t a1, uint32_t a2,
                                            uint32_t a3,
                                            uint32_t audio_nonzero,
                                            uint32_t function_nonzero) {
    const char* all = std::getenv("ROGUESQ_LOG_ALL");
    const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_STATE");
    if (!((all && all[0] && all[0] != '0') ||
          (own && own[0] && own[0] != '0'))) return;

    if (edge && edge[0] == 'e' && edge[1] == 'n') {
        g_rs64_m5_route_state_entry_a1 = a1;
    }
    if (edge && edge[0] == 'a' && edge[1] == 'u') {
        g_rs64_m5_route_state_audio_nonzero = audio_nonzero ? 1u : 0u;
    }
    rs64_m5_route_state_log(rdram, edge, pc,
                            g_rs64_m5_route_state_call_ordinal,
                            a0, a1, a2, a3,
                            g_rs64_m5_route_state_entry_a1,
                            audio_nonzero, function_nonzero);
}

extern "C" void rs64_m5_selector_route_caller(const char* name, uint32_t pc,
                                                uint32_t ra, uint32_t a0,
                                                uint32_t a1, uint32_t a2,
                                                uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_ROUTE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-route-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-route] ordinal=%u phase=%u width=%u origin=0x%06X "
        "name=%s pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, phase, width, origin, name ? name : "?", pc, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_caller_route(const char* edge, uint32_t pc,
                                       uint32_t ra, uint32_t a0, uint32_t a1,
                                       uint32_t a2, uint32_t a3, uint32_t s0,
                                       uint32_t s1, uint32_t s2, uint32_t s3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_CALLER_ROUTE");
        const char* master = std::getenv("ROGUESQ_LOG_ALL");
        return (all && all[0] && all[0] != '0') ||
               (master && master[0] && master[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-caller-route-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    const bool target =
        (width == 1024u &&
         (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target) return;

    uint32_t phase = 0, route_width = width, route_origin = origin;
    uint32_t route_ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &phase, &route_width, &route_origin, &route_ordinal, &route_row,
        &exit_reason, &arm);
    uint64_t source_event = 0;
    uint64_t task_generation = 0;
    uint32_t latest_route_seq = 0xFFFFFFFFu;
    uint32_t latest_route_ordinal = 0xFFFFFFFFu;
    uint32_t latest_route_row = 0xFFFFFFFFu;
    rs64_m5_audio_dma_identity(&source_event, &task_generation,
                               &latest_route_seq, &latest_route_ordinal,
                               &latest_route_row);
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
    }
    if (rows >= 512u) return;
    if (rows == 0u) {
        std::fprintf(stderr,
            "[m5-caller-route-phase-control] phase=%u width=%u origin=0x%06X\n",
            rs64_phase_ord(), width, origin);
    }
    std::fprintf(stderr,
        "[m5-caller-route] row=%u edge=%s pc=0x%08X ra=0x%08X "
        "phase=%u width=%u origin=0x%06X active=%u arm=%s "
        "route_ordinal=%u route_row=%u exit=%d "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X s3=0x%08X "
        "source_event=%llu task_generation=%llu latest_route_seq=%u "
        "latest_route_ordinal=%u latest_route_row=%u\n",
        rows++, edge ? edge : "?", pc, ra, active ? phase : rs64_phase_ord(),
        active ? route_width : width, active ? route_origin : origin,
        active ? 1u : 0u, active && arm ? arm : "n/a",
        active ? route_ordinal : 0xFFFFFFFFu,
        active ? route_row : 0xFFFFFFFFu, exit_reason, a0, a1, a2, a3,
        s0, s1, s2, s3, static_cast<unsigned long long>(source_event),
        static_cast<unsigned long long>(task_generation), latest_route_seq,
        latest_route_ordinal, latest_route_row);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_mixer_callsite(const char* name,
                                                   uint32_t pc, uint32_t ra,
                                                   uint32_t a0, uint32_t a1,
                                                   uint32_t a2, uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_MIXER_CALLSITE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    {   // s4712: ungated census of initAudioSubsystem / reapplyAudioConfig initN64RspMixer call sites
        static const bool census = [] {
            const char* e = std::getenv("ROGUESQ_LOG_ALLOC_CALLERS");
            return e && e[0] && e[0] != '0';
        }();
        static uint32_t cn = 0;
        if (census && cn < 256u) {
            std::fprintf(stderr, "[s4712-mixer-callsite] n=%u name=%s pc=0x%08X ra=0x%08X width=%u origin=0x%06X\n",
                cn++, name ? name : "?", pc, ra, rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu);
            std::fflush(stderr);
        }
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-mixer-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-selector-mixer] ordinal=%u phase=%u width=%u origin=0x%06X "
        "name=%s pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, phase, width, origin, name ? name : "?", pc, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_s3352_m5_consumer_entry(uint8_t* rdram, uint32_t pc) {
    (void)rdram;
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_CONSUMER_ENTRY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-consumer-entry-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && (origin == 0x006AB400u || origin == 0x006AB800u)))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 128u) return;
    std::fprintf(stderr,
        "[m5-consumer-entry] ordinal=%u phase=%u width=%u origin=0x%06X pc=0x%08X\n",
        rows++, phase, width, origin, pc);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_tick_edge(const char* edge, uint32_t pc,
                                              uint32_t taken, uint32_t a0,
                                              uint32_t a1, uint32_t a2,
                                              uint32_t a3, uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_TICK");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-tick-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && (origin == 0x006AB400u || origin == 0x006AB800u)))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-tick] ordinal=%u phase=%u width=%u origin=0x%06X "
        "edge=%s pc=0x%08X taken=%u a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X value=0x%08X\n",
        rows++, phase, width, origin, edge ? edge : "?", pc, taken,
        a0, a1, a2, a3, value);
    std::fflush(stderr);
}

extern "C" void rs64_m5_route_candidate(uint8_t* rdram, uint32_t pc,
                                           uint32_t caller, uint32_t s0,
                                           uint32_t s1, uint32_t a0,
                                           uint32_t a1, uint32_t a2,
                                           uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_CANDIDATE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || rdram == nullptr) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    const auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint8_t* p = rdram + (guest - 0x80000000u);
        return (static_cast<uint32_t>(p[3]) << 24) |  /* s7601 BS: was p[0]<<24.. = byte-reversed word */
               (static_cast<uint32_t>(p[2]) << 16) |
               (static_cast<uint32_t>(p[1]) << 8) | p[0];
    };
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    std::fprintf(stderr,
        "[m5-route-candidate] n=%u phase=%u width=%u origin=0x%06X "
        "arm=%s active=%u ordinal=%u row=%u pc=0x%08X caller=0x%08X "
        "s0=0x%08X s1=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X v0=0x%08X "
        "m0=0x%08X m4=0x%08X m8=0x%08X mc=0x%08X st1ad0=0x%02X "
        "st3b038=0x%02X st1ad1=0x%02X exit=%d\n",
        rows, rs64_phase_ord(), width, origin, arm ? arm : "n/a",
        active ? 1u : 0u, ordinal, route_row, pc, caller, s0, s1, a0,
        a1, a2, v0, word(a0), word(a0 + 4u), word(a0 + 8u), word(a0 + 12u),
        rs64_m5_route_state_guest_byte(rdram, 0x80141AD0u),
        rs64_m5_route_state_guest_byte(rdram, 0x8013B038u),
        rs64_m5_route_state_guest_byte(rdram, 0x80141AD1u), exit_reason);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_route_exact_load(uint8_t* rdram, uint32_t pc,
                                           uint32_t base, uint32_t offset,
                                           uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_EXACT_LOAD");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || rdram == nullptr) return;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-route-exact-control] pc=0x%08X base=0x%08X offset=0x%X value=0x%08X\n",
            pc, base, offset, value);
        std::fflush(stderr);
    }
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target_phase = (width == 1024u && origin == 0x00790400u) ||
                              (width == 512u && origin == 0x006AB400u);
    if (!target_phase || base != 0x80128C70u) return;
    static std::mutex mutex;
    static uint32_t rows[2] = {};
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 512u) return;
    uint32_t route_ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &route_ordinal, &route_row, &exit_reason,
        &arm);
    std::fprintf(stderr,
        "[m5-route-exact-load] row=%u phase=%u width=%u origin=0x%06X arm=%s "
        "pc=0x%08X base=0x%08X offset=0x%X value=0x%08X source_event=%llu "
        "route_ordinal=%u route_row=%u active=%u exit=%d\n",
        rows[slot]++, rs64_phase_ord(), width, origin, arm ? arm : "n/a", pc,
        base, offset, value,
        static_cast<unsigned long long>(rs64_m5_clear_branch_source_sequence()),
        route_ordinal, route_row, active ? 1u : 0u, exit_reason);
    std::fflush(stderr);
}

extern "C" void rs64_m5_audio_channel_load(uint8_t* rdram, uint32_t pc,
                                               uint32_t base, uint32_t offset,
                                               uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_AUDIO_CHANNEL_LOAD");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || rdram == nullptr || pc != 0x8008D5E4u) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target_phase = (width == 1024u && origin == 0x00790400u) ||
                              (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static std::mutex mutex;
    static bool control_seen = false;
    static uint32_t rows[2] = {};
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-audio-channel-load-control] pc=0x%08X base=0x%08X offset=0x%X value=0x%08X\n",
            pc, base, offset, value);
        std::fflush(stderr);
    }
    if (rows[slot] >= 128u) return;
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    std::fprintf(stderr,
        "[m5-audio-channel-load] row=%u phase=%u width=%u origin=0x%06X arm=%s "
        "pc=0x%08X base=0x%08X offset=0x%X effective=0x%08X value=0x%02X "
        "route_ordinal=%u route_row=%u active=%u exit=%d\n",
        rows[slot]++, rs64_phase_ord(), width, origin, arm ? arm : "n/a", pc,
        base, offset, base + offset, value & 0xFFu, ordinal, route_row,
        active ? 1u : 0u, exit_reason);
    std::fflush(stderr);
}

static bool rs64_m5_voice_modulation_enabled() {
    const char* all = std::getenv("ROGUESQ_LOG_ALL");
    const char* own = std::getenv("ROGUESQ_LOG_M5_VOICE_MODULATION");
    return (all && all[0] && all[0] != '0') ||
           (own && own[0] && own[0] != '0');
}

static bool rs64_m5_voice_modulation_phase(uint32_t* width, uint32_t* origin) {
    *width = rs64_vi_committed_width();
    *origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    return (*width == 1024u && *origin == 0x00790400u) ||
           (*width == 512u && *origin == 0x006AB400u);
}

static bool rs64_m5_voice_callee_detail_active = false;
static bool rs64_m5_voice_callee_detail_pending = false;

extern "C" void rs64_m5_voice_modulation_callee_detail(
    uint8_t* rdram, uint32_t pc, uint32_t ra, uint32_t kind,
    uint32_t ptr, uint32_t value, uint32_t aux);

extern "C" void rs64_m5_voice_modulation_setup(uint8_t* rdram, uint32_t pc,
                                                   uint32_t s2, uint32_t s3,
                                                   uint32_t s0, uint32_t v1,
                                                   uint32_t a1, uint32_t a2,
                                                   uint32_t a3, uint32_t scaled) {
    if (!rdram || !rs64_m5_voice_modulation_enabled()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static uint32_t rows[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 128u) return;
    std::fprintf(stderr,
        "[m5-voice-mod-setup] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "s2=0x%08X s3=0x%08X s0=0x%08X v1=0x%08X "
        "a1=0x%08X a2=0x%08X a3=0x%08X scaled=0x%08X\n",
        rows[slot]++, rs64_phase_ord(), width, origin, pc, s2, s3, s0, v1,
        a1, a2, a3, scaled);
    std::fflush(stderr);
}

extern "C" void rs64_m5_voice_modulation_pre_setup(
    uint8_t* rdram, uint32_t pc, uint32_t s2, uint32_t s3, uint32_t s0,
    uint32_t v0, uint32_t v1, uint32_t a0) {
    if (!rdram || !rs64_m5_voice_modulation_enabled()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static uint32_t rows[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 256u) return;
    std::fprintf(stderr,
        "[m5-voice-mod-pre] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X s2=0x%08X s3=0x%08X s0=0x%08X "
        "v0=0x%08X v1=0x%08X a0=0x%08X\n",
        rows[slot]++, rs64_phase_ord(), width, origin, pc, s2, s3, s0,
        v0, v1, a0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_voice_modulation_arithmetic(
    uint8_t* rdram, uint32_t pc, uint32_t lhs, uint32_t rhs,
    uint32_t s2, uint32_t s3, uint32_t s0, uint32_t v0, uint32_t v1,
    uint32_t a0) {
    if (!rdram || !rs64_m5_voice_modulation_enabled()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static uint32_t rows[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 128u) return;
    std::fprintf(stderr,
        "[m5-voice-mod-arith] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X lhs=0x%08X rhs=0x%08X s2=0x%08X s3=0x%08X "
        "s0=0x%08X v0=0x%08X v1=0x%08X a0=0x%08X\n",
        rows[slot]++, rs64_phase_ord(), width, origin, pc, lhs, rhs, s2,
        s3, s0, v0, v1, a0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_voice_modulation_postcall(uint8_t* rdram, uint32_t pc,
                                                    uint32_t s3, uint32_t v0) {
    if (!rdram || !rs64_m5_voice_modulation_enabled()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static bool control_emitted = false;
    if (pc == 0x8008D604u && !control_emitted) {
        control_emitted = true;
        rs64_m5_voice_modulation_callee_detail(
            rdram, 0xC0DEC002u, 0u, 0u, 0u, 0xC0DEu, 0xD604u);
    }
    static uint32_t rows[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 256u) return;
    std::fprintf(stderr,
        "[m5-voice-mod-post] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X s3=0x%08X v0=0x%08X\n",
        rows[slot]++, rs64_phase_ord(), width, origin, pc, s3, v0);
    std::fflush(stderr);
}


static bool rs64_s4222_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4222"); return e && e[0] && e[0] != '0'; }(); return on; }
// s4231: 1 ms poll of allocator list words (head 0x801499E4, tail 0x801499B4, pool 0x801499CC); logs every change with last guest pc
extern "C" void rs64_s4230_poll_start(uint8_t* rdram) {
    static std::atomic<bool> started{false};
    if (!rdram || !rs64_s4222_on() || started.exchange(true)) return;
    if (const char* e = std::getenv("ROGUESQ_LOG_S4299P"); e && e[0] && e[0] != '0') {
        // s4299: 200 us poll of the stream-node block 0x17D000..0x17E200; logs each word that becomes 4 printable ASCII bytes
        // (the name-text-over-ROM-pair corruption) with last guest pc, plus total change count as the positive control.
        std::thread([rdram] {
            static uint32_t prev[0x1200 / 4]; bool init = false; unsigned long changes = 0, ticks = 0; int rows = 0, ctl = 0;
            auto asc = [](uint32_t v) { for (int i = 0; i < 4; i++) { uint32_t b = (v >> (8 * i)) & 0xFF; if (b < 0x20 || b > 0x7E) return false; } return true; };
            for (;;) {
                for (uint32_t i = 0; i < 0x1200 / 4; i++) {
                    uint32_t c = *(volatile uint32_t*)(rdram + 0x17D000u + i * 4u);
                    if (!init) { prev[i] = c; continue; }
                    if (c == prev[i]) continue;
                    changes++;
                    if (ctl < 5) { ctl++; std::fprintf(stderr, "[s4299-P] control change addr=%06X %08X -> %08X pc=%08X\n", 0x17D000u + i * 4u, prev[i], c, (unsigned)g_rs64_last_guest_pc); }
                    if (asc(c) && !asc(prev[i]) && rows < 6000 && (c == 0x6C746578u || (i & 7) == 0)) { rows++; std::fprintf(stderr, "[s4299-P] ASCII addr=%06X %08X -> %08X t=%lu changes=%lu pc=%08X width=%u\n", 0x17D000u + i * 4u, prev[i], c, ticks, changes, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); }
                    prev[i] = c;
                }
                init = true; ticks++;
                if ((ticks % 20000) == 0) std::fprintf(stderr, "[s4299-P] alive ticks=%lu changes=%lu\n", ticks, changes);
                std::this_thread::sleep_for(std::chrono::microseconds(200));
            }
        }).detach();
    }
    if (const char* e = std::getenv("ROGUESQ_LOG_S4526"); e && e[0] && e[0] != '0') {
        // s4526: every 5 ms walk the node lists at 0x1499B4/0x1499E4 (node = {romA,romB,size,dram,prev,next}, next at +0x14)
        // and scan the voice array; log the FIRST hits where any node address / node word / voice word lies in
        // 0x8017D000..0x80188000. That 40-hit cap is spent on 0x8017D030, which is below the freed block.
        // s4529: a second cap snapshots a chain whose head or any node lies in [0x8017D910, 0x80189340).
        // Dumping every poll would spend all 30 slots on the first head (~150 ms) and miss the later one,
        // so a new head gets itself plus 4 more polls, and later word changes are at most 8 snapshots
        // >=200 ms apart. Guest pc is not logged on those lines: it is not the store.
        std::thread([rdram] {
            const auto W = [rdram](uint32_t g) -> uint32_t { g &= 0x1FFFFFFFu; return g < (rs64_ram_top - 0x80000000u) ? *(volatile uint32_t*)(rdram + (g & ~3u)) : 0u; };
            const auto in = [](uint32_t v) { return v >= 0x8017D000u && v < 0x80188000u; };
            const auto freed = [](uint32_t v) { return v >= 0x8017D910u && v < 0x80189340u; };
            unsigned long ticks = 0; int hits = 0; int snaps = 0; int repeat_snaps = 0; bool cap_logged = false;
            uint32_t lastlen[2] = {0, 0};
            uint32_t last_sig[2] = {0, 0};
            uint32_t last_head[2] = {0xFFFFFFFFu, 0xFFFFFFFFu};
            unsigned long last_snap_tick[2] = {0, 0};
            int burst[2] = {0, 0};
            bool have_sig[2] = {false, false};
            // Head-in-block cap is separate. The shared cap above is spent at width 1024 on
            // next-pointers into the block (heads still 0x80192Cxx) and never sees the
            // VI-512 heads 0x8017DA10 / 0x8017D9E0.
            int head_snaps = 0; int head_repeat = 0; bool head_cap_logged = false;
            uint32_t head_sig_last[2] = {0, 0};
            uint32_t head_addr_last[2] = {0xFFFFFFFFu, 0xFFFFFFFFu};
            unsigned long head_tick_last[2] = {0, 0};
            int head_burst[2] = {0, 0};
            bool head_have[2] = {false, false};
            for (;;) {
                const uint32_t heads[2] = {0x1499B4u, 0x1499E4u};
                for (int l = 0; l < 2; l++) {
                    uint32_t rec[64][4];
                    uint32_t nstored = 0;
                    bool trunc = false;
                    bool in_freed = false;
                    uint32_t head = W(heads[l]);
                    if (freed(head)) in_freed = true;
                    uint32_t n = head, len = 0, sig = head;
                    while (n >= 0x80000000u && n < rs64_ram_top && len < 2100) {
                        len++;
                        uint32_t words[6];
                        for (uint32_t k = 0; k < 6; k++) words[k] = W(n + k * 4);
                        if (freed(n)) in_freed = true;
                        sig = (sig * 16777619u) ^ n ^ words[0] ^ (words[1] * 0x9E3779B9u) ^ words[5] ^ (len * 0x85EBCA6Bu);
                        if (nstored < 64) { rec[nstored][0] = n; rec[nstored][1] = words[0]; rec[nstored][2] = words[1]; rec[nstored][3] = words[5]; nstored++; }
                        else trunc = true;
                        if (in(n) && hits < 40) { hits++; std::fprintf(stderr, "[s4526-P] NODE-IN-RANGE list=%d idx=%u node=%08X t=%lu pc=%08X width=%u\n", l, len, n, ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); }
                        for (uint32_t k = 0; k < 6; k++) { if (in(words[k]) && k != 3 && hits < 40) { hits++; std::fprintf(stderr, "[s4526-P] LINK-IN-RANGE list=%d idx=%u node=%08X word%u=%08X t=%lu pc=%08X width=%u\n", l, len, n, k, words[k], ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); } }
                        n = words[5];
                    }
                    if (len != lastlen[l]) { lastlen[l] = len; std::fprintf(stderr, "[s4526-P] chain list=%d len=%u head=%08X t=%lu pc=%08X width=%u\n", l, len, W(heads[l]), ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); }
                    if (!in_freed) burst[l] = 0;
                    else if (snaps < 30) {
                        bool new_head = !have_sig[l] || head != last_head[l];
                        bool sig_changed = !have_sig[l] || sig != last_sig[l];
                        bool cooled = have_sig[l] && (ticks - last_snap_tick[l]) >= 40;
                        const char* kind = nullptr;
                        if (new_head) { kind = "head"; burst[l] = 4; }
                        else if (burst[l] > 0) { kind = "burst"; burst[l]--; }
                        else if (sig_changed && cooled && repeat_snaps < 8) { kind = "change"; repeat_snaps++; }
                        if (kind) {
                            snaps++;
                            have_sig[l] = true;
                            last_sig[l] = sig;
                            last_head[l] = head;
                            last_snap_tick[l] = ticks;
                            std::fprintf(stderr, "[s4529-P] SNAP n=%d list=%d kind=%s len=%u head=%08X stored=%u width=%u t=%lu\n", snaps, l, kind, len, head, nstored, rs64_vi_committed_width(), ticks);
                            for (uint32_t i = 0; i < nstored; i++) {
                                std::fprintf(stderr, "[s4529-P] NODE snap=%d list=%d idx=%u addr=%08X w0=%08X w1=%08X w5=%08X\n", snaps, l, i + 1, rec[i][0], rec[i][1], rec[i][2], rec[i][3]);
                            }
                            if (trunc) std::fprintf(stderr, "[s4529-P] TRUNC snap=%d list=%d len=%u stored=%u\n", snaps, l, len, nstored);
                            std::fflush(stderr);
                        }
                    } else if (!cap_logged) {
                        cap_logged = true;
                        std::fprintf(stderr, "[s4529-P] SNAP-CAP snaps=%d width=%u t=%lu\n", snaps, rs64_vi_committed_width(), ticks);
                        std::fflush(stderr);
                    }
                    if (!freed(head)) head_burst[l] = 0;
                    else if (head_snaps < 30) {
                        bool new_head = !head_have[l] || head != head_addr_last[l];
                        bool sig_changed = !head_have[l] || sig != head_sig_last[l];
                        bool cooled = head_have[l] && (ticks - head_tick_last[l]) >= 200;
                        const char* hkind = nullptr;
                        if (new_head) { hkind = "head"; head_burst[l] = 4; }
                        else if (head_burst[l] > 0) { hkind = "burst"; head_burst[l]--; }
                        else if (sig_changed && cooled && head_repeat < 6) { hkind = "change"; head_repeat++; }
                        if (hkind) {
                            head_snaps++;
                            head_have[l] = true;
                            head_sig_last[l] = sig;
                            head_addr_last[l] = head;
                            head_tick_last[l] = ticks;
                            std::fprintf(stderr, "[s4529-H] SNAP n=%d list=%d kind=%s len=%u head=%08X stored=%u width=%u t=%lu\n", head_snaps, l, hkind, len, head, nstored, rs64_vi_committed_width(), ticks);
                            for (uint32_t i = 0; i < nstored; i++) {
                                std::fprintf(stderr, "[s4529-H] NODE snap=%d list=%d idx=%u addr=%08X w0=%08X w1=%08X w5=%08X\n", head_snaps, l, i + 1, rec[i][0], rec[i][1], rec[i][2], rec[i][3]);
                            }
                            if (trunc) std::fprintf(stderr, "[s4529-H] TRUNC snap=%d list=%d len=%u stored=%u\n", head_snaps, l, len, nstored);
                            std::fflush(stderr);
                        }
                    } else if (!head_cap_logged) {
                        head_cap_logged = true;
                        std::fprintf(stderr, "[s4529-H] SNAP-CAP snaps=%d width=%u t=%lu\n", head_snaps, rs64_vi_committed_width(), ticks);
                        std::fflush(stderr);
                    }
                }
                const uint32_t vb = W(0x1496F8u); const uint32_t vc = (W(0x149700u) >> 16) & 0xFFFFu;
                if (vb >= 0x80000000u && vb < rs64_ram_top && vc && vc < 512) {
                    for (uint32_t o = 0; o < vc * 0x40u && o < 0x8000u; o += 4) { uint32_t v = W(vb + o); if (in(v) && hits < 40) { hits++; std::fprintf(stderr, "[s4526-P] VOICE-IN-RANGE base=%08X cnt=%u off=%04X word=%08X t=%lu pc=%08X width=%u\n", vb, vc, o, v, ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); } }
                }
                ticks++; if ((ticks % 400) == 0) std::fprintf(stderr, "[s4526-P] alive ticks=%lu len0=%u len1=%u voicebase=%08X cnt=%u\n", ticks, lastlen[0], lastlen[1], vb, vc);
                std::this_thread::sleep_for(std::chrono::milliseconds(5));
            }
        }).detach();
    }
    std::thread([rdram] {
        uint32_t pv[3] = {0xDEADBEEFu, 0xDEADBEEFu, 0xDEADBEEFu}; int rows = 0; unsigned long ticks = 0;
        static const uint32_t A[3] = {0x1499E4u, 0x1499B4u, 0x1499CCu};
        for (;;) {
            for (int i = 0; i < 3; i++) {
                uint32_t c = *(volatile uint32_t*)(rdram + A[i]);
                if (c != pv[i] && rows < 400) { rows++; std::fprintf(stderr, "[s4231-P] t=%lu %s %08X -> %08X pc=%08X\n", ticks, i==0?"head":i==1?"tail":"pool", pv[i], c, (unsigned)g_rs64_last_guest_pc); pv[i] = c; }
            }
            ticks++; std::this_thread::sleep_for(std::chrono::microseconds(200));
        }
    }).detach();
}
extern "C" void rs64_s4222_chain(uint8_t* rdram, uint32_t which, uint32_t s1, uint32_t s2, uint32_t s3, uint32_t s4, uint32_t fp) {
    if (!rdram || !rs64_s4222_on()) return;
    {   // ungated tripwire on the volume-settings bytes 0x80130B60..62
        static uint32_t prev = 0xFFFFFFFFu; static int rows_t = 0;
        uint32_t cur = 0; for (int j = 0; j < 3; j++) cur = (cur << 8) | rdram[(0x80130B60u + j) & 0x1FFFFFFFu ^ 3];
        if (cur != prev && rows_t < 40) {
            rows_t++;
            std::fprintf(stderr, "[s4222-T] vol %06X -> %06X width=%u last_guest_pc=%08X\n", prev & 0xFFFFFF, cur, rs64_vi_committed_width(), (unsigned)g_rs64_last_guest_pc);
            prev = cur;
        }
    }
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static uint32_t rows[2][2] = {}; static unsigned long calls[2][2] = {}, nz[2][2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    calls[slot][which]++; if (s2) nz[slot][which]++;
    if (rows[slot][which] >= 48u) return;
    rows[slot][which]++;
    const auto w = [rdram](uint32_t g) -> uint32_t { if (g < 0x80000000u || g > 0x807FFFFCu) return 0xFFFFFFFFu; const uint8_t* p = rdram + (g - 0x80000000u); return ((uint32_t)p[3] << 24) | ((uint32_t)p[2] << 16) | ((uint32_t)p[1] << 8) | p[0]; };
    // rdram is stored host-word-swapped (byte ^ 3): reuse the idiom from s4221
    const auto W = [rdram](uint32_t a) { uint32_t v = 0; for (int k = 0; k < 4; k++) v = (v << 8) | rdram[((a + k) & 0x1FFFFFFFu) ^ 3]; return v; };
    const auto H = [rdram](uint32_t a) { uint32_t v = 0; for (int k = 0; k < 2; k++) v = (v << 8) | rdram[((a + k) & 0x1FFFFFFFu) ^ 3]; return v; };
    const auto B = [rdram](uint32_t a) { return (uint32_t)rdram[(a & 0x1FFFFFFFu) ^ 3]; };
    (void)w;
    const uint32_t base = 0x80140000u + s1;
    if (which == 0) {
        const uint32_t idx = B(base - 0x26C6), grp = B(base - 0x2751);
        std::fprintf(stderr, "[s4222-A] w=%u n=%lu nzs2=%lu s1=%08X s2=%08X raw(-2750)=%08X rec(-275C)=%08X idx=%u t1B30=%04X t1B18=%04X m370=%04X flag(-2730)=%02X grp=%02X t1AD8=%02X s3=%08X s4=%02X\n",
            width, calls[slot][0], nz[slot][0], s1, s2, W(base - 0x2750), W(base - 0x275C), idx, H(0x80141B30u + idx * 40u), H(0x80141B18u + idx * 40u), H(0x80141B18u + 0x370u), B(base - 0x2730), grp, grp == 0xFF ? 0xFFu : B(0x80141AD8u + grp), s3, s4 & 0xFF);
    } else {
        const uint32_t s0 = s1 + fp;
        std::fprintf(stderr, "[s4222-B] w=%u n=%lu nzs2=%lu s1=%08X s2(final)=%08X s3=%08X s0rec=%08X lerp@C0=%04X D2=%04X E4=%04X 150=%04X byteMasterOn(80148...)=%02X\n",
            width, calls[slot][1], nz[slot][1], s1, s2, s3, s0, H(s0 + 0xC0), H(s0 + 0xD2), H(s0 + 0xE4), H(s0 + 0x150), B(0x80150000u - 0x7C38u));
    }
    std::fflush(stderr);
}

extern "C" void rs64_s4222_pc(uint8_t* rdram, uint32_t pc, uint32_t addr, uint32_t val, uint32_t t1, uint32_t s0) {
    if (!rdram || !rs64_s4222_on()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static unsigned long cnt[2][16] = {}; static uint32_t pcs[16] = {}; static int npc = 0;
    int k = -1; for (int i = 0; i < npc; i++) if (pcs[i] == pc) { k = i; break; }
    if (k < 0) { if (npc >= 16) return; k = npc; pcs[npc++] = pc; }
    const uint32_t slot = width == 1024u ? 0u : 1u;
    const unsigned long n = ++cnt[slot][k];
    if (n <= 12 || (n & (n - 1)) == 0) std::fprintf(stderr, "[s4222-W] w=%u pc=%08X n=%lu at=%08X v0=%08X t1=%08X s0=%08X\n", width, pc, n, addr, val, t1, s0);
}

extern "C" void rs64_s4222_cmd(uint8_t* rdram, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t sp, uint32_t ra) {
    if (!rdram || !rs64_s4222_on()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static unsigned long n[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (++n[slot] > 400) return;
    uint32_t s10 = 0; for (int k = 0; k < 4; k++) s10 = (s10 << 8) | rdram[((sp + 0x10 + k) & 0x1FFFFFFFu) ^ 3];
    std::fprintf(stderr, "[s4222-C] w=%u n=%lu a0=%08X a1=%08X a2=%08X a3=%08X sp10=%08X ra=%08X\n", width, n[slot], a0, a1, a2, a3, s10, ra);
}

extern "C" void rs64_s4222_vol(uint8_t* rdram, uint32_t pc, uint32_t a0) {
    if (!rdram || !rs64_s4222_on()) return;
    static unsigned long cnt[16] = {}; static uint32_t pcs[16] = {}; static int npc = 0;
    int k = -1; for (int i = 0; i < npc; i++) if (pcs[i] == pc) { k = i; break; }
    if (k < 0) { if (npc >= 16) return; k = npc; pcs[npc++] = pc; }
    const unsigned long n = ++cnt[k];
    if (n > 16 && (n & (n - 1)) != 0) return;
    const auto B = [rdram](uint32_t a) { return (uint32_t)rdram[(a & 0x1FFFFFFFu) ^ 3]; };
    uint32_t fl = 0; for (int j = 0; j < 4; j++) fl = (fl << 8) | B(0x80130B50u + j);
    std::fprintf(stderr, "[s4222-V] w=%u pc=%08X n=%lu a0=%08X vol=%02X,%02X,%02X b23=%02X flags=%08X\n", rs64_vi_committed_width(), pc, n, a0, B(0x80130B60u), B(0x80130B61u), B(0x80130B62u), B(0x80130B63u), fl);
}

extern "C" volatile unsigned rs64_s4234_g = 0;

static struct { uint32_t pc, addr, n; char w; } s4279_rg[96]; static unsigned s4279_rgi = 0;
static void s4279_ring_push(uint32_t pc, uint32_t addr, char w) { auto& e = s4279_rg[s4279_rgi++ % 96]; e.pc = pc; e.addr = addr; e.n = rs64_s4234_g; e.w = w; }
extern "C" void rs64_s4279_dump_ring(void) {
    std::fprintf(stderr, "[s4279-ring] last 96 node-region stores (oldest first)\n");
    for (unsigned k = 0; k < 96; k++) { auto& e = s4279_rg[(s4279_rgi + k) % 96]; if (e.pc) std::fprintf(stderr, "[s4279-ring] n=%u pc=%08X %c addr=%08X\n", e.n, e.pc, e.w, e.addr); }
}
extern "C" void rs64_s4222_store_watch(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    if (rs64_s4222_on()) {
        uint32_t np = addr & 0x1FFFFFFFu;
        if (np >= 0x1F9C00u && np < 0x1FB400u) {
            s4279_ring_push(pc, addr, width);
            static unsigned long own = 0; static int frows = 0;
            if (pc >= 0x8008F780u && pc < 0x8008FF00u) {
                ++own;
                if (own == 1 || own == 100 || (own % 20000) == 0)
                    std::fprintf(stderr, "[s4279-own] n=%u cnt=%lu pc=%08X addr=%08X\n", rs64_s4234_g, own, pc, addr);
            } else if (frows < 400) {
                ++frows;
                std::fprintf(stderr, "[s4279-foreign] n=%u pc=%08X %c addr=%08X val=%08X\n", rs64_s4234_g, pc, width, addr, value);
            }
            return;
        }
    }
    if (!rs64_s4222_on() || rs64_s4234_g < 9400u) return;
    static int rows = 0;
    static uint32_t last[64];  // s4230: drop value-unchanged rewrites (tail loop at 0x8008FBE8 was 5553/6000 rows)
    { // s4239 ring: aggregate per store PC
        static struct { uint32_t pc; unsigned long n; } pcs[64];
        static int npc = 0;
        int k = 0; while (k < npc && pcs[k].pc != pc) k++;
        if (k == npc && npc < 64) { pcs[npc].pc = pc; pcs[npc].n = 0; npc++; }
        if (k >= 64) return;
        unsigned long c = ++pcs[k].n;
        if (c == 1 || (c % 500) == 0)
            std::fprintf(stderr, "[s4239-ringS] w=%u pc=%08X %c addr=%08X val=%08X cnt=%lu\n", rs64_vi_committed_width(), pc, width, addr, value, c);
        /* s4278: fall through to per-write rows */
    }
    uint32_t li = (addr >> 2) & 63u;
    if (last[li] == value + 1u) return;
    last[li] = value + 1u;
    if (rows >= 40000) return;
    rows++;
    std::fprintf(stderr, "[s4222-S] w=%u pc=%08X %c addr=%08X val=%08X\n", rs64_vi_committed_width(), pc, width, addr, value);
}

extern "C" void rs64_s4223_stk(uint8_t* rdram, uint32_t pc, uint32_t sp, uint32_t v0) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4223"); return e && e[0] && e[0] != '0'; }();
    if (!rdram || !on) return;
    static int n = 0; if (++n > 64) return;
    std::fprintf(stderr, "[s4223-stk] pc=%08X sp=%08X v0=%08X stk=", pc, sp, v0);
    for (uint32_t o = 0x18; o < 0x90; o += 4) {
        const uint32_t a = (sp + o) & 0x1FFFFFFFu;
        const uint32_t w = (uint32_t(rdram[(a + 0) ^ 3]) << 24) | (uint32_t(rdram[(a + 1) ^ 3]) << 16) | (uint32_t(rdram[(a + 2) ^ 3]) << 8) | rdram[(a + 3) ^ 3];
        std::fprintf(stderr, "%08x,", w);
    }
    std::fprintf(stderr, "\n");
}

extern "C" void rs64_s4223_memcpy(uint8_t* rdram, uint32_t dst, uint32_t src, uint32_t len, uint32_t ra) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4223"); return e && e[0] && e[0] != '0'; }();
    if (!rdram || !on || dst != 0x8013A5C0u) return;
    static int n = 0; if (++n > 16) return;
    std::fprintf(stderr, "[s4223-memcpy] ra=%08X dst=%08X src=%08X len=%u src+0x10=", ra, dst, src, len);
    for (uint32_t o = 0x10; o < 0x20; o++) std::fprintf(stderr, "%02x", rdram[((src + o) & 0x1FFFFFFFu) ^ 3]);
    std::fprintf(stderr, "\n");
}

struct S4299Ent { uint32_t pc, addr; uint32_t seq; char w; const char* fn; };
static S4299Ent g_s4299_ring[1 << 20];
static unsigned long g_s4299_total = 0;
static unsigned long g_s4299_swlr_total = 0;
struct S4307Writer { uint32_t ordinal, pc, addr, requested, post; };
static S4307Writer g_s4307_last_writer{};
extern "C" void rs64_s4307_note_writer(uint32_t ordinal, uint32_t pc,
                                         uint32_t addr, uint32_t requested,
                                         uint32_t post);
#include <map>
#include <vector>
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
    { std::lock_guard<std::mutex> g(mu); hist[((uint64_t)cls << 40) | ((uint64_t)(off >> 2) << 32) | pc]++; }
    if (rs64_vi_committed_width() >= 512u && rows[cls].fetch_add(1) < 60)
        std::fprintf(stderr, "[s4572-W] %s %c cls=%s buf=%u idx=%u off=%u pc=%08X addr=%08X val=%08X vi_w=%u\n", kind, w,
                     cls == 2 ? "cursor" : cls ? "chunk2+" : "inrange", buf, idx, off, pc, addr, value, rs64_vi_committed_width());
    if ((++all % 20000u) == 0 && (all / 20000u) <= 20) {
        std::lock_guard<std::mutex> g(mu);
        std::fprintf(stderr, "[s4572-tot] stores inrange=%u chunk2+=%u cursor=%u\n", tot[0].load(), tot[1].load(), tot[2].load());
        for (auto& kv : hist) std::fprintf(stderr, "[s4572-hist] cls=%u woff=%u pc=%08X n=%u\n", (unsigned)(kv.first >> 40), (unsigned)((kv.first >> 32) & 0xFFu), (unsigned)kv.first, kv.second);
    }
}
#include <mutex>
struct rs64_s4577_ent { uint32_t seq, pc, addr, val, vi_w; char w; };
static rs64_s4577_ent g_s4577_cb[64]; static unsigned g_s4577_ncb = 0;
static rs64_s4577_ent g_s4577_ring[128]; static unsigned g_s4577_n = 0; static std::mutex g_s4577_mu;
static void rs64_s4577_note(char w, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4577"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    const uint32_t p = addr & 0x1FFFFFFFu;
    if (p >= 0x1496F8u && p < 0x149704u) {
        std::lock_guard<std::mutex> g(g_s4577_mu);
        g_s4577_cb[g_s4577_ncb % 64] = {g_s4577_ncb, pc, addr, value, rs64_vi_committed_width(), w};
        g_s4577_ncb++;
        return;
    }
    if (p < 0x172438u || p >= 0x172548u) return;
    std::lock_guard<std::mutex> g(g_s4577_mu);
    g_s4577_ring[g_s4577_n % 128] = {g_s4577_n, pc, addr, value, rs64_vi_committed_width(), w};
    g_s4577_n++;
}
extern "C" void rs64_s4577_dump() {
    std::lock_guard<std::mutex> g(g_s4577_mu);
    std::fprintf(stderr, "[s4577-dump] total_stores=%u (ring keeps last 128)\n", g_s4577_n);
    for (unsigned i = g_s4577_ncb > 64 ? g_s4577_ncb - 64 : 0; i < g_s4577_ncb; i++) {
        const auto& e = g_s4577_cb[i % 64];
        std::fprintf(stderr, "[s4577-CB] seq=%u addr=%08X w=%c pc=%08X val=%08X vi_w=%u\n", e.seq, e.addr, e.w, e.pc, e.val, e.vi_w);
    }
    const unsigned n = g_s4577_n < 128 ? g_s4577_n : 128, start = g_s4577_n - n;
    for (unsigned i = start; i < g_s4577_n; i++) {
        const auto& e = g_s4577_ring[i % 128];
        std::fprintf(stderr, "[s4577-W] seq=%u rec=%u off=0x%02X w=%c pc=%08X val=%08X vi_w=%u\n", e.seq,
                     (unsigned)(((e.addr & 0x1FFFFFFFu) - 0x172438u) / 0x88u) + 29u, (unsigned)(((e.addr & 0x1FFFFFFFu) - 0x172438u) % 0x88u),
                     e.w, e.pc, e.val, e.vi_w);
    }
}
static void rs64_s4569_note(const char* kind, char w, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4569"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    const uint32_t p = addr & 0x1FFFFFFFu;
    const bool tgt = (p >= 0x179A58u && p < 0x179A70u) || (p >= 0x1120A8u && p < 0x1120C0u) || (p >= 0x17DBC0u && p < 0x17DBD8u);
    static std::atomic<unsigned> ctl{0}, rows{0};
    if (!tgt) { if (p >= 0x17C000u && p < 0x180000u && ctl.fetch_add(1) == 0) std::fprintf(stderr, "[s4569-control] first non-target store in 0x17C000..0x180000 %s %c pc=%08X addr=%08X val=%08X vi_w=%u\n", kind, w, pc, addr, value, rs64_vi_committed_width()); return; }
    if (rows.fetch_add(1) > 4000) return;
    std::fprintf(stderr, "[s4569-W] %s %c pc=%08X addr=%08X val=%08X vi_w=%u\n", kind, w, pc, addr, value, rs64_vi_committed_width());
}
extern "C" void rs64_s4597_target_store(char width, uint32_t pc, uint32_t addr, uint32_t value);
extern "C" void rs64_s4299_store_watch(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4299"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    rs64_s4569_note("st", width, pc, addr, value);
    rs64_s4577_note(width, pc, addr, value);
    rs64_s4572_note("st", width, pc, addr, value);
    rs64_s4597_target_store(width, pc, addr, value);
    (void)value;
    const uint32_t phys = addr & 0x1FFFFFFFu;
    // s4638: CPU-store watch on hangar colour buffer 0x656400 (512x16bpp):
    // edge = col 511 (byte offset 1022/1023 in a 1024-byte row), body = any other col.
    {
        static std::atomic<uint32_t> all{0}, body{0}, edge{0}, eprint{0};
        if (phys >= 0x656400u && phys < 0x656400u + 260u * 1024u) {
            const uint32_t off = phys - 0x656400u, col = (off & 1023u) >> 1;
            if (col == 511u) {
                edge.fetch_add(1);
                if (rs64_vi_committed_width() == 512u && (value & 0xFFu) && eprint.fetch_add(1) < 64)
                    std::fprintf(stderr, "[s4638-EDGE] %c pc=%08X addr=%08X val=%08X row=%u vi_w=%u\n",
                                 width, pc, addr, value, off >> 10, rs64_vi_committed_width());
            } else if (body.fetch_add(1) < 8) {
                std::fprintf(stderr, "[s4638-BODY-control] %c pc=%08X addr=%08X col=%u\n", width, pc, addr, col);
            }
        }
        if ((all.fetch_add(1) & 0xFFFFFu) == 0)
            std::fprintf(stderr, "[s4638-tally] stores=%u body=%u edge=%u\n", all.load(), body.load(), edge.load());
    }
    if (phys >= 0x17C000u && phys < 0x17D000u) {
        static std::atomic<bool> control{false};
        if (!control.exchange(true)) {
            std::fprintf(stderr, "[s4306-control] adjacent-range-positive-control=1 phys=0x%06X width=%c pc=0x%08X\n",
                         phys, width, pc);
            std::fflush(stderr);
        }
    }
    S4299Ent& e = g_s4299_ring[g_s4299_total & ((1u << 20) - 1)];
    e.pc = pc; e.addr = addr; e.seq = (uint32_t)g_s4299_total; e.w = width; e.fn = nullptr;
    g_s4299_total++;
}
extern "C" void rs64_s4306_postfree_store(uint8_t* rdram, uint32_t pc,
                                             uint32_t addr, uint32_t requested) {
    static const bool on = [] {
        const char* e = std::getenv("ROGUESQ_LOG_S4306");
        return e && e[0] && e[0] != '0';
    }();
    if (!on || !rdram) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 512u || origin != 0x006AB400u) return;
    const uint32_t phys = addr & 0x1FFFFFFFu;
    if (phys < 0x17D000u || phys >= 0x17E200u) return;
    static std::atomic<uint32_t> ordinal{0};
    static std::atomic<bool> control{false};
    const uint32_t post = (uint32_t(rdram[(phys + 0) ^ 3]) << 24) |
                          (uint32_t(rdram[(phys + 1) ^ 3]) << 16) |
                          (uint32_t(rdram[(phys + 2) ^ 3]) << 8) |
                          uint32_t(rdram[(phys + 3) ^ 3]);
    if (!control.exchange(true)) {
        std::fprintf(stderr, "[s4306-control] adjacent-range-positive-control=1 phase=%u width=%u origin=0x%06X\n",
                     rs64_phase_ord(), width, origin);
        std::fflush(stderr);
    }
    const uint32_t n = ordinal.fetch_add(1, std::memory_order_relaxed);
    rs64_s4307_note_writer(n, pc, phys, requested, post);
    if (n >= 16384u) return;
    std::fprintf(stderr,
        "[s4306-row] ordinal=%u phase=%u width=%u origin=0x%06X pc=0x%08X addr=0x%06X requested=0x%08X post=0x%08X mismatch=%u\n",
        n, rs64_phase_ord(), width, origin, pc, phys, requested, post,
        requested != post ? 1u : 0u);
    std::fflush(stderr);
}

extern "C" void rs64_s4307_note_writer(uint32_t ordinal, uint32_t pc,
                                         uint32_t addr, uint32_t requested,
                                         uint32_t post) {
    g_s4307_last_writer = { ordinal, pc, addr, requested, post };
}
static void rs64_s4575_load(uint32_t pc, uint32_t addr) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4575"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    const uint32_t p = addr & 0x1FFFFFFFu;
    static std::atomic<unsigned> tot[2]{}, all{0};
    static std::mutex mu; static std::map<uint64_t, unsigned> hist;
    int cls = -1; uint32_t off = 0;
    const uint32_t cap = g_s4572_cap, cnt = g_s4572_cnt;
    for (int b = 0; b < 2 && cls < 0; b++) {
        const uint32_t tb = (b ? g_s4572_t1 : g_s4572_t0) & 0x1FFFFFFFu;
        if (tb && p >= tb && p < tb + cap * 0x88u) { off = (p - tb) % 0x88u; cls = ((p - tb) / 0x88u) < cnt ? 0 : 1; }
    }
    if (cls < 0) return;
    tot[cls]++;
    { std::lock_guard<std::mutex> g(mu); hist[((uint64_t)cls << 40) | ((uint64_t)(off >> 2) << 32) | pc]++; }
    if ((++all % 20000u) == 0 && (all / 20000u) <= 20) {
        std::lock_guard<std::mutex> g(mu);
        std::fprintf(stderr, "[s4575-tot] loads inrange=%u chunk2+=%u\n", tot[0].load(), tot[1].load());
        for (auto& kv : hist) std::fprintf(stderr, "[s4575-hist] cls=%u woff=%u pc=%08X n=%u\n", (unsigned)(kv.first >> 40), (unsigned)((kv.first >> 32) & 0xFFu), (unsigned)kv.first, kv.second);
    }
}
extern "C" void rs64_s4457_list_check(uint8_t* rdram, uint32_t value);
// s7069: inline call-site gate read by the generated code (tools/apply_s7069_callsite_gate.py); see main.cpp g_rs64_lowfield_hook.
extern "C" { int g_rs64_synthread_hook = 1; }
extern "C" void rs64_s4307_synth_read(uint8_t* rdram, uint32_t pc,
                                        uint32_t addr, uint32_t value) {
    // s7068: one early-out for the synth-read hook (S4457 list check, S4575 load hist, S4307 rows; all default off).
    // ROGUESQ_DIAG_GATE=0 restores the per-gate checks.
    static const bool s7068_any = [] {
        auto on = [](const char* n) { const char* e = std::getenv(n); return e && e[0] && e[0] != '0'; };
        const char* g = std::getenv("ROGUESQ_DIAG_GATE");
        return (g && g[0] == '0') || on("ROGUESQ_LOG_S4457") || on("ROGUESQ_LOG_S4575") || on("ROGUESQ_LOG_S4307");
    }();
    if (!s7068_any) {
        const char* c = std::getenv("ROGUESQ_DIAG_CALLSITE");
        if (!(c && c[0] == '0')) g_rs64_synthread_hook = 0;
        return;
    }
    if (pc == 0x80091378u || pc == 0x8009133Cu) rs64_s4457_list_check(rdram, value);
    rs64_s4575_load(pc, addr);
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4307"); return e && e[0] && e[0] != '0'; }();
    if (!on || !rdram) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 512u || origin != 0x006AB400u) return;
    const uint32_t phys = addr & 0x1FFFFFFFu;
    static std::atomic<bool> any_control{false};
    if (!any_control.exchange(true)) {
        std::fprintf(stderr, "[s4307-control] phase-gated-read-positive-control=1 phase=%u width=%u origin=0x%06X pc=0x%08X addr=0x%06X\n",
                     rs64_phase_ord(), width, origin, pc, phys);
        std::fflush(stderr);
    }
    if (phys < 0x17D000u || phys >= 0x17E200u) return;
    static std::atomic<uint32_t> rows{0};
    const uint32_t n = rows.fetch_add(1, std::memory_order_relaxed);
    if (n >= 16384u) return;
    const S4307Writer w = g_s4307_last_writer;
    std::fprintf(stderr,
        "[s4307-row] ordinal=%u phase=%u width=%u origin=0x%06X read_pc=0x%08X addr=0x%06X value=0x%08X preceding_writer_ordinal=%u writer_pc=0x%08X writer_addr=0x%06X requested=0x%08X post=0x%08X\n",
        n, rs64_phase_ord(), width, origin, pc, phys, value, w.ordinal, w.pc,
        w.addr, w.requested, w.post);
    std::fflush(stderr);
}
extern "C" void rs64_s4299_swlr(char w, const char* fn, uint32_t line, uint32_t addr) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4299"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    g_s4299_swlr_total++;
    rs64_s4569_note(w == 'L' ? "swl" : "swr", w, line, addr, 0);
    rs64_s4572_note(w == 'L' ? "swl" : "swr", w, line, addr, 0);
    uint32_t p = addr & 0x1FFFFFFFu;
    if (p < 0x17C000u || p >= 0x180000u) return;
    S4299Ent& e = g_s4299_ring[g_s4299_total & ((1u << 20) - 1)];
    e.pc = line; e.addr = addr; e.seq = (uint32_t)g_s4299_total; e.w = w; e.fn = fn;
    g_s4299_total++;
}
extern "C" void rs64_s4597_target_store(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] {
        const char* e = std::getenv("ROGUESQ_LOG_S4597");
        return e && e[0] && e[0] != '0';
    }();
    if (!on) return;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t vi_width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t phys = addr & 0x1FFFFFFFu;
    if (addr == 0xFFFFFFFFu) {
        static std::atomic<bool> control[64]{};
        const uint32_t bucket = phase < 64u ? phase : 63u;
        if (!control[bucket].exchange(true, std::memory_order_relaxed)) {
            std::fprintf(stderr,
                "[s4597-phase-control] kind=entry phase=%u width=%u origin=0x%06X pc=0x%08X\n",
                phase, vi_width, origin, pc);
            std::fflush(stderr);
        }
        return;
    }
    if (phys >= 0x1724C0u && phys < 0x17250Cu) {
        static std::mutex mu;
        static std::set<uint64_t> seen;
        const uint64_t key = (static_cast<uint64_t>(phase) << 40) |
                             (static_cast<uint64_t>(pc) << 8) |
                             (phys - 0x1724C0u);
        bool first = false;
        {
            std::lock_guard<std::mutex> lock(mu);
            first = seen.size() < 256u && seen.insert(key).second;
        }
        if (first) {
            std::fprintf(stderr,
                "[s4601-span] phase=%u width=%u origin=0x%06X pc=0x%08X store_width=%c offset=0x%02X addr=0x%08X value=0x%08X\n",
                phase, vi_width, origin, pc, width, phys - 0x1724C0u, addr, value);
            std::fflush(stderr);
        }
        return;
    }
    if (phys >= 0x17C000u && phys < 0x17D000u) {
        static std::atomic<bool> control[64]{};
        const uint32_t bucket = phase < 64u ? phase : 63u;
        if (!control[bucket].exchange(true, std::memory_order_relaxed)) {
            std::fprintf(stderr,
                "[s4597-phase-control] kind=adjacent phase=%u width=%u origin=0x%06X pc=0x%08X addr=0x%08X\n",
                phase, vi_width, origin, pc, addr);
            std::fflush(stderr);
        }
    }
}
extern "C" void rs64_s4602_strncpy_caller(uint8_t* rdram, uint32_t caller,
                                             uint32_t a0, uint32_t a1,
                                             uint32_t a2) {
    static const bool on = [] {
        const char* e = std::getenv("ROGUESQ_LOG_S4602");
        return e && e[0] && e[0] != '0';
    }();
    if (!on || rs64_vi_committed_width() != 640u) return;
    static std::mutex mu;
    static std::set<uint64_t> seen;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t a0_phys = a0 & 0x1FFFFFFFu;
    const bool target = a0_phys >= 0x1724C0u && a0_phys < 0x17250Cu;
    const uint64_t key = (static_cast<uint64_t>(phase) << 32) | caller;
    std::lock_guard<std::mutex> lock(mu);
    if (!target && (seen.size() >= 128u || !seen.insert(key).second)) return;
    auto dump16 = [rdram](uint32_t guest, char* out) {
        if (!rdram || guest < 0x80000000u || guest > 0x807FFFF0u) {
            std::strcpy(out, "invalid");
            return;
        }
        for (uint32_t i = 0; i < 16u; ++i)
            std::snprintf(out + i * 2u, 3u, "%02X", rdram[(guest - 0x80000000u + i) ^ 3u]);
        out[32] = '\0';
    };
    char source[33];
    char destination[33];
    if (caller == 0x80022B44u) {
        dump16(a1, source);
        dump16(a0, destination);
    } else {
        std::strcpy(source, "-");
        std::strcpy(destination, "-");
    }
    std::fprintf(stderr,
        "[s4602-strncpy] phase=%u width=640 origin=0x%06X caller=0x%08X a0=%08X a1=%08X a2=%08X source16=%s dstpre16=%s\n",
        phase, rs64_vi_committed_origin() & 0x00FFFFFFu, caller, a0, a1, a2,
        source, destination);
    std::fflush(stderr);
}
extern "C" void rs64_s4299_dump(uint32_t lo, uint32_t hi) {
    unsigned long n = g_s4299_total < (1u << 20) ? g_s4299_total : (1u << 20);
    std::fprintf(stderr, "[s4299-D] dump [%08X,%08X) ring total=%lu held=%lu swlr_calls=%lu\n", lo, hi, g_s4299_total, n, g_s4299_swlr_total);
    int shown = 0;
    for (unsigned long i = 0; i < n && shown < 24; i++) {
        const S4299Ent& e = g_s4299_ring[(g_s4299_total - 1 - i) & ((1u << 20) - 1)];
        if (e.addr < hi && e.addr + (e.w == 'D' ? 8u : (e.w == 'W' || e.w == 'L' || e.w == 'R') ? 4u : e.w == 'H' ? 2u : 1u) > lo) {
            std::fprintf(stderr, "[s4299-D]  back=%lu seq=%u pc=%08X %c addr=%08X fn=%s\n", i, e.seq, e.pc, e.w, e.addr, e.fn ? e.fn : "-");
            shown++;
        }
    }
    std::fprintf(stderr, "[s4299-D] matches shown=%d\n", shown);
}

extern "C" void rs64_s4694b_status_store(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] {
        const char* a = std::getenv("ROGUESQ_LOG_ALL"); const char* e = std::getenv("ROGUESQ_LOG_S4694B");
        return (a && a[0] && a[0] != '0') || (e && e[0] && e[0] != '0'); }();
    if (!on) return;
    if (rs64_phase_ord() < 4u) return;
    static int rows = 0;
    static uint32_t keys[256]; static uint32_t cnt[256]; static int nk = 0;
    const uint32_t key = (pc & ~3u) ^ ((uint32_t)width << 28) ^ (uint32_t)width;
    int k = 0; while (k < nk && keys[k] != key) k++;
    if (k == nk) { if (nk >= 256) return; keys[nk] = key; cnt[nk] = 0; nk++; }
    cnt[k]++;
    if (cnt[k] > 8 && (cnt[k] % 1000) != 0) return;
    if (rows >= 800) return;
    rows++;
    std::fprintf(stderr, "[s4694b-status] phase=%u pc=%08X %c addr=%08X val=%08X n=%u\n", rs64_phase_ord(), pc, width, addr, value, cnt[k]);
    std::fflush(stderr);
}

extern "C" int rs64_s5037_copy_guard(uint8_t* rdram, uint32_t dst, uint32_t src, uint32_t len, uint32_t ra, int which) {
    static const bool off = [] { const char* e = std::getenv("ROGUESQ_COPY_GUARD"); return e && e[0] == '0'; }();
    static const bool force = [] { const char* e = std::getenv("ROGUESQ_COPY_GUARD_FORCE"); return e && e[0] && e[0] != '0'; }();
    if (off || !rdram || len == 0) return 0;
    auto span_ok = [len](uint32_t a) {
        uint32_t p = a & 0x1FFFFFFFu;
        bool seg = (a < (rs64_ram_top - 0x80000000u)) || (a >= 0x80000000u && a < rs64_ram_top) || (a >= 0xA0000000u && a < (rs64_ram_top + 0x20000000u));
        return seg && (uint64_t)p + len <= (rs64_ram_top - 0x80000000u);
    };
    bool bad = len > (rs64_ram_top - 0x80000000u) || !span_ok(dst) || !span_ok(src);
    static int shown = 0; static unsigned long viol = 0;
    if (force) bad = true;
    if (!bad) return 0;
    ++viol;
    if (shown < 16) { ++shown;
        std::fprintf(stderr, "[s5037-copy-guard] %s ra=%08X dst=%08X src=%08X len=%u viol=%lu%s\n",
                     which ? "bcopy" : "memcpy", ra, dst, src, len, viol, force ? " (FORCE control, not skipped)" : " SKIPPED");
    }
    return force ? 0 : 1;
}

#include <unordered_set>
static std::unordered_set<uint32_t> s_s5041_freed;
static bool s5041_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_FREE_CENSUS"); return e && e[0] && e[0] != '0'; }(); return on; }
extern "C" void rs64_s5041_free(uint32_t ptr, uint32_t ra) {
    static const bool force = [] { const char* e = std::getenv("ROGUESQ_FREE_CENSUS_FORCE"); return e && e[0] && e[0] != '0'; }();
    if (!s5041_on() || ptr == 0) return;
    static unsigned long nfree = 0, ndouble = 0; static int shown = 0;
    ++nfree;
    bool dbl = !s_s5041_freed.insert(ptr).second;
    if (force) dbl = true;
    if (dbl) { ++ndouble; if (shown < 16) { ++shown;
        std::fprintf(stderr, "[s5041-free-census] DOUBLE ptr=%08X ra=%08X nfree=%lu ndouble=%lu%s\n", ptr, ra, nfree, ndouble, force ? " (FORCE control)" : ""); } }
    if ((nfree & (nfree - 1)) == 0) std::fprintf(stderr, "[s5041-free-census] total nfree=%lu ndouble=%lu live_freed=%zu\n", nfree, ndouble, s_s5041_freed.size());
}
#include <map>
#include <vector>
static std::map<uint32_t, uint32_t> s_s6063_live; static uint64_t s_s6063_bytes = 0, s_s6063_peak = 0;
static bool s6063_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_HEAPLOG"); return e && e[0] && e[0] != '0'; }(); return on; }
static void s6127_walk(uint32_t req, bool ok = false);
static void s6129_dump(const char* why, uint32_t from);
static uint8_t* g_s6127_rd = nullptr;
static inline uint32_t s5042_rd(const uint8_t* rd, uint32_t off);
static uint32_t g_s6127_flags;
extern "C" void rs64_s6127_fl(uint32_t f) { g_s6127_flags = f; }
extern "C" void rs64_floor_ownership(const char*, uint32_t, uint32_t, uint32_t);
/* s7317: ROGUESQ_S7317_ALLOCMAP=1 keeps every live guest allocation (heap AND spill) as ptr -> (req, malloc ra), written beside
   each ROGUESQ_RDRAM_DUMP_DIR dump as alloc_<swap>.txt, so a word holding a spill pointer can be mapped to its owner block and allocator.
   Guest ra is 0 here (recompiled jal does not write r31), so the caller is the host return address chain (frames 0..2), resolved
   with dladdr at write time. '#' header: spill blocks recorded / freed so far (positive control that spill blocks reach the map). */
struct S7317B { uint32_t req; void* pc[3]; double t; uint32_t fl; };
static std::mutex s_s7317_mu; static std::map<uint32_t, S7317B> s_s7317_live; static uint64_t s_s7317_sprec = 0, s_s7317_spfree = 0;
static char s7332_carve_tag;  /* s7332: pc[0] marker of host-map entries registered from the guest carve walk (not an rs_malloc) */
static std::map<uint32_t, uint32_t> s_s7332_carve;  /* s7332: carve start -> req; fallback when a nested temp-pool block shadows it */
/* s7333 item 24(a): every erase / replace of a host-map entry at a key the carve walk ever registered is logged with its path
   (free / malloc / rebuild / sync / fallback) and the guest header at key-0x10 at that moment ([s7333] lines, first 300).
   ROGUESQ_S7333_KEEP (default 1; =0 old): the s7318_blk carve fallback trusts the guest header (fl&6 == 6, size covers x) instead of
   the host entry, so a host erase between heapsyncs no longer turns a still-allocated guest carve into "not live". */
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;
static std::map<uint32_t, uint64_t> s_s7333_keys;  /* carve key -> event count; guarded by s_s7317_mu */
static uint64_t s_s7333_nev = 0, s_s7333_kept = 0, s_s7333_dropped = 0;
static uint64_t s_s7332_ncarve = 0;
static bool s7333_keep_on() { static const int v = [] { const char* e = std::getenv("ROGUESQ_S7333_KEEP"); return (e && *e == '0') ? 0 : 1; }(); return v != 0; }
static bool s7333_hdr(uint32_t key, uint32_t* fl, uint32_t* sz) {
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; *fl = *sz = 0; if (!r || key < 0x80000010u || key >= 0x81000000u) return false;
    const uint32_t h = key - 0x10u; *fl = (*(volatile uint32_t*)(r + (h & 0x00FFFFFCu))) >> 16; *sz = *(volatile uint32_t*)(r + ((h + 4u) & 0x00FFFFFCu));
    return (*fl & 6u) == 6u && !(*fl & 8u) && *sz && *sz <= 0x1000000u; }
/* caller holds s_s7317_mu */
static void s7333_ev(const char* path, uint32_t key, uint32_t oldreq, bool oldcarve, uint32_t newreq) {
    auto k = s_s7333_keys.find(key); if (k == s_s7333_keys.end()) return; ++k->second; ++s_s7333_nev;
    uint32_t fl, sz; const bool g = s7333_hdr(key, &fl, &sz);
    void* pc[4] = {nullptr, nullptr, nullptr, nullptr}; void** fp = (void**)__builtin_frame_address(0);
    for (int i = 0; i < 4 && fp && fp[0]; ++i) { fp = (void**)fp[0]; pc[i] = fp[1]; }
    if (s_s7333_nev <= 300) { std::fprintf(stderr, "[s7333] carve-key %s key=%08X old=%c+%X new=%X guest fl=%X sz=%X carve_ok=%d n=%llu stack:", path, key,
                                         oldcarve ? 'C' : 'M', oldreq, newreq, fl, sz, (int)g, (unsigned long long)k->second);
        for (void* q : pc) { Dl_info di; if (q && dladdr(q, &di) && di.dli_sname) std::fprintf(stderr, " %s+0x%lx", di.dli_sname, (unsigned long)((char*)q - (char*)di.dli_saddr)); else std::fprintf(stderr, " ?"); }
        std::fprintf(stderr, "\n"); } }
static bool s7317_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7317_ALLOCMAP"); return e && e[0] && e[0] != '0'; }(); return on; }
static inline bool s7317_isspill(uint32_t p) { return p >= 0x81000000u && p < 0x81800000u; }  /* s7326: 8 MB arena */
/* s7325 audio heap-gap reads (needs ROGUESQ_S7324_RCPREF + ALLOCMAP): history of the last 65536 non-spill frees (ptr, req, free
   time, host freer frames, allocator frames) so an RCP read in no live block can be classed freed / header gap / untracked. */
extern "C" int rs64_s7331_on; extern "C" void rs64_s7331_track(uint64_t sync, char kind, uint32_t ptr, uint32_t req, void* own);
extern "C" void rs64_s7331_malloc(uint32_t ptr, uint32_t req, void* own);
extern "C" void rs64_s7331_task(const uint32_t* f);
extern "C" int rs64_s7324_on;
struct S7325F { uint32_t ptr, req; uint64_t seq; double t; void* fpc[4]; void* apc[3]; };
static std::multimap<uint32_t, S7325F> s_s7325_freed;
static std::deque<std::multimap<uint32_t, S7325F>::iterator> s_s7325_ord;
static uint64_t s_s7325_seq = 0; static uint32_t s_s7325_lastfree = 0, s_s7325_lastmalloc = 0, s_s7325_hmin = 0xFFFFFFFFu, s_s7325_hmax = 0;
static double s7325_now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
/* s7326: spill blocks alive at a retail scene reset that retail would have released there: kind 'C' = a1 tag lacks 0x80 and not
   flags&4, alive after coalesceFreeHeapBlocks (persistent-heap bulk free); 'T' = flags&4 (temp pool) alive at the temp-arena rebuild
   (buildHeapFreeList on head 0x8010FEFC). A survivor later rs_free'd is a "late free" (H-freed-later); one never freed is a leak
   relative to retail (H-leak). ROGUESQ_S7326_CTL=1: a synthetic a1=0 spill block is allocated before each coalesce scan (must be
   listed as a survivor) and freed right after (must register as a late free). Needs ROGUESQ_S7317_ALLOCMAP=1. */
struct S7326S { uint64_t reset; double t; uint32_t fl, req; void* pc; char kind; bool ctl; };
static std::map<uint32_t, S7326S> s_s7326_surv;  /* guarded by s_s7317_mu */
static uint64_t s_s7326_nsurv = 0, s_s7326_nlate = 0, s_s7326_ctl_seen = 0, s_s7326_ctl_late = 0, s_s7326_ctl_n = 0, s_s7326_resets = 0;
static uint64_t s_s7326_late_bytes = 0; static double s_s7326_late_dtmax = 0;
static bool s7326_ctl_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7326_CTL"); return e && e[0] && e[0] != '0'; }(); return on; }
static void s7317_free(uint32_t ptr) {
    if (!s7317_on() || !ptr) return;
    void* fpc[4] = {nullptr, nullptr, nullptr, nullptr};
    if (rs64_s7324_on) { fpc[0] = __builtin_return_address(0); void** fp = (void**)__builtin_frame_address(0);
        for (int k = 1; k < 4 && fp && fp[0]; ++k) { fp = (void**)fp[0]; fpc[k] = fp[1]; } }
    std::lock_guard<std::mutex> lk(s_s7317_mu);
    auto it = s_s7317_live.find(ptr); if (it == s_s7317_live.end()) return;
    if (rs64_s7324_on && !s7317_isspill(ptr)) {
        S7325F f{ptr, it->second.req, ++s_s7325_seq, s7325_now(), {fpc[0], fpc[1], fpc[2], fpc[3]}, {it->second.pc[0], it->second.pc[1], it->second.pc[2]}};
        s_s7325_ord.push_back(s_s7325_freed.emplace(ptr, f));
        if (s_s7325_ord.size() > 65536u) { s_s7325_freed.erase(s_s7325_ord.front()); s_s7325_ord.pop_front(); }
        s_s7325_lastfree = ptr; }
    if (s7317_isspill(ptr)) { ++s_s7317_spfree;
        auto sv = s_s7326_surv.find(ptr);
        if (sv != s_s7326_surv.end()) { const double dt = s7325_now() - sv->second.t;
            if (sv->second.ctl) ++s_s7326_ctl_late;
            else { ++s_s7326_nlate; s_s7326_late_bytes += sv->second.req; if (dt > s_s7326_late_dtmax) s_s7326_late_dtmax = dt;
                static int nl = 0; if (nl++ < 60) { Dl_info di; void* pc = sv->second.pc;
                    std::fprintf(stderr, "[s7326] late free %08X req=0x%X fl=%X kind=%c reset#%llu now#%llu dt=%.3f s owner=%s\n", ptr, sv->second.req, sv->second.fl,
                                 sv->second.kind, (unsigned long long)sv->second.reset, (unsigned long long)s_s7326_resets, dt,
                                 (pc && dladdr(pc, &di) && di.dli_sname) ? di.dli_sname : "?"); } }
            s_s7326_surv.erase(sv); } }
    s7333_ev("free", ptr, it->second.req, it->second.pc[0] == (void*)&s7332_carve_tag, 0);
    s_s7317_live.erase(it); }
static void s7317_sym(FILE* f, void* pc) {
    Dl_info di; if (pc && dladdr(pc, &di) && di.dli_sname) fprintf(f, " %s+0x%lx", di.dli_sname, (unsigned long)((char*)pc - (char*)di.dli_saddr)); else fprintf(f, " ?%p", pc);
}
void rs64_s7317_write(const char* path) {
    if (!s7317_on()) return;
    std::lock_guard<std::mutex> lk(s_s7317_mu);
    if (FILE* f = fopen(path, "w")) {
        uint64_t nsp = 0; for (auto& kv : s_s7317_live) nsp += s7317_isspill(kv.first);
        fprintf(f, "# spill_recorded=%llu spill_freed=%llu spill_live=%llu blocks=%zu\n", (unsigned long long)s_s7317_sprec, (unsigned long long)s_s7317_spfree, (unsigned long long)nsp, s_s7317_live.size());
        for (auto& kv : s_s7317_live) { fprintf(f, "%08X %X", kv.first, kv.second.req); for (void* pc : kv.second.pc) s7317_sym(f, pc); fprintf(f, "\n"); }
        fclose(f);
    }
}
/* s7318: ROGUESQ_S7318_BCMP=1|<path> (needs ROGUESQ_S7317_ALLOCMAP=1): classifier behind the 182 class-B field-order compares
   (tools/apply_s7318_bcmp_probe.py, sites tools/s7318_bcmp_sites.txt). Per site, every executed compare (a, b) is classed:
   nn = no spill operand (hh = both 0x80xxxxxx); same = both spill, same live block; spsp = both spill, different/unmapped blocks;
   cross = one spill, other in 0x80000000-0x80FFFFFF (the only case whose outcome can differ from a retail all-heap layout);
   speq = one spill, other < 0x80000000 or >= 0x81400000 (outcome identical for any heap or spill pointer). unm = spill operand in
   no live block. First 4 cross examples per site kept with the spill block's req and allocator. Positive control
   ROGUESQ_S7318_BCMP_CTL=<pc hex>: at that site, when neither operand is spill and b is 0x80xxxxxx, the classifier is re-run with
   a := the lowest live spill block start into the separate ctl counters (must class cross). Table rewritten every >=10 s. */
extern "C" { int rs64_s7318_on = 0; }
namespace {
struct S7318S { uint32_t pc; uint64_t n, nn, hh, same, spsp, cross, speq, unm, ctl_n, ctl_cross; uint32_t ex[4][4]; int nex; };
S7318S g_s7318[768];  /* 0-255 class B (s7318), 256-511 class C (s7320), 512-767 class D (s7321) */ const char* g_s7318_path = nullptr; uint32_t g_s7318_ctl = 0; uint64_t g_s7318_calls = 0, g_s7318_last = 0;
struct S7318Init { S7318Init() {
    const char* e = std::getenv("ROGUESQ_S7318_BCMP"); if (!e || !e[0] || e[0] == '0') return;
    g_s7318_path = (e[0] == '1' && !e[1]) ? "rs64_s7318_bcmp.txt" : e;
    const char* c = std::getenv("ROGUESQ_S7318_BCMP_CTL"); if (c && *c) g_s7318_ctl = (uint32_t)strtoul(c, nullptr, 16);
    rs64_s7318_on = 1; std::fprintf(stderr, "[s7318] bcmp probe on -> %s ctl=%08X allocmap=%d\n", g_s7318_path, g_s7318_ctl, (int)s7317_on()); } } g_s7318_init;
inline bool s7318_sp(uint32_t x) { return x >= 0x81000000u && x < 0x81800000u; }  /* s7326: 8 MB arena */
/* block containing x, or 0 (caller holds s_s7317_mu) */
void s7333_boot_register();
uint32_t s7318_blk(uint32_t x, uint32_t* req) {
    auto it = s_s7317_live.upper_bound(x);
    if (it != s_s7317_live.begin()) { --it;
        if (x - it->first < (it->second.req ? it->second.req : 1)) { if (req) *req = it->second.req; return it->first; } }
    if (s7333_keep_on() && s_s7332_ncarve == 0) s7333_boot_register();  /* s7333: boot FIFO precedes heapsync #1 */
    auto c = s_s7332_carve.upper_bound(x);
    /* s7333: walk DOWN the carve keys: carves from different scenes overlap, so a stale nearer key must not shadow the enclosing one.
       A live host entry at the key (an rs_malloc that re-took the carve start with req < guest size) keeps the carve. */
    for (int n = 0; n < 64 && c != s_s7332_carve.begin(); ++n) { --c;
        if (s_s7317_live.find(c->first) == s_s7317_live.end()) {
            uint32_t fl, sz;
            if (s7333_keep_on() && s7333_hdr(c->first, &fl, &sz)) { if (x - c->first < sz) { ++s_s7333_kept; if (req) *req = sz; return c->first; } continue; }
            if (!s7333_keep_on() && x - c->first >= c->second) return 0;
            ++s_s7333_dropped; s7333_ev("fallback-drop", c->first, c->second, true, 0); c = s_s7332_carve.erase(c);
            if (!s7333_keep_on()) return 0; continue; }
        if (x - c->first < c->second) { if (req) *req = c->second; return c->first; }
        if (!s7333_keep_on()) return 0; }
    return 0; }
/* 0 nn 1 same 2 spsp 3 cross 4 speq; *unm set when a spill operand is unmapped */
int s7318_class(uint32_t a, uint32_t b, int* unm, uint32_t* blk, uint32_t* req) {
    bool sa = s7318_sp(a), sb = s7318_sp(b); *unm = 0; *blk = 0; *req = 0;
    if (!sa && !sb) return 0;
    std::lock_guard<std::mutex> lk(s_s7317_mu);
    uint32_t ra = 0, rb = 0, ba = sa ? s7318_blk(a, &ra) : 0, bb = sb ? s7318_blk(b, &rb) : 0;
    if ((sa && !ba) || (sb && !bb)) *unm = 1;
    *blk = sa ? ba : bb; *req = sa ? ra : rb;
    if (sa && sb) return (ba && ba == bb) ? 1 : 2;
    uint32_t o = sa ? b : a;
    return (o >= 0x80000000u && o < 0x81000000u) ? 3 : 4; }
void s7318_dump() {
    FILE* f = std::fopen(g_s7318_path, "w"); if (!f) return;
    uint64_t T[9] = {0}; for (auto& s : g_s7318) { T[0] += s.n; T[1] += s.nn; T[2] += s.hh; T[3] += s.same; T[4] += s.spsp; T[5] += s.cross; T[6] += s.speq; T[7] += s.unm; T[8] += s.ctl_cross; }
    std::fprintf(f, "# s7318 calls=%llu nn=%llu hh=%llu same=%llu spsp=%llu cross=%llu speq=%llu unm=%llu ctl_cross=%llu\n# idx pc n nn hh same spsp cross speq unm ctl_n ctl_cross | ex a b blk req\n",
        (unsigned long long)T[0], (unsigned long long)T[1], (unsigned long long)T[2], (unsigned long long)T[3], (unsigned long long)T[4], (unsigned long long)T[5], (unsigned long long)T[6], (unsigned long long)T[7], (unsigned long long)T[8]);
    for (int i = 0; i < 768; ++i) { auto& s = g_s7318[i]; if (!s.n) continue;
        std::fprintf(f, "%d %08X %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu |", i, s.pc, (unsigned long long)s.n, (unsigned long long)s.nn, (unsigned long long)s.hh, (unsigned long long)s.same,
            (unsigned long long)s.spsp, (unsigned long long)s.cross, (unsigned long long)s.speq, (unsigned long long)s.unm, (unsigned long long)s.ctl_n, (unsigned long long)s.ctl_cross);
        for (int k = 0; k < s.nex; ++k) std::fprintf(f, " %08X,%08X,%08X,%X", s.ex[k][0], s.ex[k][1], s.ex[k][2], s.ex[k][3]);
        std::fprintf(f, "\n"); }
    std::fclose(f); }
}
extern "C" void rs64_s7318_bcmp(int idx, uint32_t pc, uint32_t a, uint32_t b) {
    if ((unsigned)idx >= 768) return;
    S7318S& s = g_s7318[idx]; s.pc = pc; ++s.n;
    int unm; uint32_t blk, req; int c = s7318_class(a, b, &unm, &blk, &req);
    if (c == 0) { ++s.nn; if ((a >> 24) == 0x80 && (b >> 24) == 0x80) ++s.hh; }
    else if (c == 1) ++s.same; else if (c == 2) ++s.spsp; else if (c == 4) ++s.speq;
    else { ++s.cross; if (s.nex < 4) { uint32_t* e = s.ex[s.nex++]; e[0] = a; e[1] = b; e[2] = blk; e[3] = req; } }
    s.unm += unm;
    if (g_s7318_ctl == pc && c == 0 && (b >> 24) == 0x80) {
        uint32_t lo = 0; { std::lock_guard<std::mutex> lk(s_s7317_mu); auto it = s_s7317_live.lower_bound(0x81000000u); if (it != s_s7317_live.end() && s7318_sp(it->first)) lo = it->first; }
        if (lo) { ++s.ctl_n; int u2; uint32_t b2, r2; if (s7318_class(lo, b, &u2, &b2, &r2) == 3 && !u2) ++s.ctl_cross; } }
    if ((++g_s7318_calls & 0xFFFF) == 0) { uint64_t now = mach_absolute_time(); static mach_timebase_info_data_t tb; if (!tb.denom) mach_timebase_info(&tb);
        if ((now - g_s7318_last) * tb.numer / tb.denom >= 10000000000ull) { g_s7318_last = now; s7318_dump(); } }
}
/* s7324 class G: is any RCP-read address (RSP DMA dram, RDP SETTIMG/SETZIMG/SETCIMG) a spill block, direct or 24-bit aliased?
   addr is the raw value the RCP was handed. Returns 0 none (static/untracked), 1 heap block, 2 alias-only (addr < 4 MB, its
   0x81000000|addr lies in a live spill block and 0x80000000|addr in no live heap block), 3 alias+heap (both), 4 direct live spill
   (bits 24+ set, KSEG0 form in a live spill block), 5 direct other (bits 24+ set, no live spill block). blk/req/pc of the spill
   (classes 2-4) or heap (1) block. rs64_s7324_lowspill: lowest live spill block start or 0 (positive control source). */
extern "C" int rs64_s7324_class(uint32_t addr, uint32_t* blk, uint32_t* req, void** pc) {
    const uint32_t q = addr & 0x1FFFFFFFu; *blk = 0; *req = 0; pc[0] = pc[1] = pc[2] = nullptr;
    std::lock_guard<std::mutex> lk(s_s7317_mu);
    auto fill = [&](uint32_t b) { auto it = s_s7317_live.find(b); if (it != s_s7317_live.end()) { *blk = b; *req = it->second.req; for (int k = 0; k < 3; ++k) pc[k] = it->second.pc[k]; } };
    if (q >= 0x01000000u) { uint32_t r; uint32_t b = s7318_blk(0x80000000u | q, &r); if (b && s7318_sp(b)) { fill(b); return 4; } return 5; }
    uint32_t rh = 0, rs = 0; const uint32_t bh = s7318_blk(0x80000000u | q, &rh);
    const uint32_t bs = q < 0x00400000u ? s7318_blk(0x81000000u | q, &rs) : 0u;
    const bool sp = bs && s7318_sp(bs);
    if (sp) { fill(bs); return bh ? 3 : 2; }
    if (bh) { fill(bh); return 1; }
    return 0; }
/* nearest live non-spill blocks around KSEG0 x: *lo = start of last block starting <= x (its end in *loend), *hi = first block start > x */
extern "C" void rs64_s7324_near(uint32_t x, uint32_t* lo, uint32_t* loend, uint32_t* hi) {
    std::lock_guard<std::mutex> lk(s_s7317_mu); *lo = *loend = *hi = 0;
    auto it = s_s7317_live.upper_bound(x);
    if (it != s_s7317_live.end() && it->first < 0x81000000u) *hi = it->first;
    if (it != s_s7317_live.begin()) { --it; *lo = it->first; *loend = it->first + it->second.req; } }
extern "C" uint32_t rs64_s7324_lowspill() {
    std::lock_guard<std::mutex> lk(s_s7317_mu); auto it = s_s7317_live.lower_bound(0x81000000u);
    return (it != s_s7317_live.end() && s7318_sp(it->first)) ? it->first : 0u; }
extern "C" void rs64_s7324_sym(void* pc, char* out, size_t n) {
    Dl_info di; if (pc && dladdr(pc, &di) && di.dli_sname) snprintf(out, n, "%s+0x%lx", di.dli_sname, (unsigned long)((char*)pc - (char*)di.dli_saddr)); else snprintf(out, n, "?%p", pc); }
/* s7472 class EB: guest-heap chain integrity. ROGUESQ_S7472_HEAPCHK=1 (default off) walks every rs_malloc arena (heads
   0x8010FEFC / FF00 / FF18, deduped; header u16 flags (1 free, 2 used, 8 terminator) u16 tag, u32 size, 16 B; next =
   h + 0x10 + size, linear first-fit chain, rs_malloc 0x80001ACC) from the guest thread at rs_malloc exit / rs_free entry, at most
   every ROGUESQ_S7472_HEAPCHK_MS (default 250) ms. Checks: flags in {1,2,6} (or 8 = end), size 16-aligned, next > h and below
   rs64_ram_top, terminator reached. Logs the first bad header per (arena, blk, w0, size) `[s7472] heap-bad ...`, a per-check
   summary every 40 checks, and a flag histogram at the first check (layout self-test). Planted control
   ROGUESQ_S7472_HEAPCHK_PLANT=<s> (default 60 when set to 1): <s> seconds after the first check, set the flags of the largest
   free block of the first arena to 0x0010 (unused bit; 0x0006 = used + top-down bit 4, rs_malloc a1&4, is legitimate, s7472 run 1); the next check MUST log heap-bad field=flags, then the word is restored. */
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;
extern "C" uint32_t rs64_ram_top;
namespace {
static inline uint32_t s7472_rd(volatile uint8_t* r, uint32_t va) { return *(volatile uint32_t*)(r + ((va - 0x80000000u) & ~3u)); }
static inline void s7472_wr(volatile uint8_t* r, uint32_t va, uint32_t v) { *(volatile uint32_t*)(r + ((va - 0x80000000u) & ~3u)) = v; }
struct S7472Bad { uint32_t arena, blk, w0, sz; bool operator<(const S7472Bad& o) const { return std::tie(arena, blk, w0, sz) < std::tie(o.arena, o.blk, o.w0, o.sz); } };
static std::set<S7472Bad> s_s7472_seen;
static uint64_t s_s7472_n = 0, s_s7472_nbad = 0; static double s_s7472_t0 = 0, s_s7472_last = 0;
static int s_s7472_plant = 0; /* 0 idle, 1 planted (await report), 2 reported+restored */
static uint32_t s_s7472_pa = 0, s_s7472_pw0 = 0; static double s_s7472_ptime = 0;
}
static void s7472_check(const char* why, uint32_t ra) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7472_HEAPCHK"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    static const double ms = [] { const char* e = std::getenv("ROGUESQ_S7472_HEAPCHK_MS"); return e ? std::atof(e) : 250.0; }();
    static const double plant_s = [] { const char* e = std::getenv("ROGUESQ_S7472_HEAPCHK_PLANT"); if (!e || !*e || *e == '0') return -1.0; double v = std::atof(e); return v <= 1.0 ? 60.0 : v; }();
    const double now = s7325_now();
    if (s_s7472_last != 0 && (now - s_s7472_last) * 1000.0 < ms && s_s7472_plant != 1) return;
    s_s7472_last = now; if (s_s7472_t0 == 0) s_s7472_t0 = now; ++s_s7472_n;
    static const uint32_t heads[3] = {0x8010FEFCu, 0x8010FF00u, 0x8010FF18u};
    uint32_t seen[3] = {0, 0, 0}; int narena = 0; uint64_t nblk = 0, nfree = 0, nused = 0; int badthis = 0; bool plant_hit = false;
    uint32_t fhist[8] = {0}; uint32_t big_a = 0, big_sz = 0; const uint32_t top = rs64_ram_top;
    for (int i = 0; i < 3; ++i) {
        const uint32_t h0 = s7472_rd(r, heads[i]);
        if (h0 < 0x80000000u || h0 >= top) continue;
        bool dup = false; for (int j = 0; j < narena; ++j) if (seen[j] == h0) dup = true;
        if (dup) continue; seen[narena++] = h0;
        uint32_t a = h0, prev = 0; bool ended = false; int g = 0;
        for (; g < 400000; ++g) {
            const uint32_t w0 = s7472_rd(r, a), sz = s7472_rd(r, a + 4u), fl = w0 >> 16;
            fhist[fl == 1 ? 0 : fl == 2 ? 1 : fl == 8 ? 2 : fl == 6 ? 3 : 4]++;
            if (fl & 8u) { ended = true; break; }
            const char* field = nullptr; uint32_t val = 0;
            const uint32_t nx = a + 0x10u + sz;
            if (fl != 1u && fl != 2u && fl != 6u) { field = "flags"; val = w0; }
            else if (sz & 0xFu) { field = "size-align"; val = sz; }
            else if (nx <= a || nx >= top) { field = "next-range"; val = nx; }
            if (field) {
                ++badthis; if (s_s7472_plant == 1 && a == s_s7472_pa && !std::strcmp(field, "flags")) plant_hit = true;
                if (s_s7472_seen.insert({h0, a, w0, sz}).second && s_s7472_seen.size() <= 64)
                    std::fprintf(stderr, "[s7472] heap-bad why=%s arena=%08X blk=%08X field=%s val=%08X w0=%08X size=%08X prev_ok=%08X idx=%d t=%.1f ra=%08X gpc=%08X%s\n",
                                 why, h0, a, field, val, w0, sz, prev, g, now - s_s7472_t0, ra, (uint32_t)g_rs64_last_guest_pc,
                                 (s_s7472_plant == 1 && a == s_s7472_pa) ? " PLANT" : "");
                break;
            }
            ++nblk; if (fl == 1u) { ++nfree; if (i == 0 || narena == 1) { if (sz > big_sz) { big_sz = sz; big_a = a; } } } else ++nused;
            prev = a; a = nx;
        }
        if (!ended && badthis == 0) {
            ++badthis;
            if (s_s7472_seen.insert({h0, a, 0xFFFFFFFFu, (uint32_t)g}).second && s_s7472_seen.size() <= 64)
                std::fprintf(stderr, "[s7472] heap-bad why=%s arena=%08X blk=%08X field=no-terminator val=%d prev_ok=%08X t=%.1f\n", why, h0, a, g, prev, now - s_s7472_t0);
        }
    }
    if (badthis) s_s7472_nbad += badthis;
    if (s_s7472_n == 1) std::fprintf(stderr, "[s7472] heapchk armed ms=%.0f plant_s=%.0f top=%08X arenas=%d blocks=%llu fl1=%u fl2=%u fl8=%u fl6=%u other=%u\n",
                                     ms, plant_s, top, narena, (unsigned long long)nblk, fhist[0], fhist[1], fhist[2], fhist[3], fhist[4]);
    if (s_s7472_plant == 1) {
        if (plant_hit) { s7472_wr(r, s_s7472_pa, s_s7472_pw0); s_s7472_plant = 2; std::fprintf(stderr, "[s7472] plant DETECTED blk=%08X after %.3f s; restored w0=%08X\n", s_s7472_pa, now - s_s7472_ptime, s_s7472_pw0); }
        else if (s7472_rd(r, s_s7472_pa) != ((s_s7472_pw0 & 0xFFFFu) | 0x00100000u)) { s_s7472_plant = 2; std::fprintf(stderr, "[s7472] plant LOST blk=%08X (guest rewrote it before a check) w0 now %08X\n", s_s7472_pa, s7472_rd(r, s_s7472_pa)); }
    } else if (s_s7472_plant == 0 && plant_s >= 0 && now - s_s7472_t0 >= plant_s && big_a && badthis == 0) {
        s_s7472_pa = big_a; s_s7472_pw0 = s7472_rd(r, big_a); s7472_wr(r, big_a, (s_s7472_pw0 & 0xFFFFu) | 0x00100000u); s_s7472_plant = 1; s_s7472_ptime = now;
        std::fprintf(stderr, "[s7472] plant SET blk=%08X size=%08X w0 %08X -> %08X t=%.1f\n", big_a, big_sz, s_s7472_pw0, s7472_rd(r, big_a), now - s_s7472_t0);
    }
    if (s_s7472_n % 40 == 1 || badthis) {
        static int nsum = 0; if (nsum++ < 400)
            std::fprintf(stderr, "[s7472] chk n=%llu t=%.1f arenas=%d blocks=%llu free=%llu used=%llu bad_this=%d bad_total=%llu distinct=%zu\n",
                         (unsigned long long)s_s7472_n, now - s_s7472_t0, narena, (unsigned long long)nblk, (unsigned long long)nfree,
                         (unsigned long long)nused, badthis, (unsigned long long)s_s7472_nbad, s_s7472_seen.size());
    }
}
/* s7475 class ED: in-block tail overrun canary. ROGUESQ_S7475_CANARY=1 (default off): at rs_malloc exit, for a block
   below rs64_ram_top whose header (ptr-0x10: u16 flags 2|6, u32 size) passes the layout test, fill the slack bytes
   [ptr+req, ptr+size) with 0xA5 and record (blk, req, size, ra). The slack is checked at rs_free entry and on a walk of
   every live record at most every ROGUESQ_S7475_CANARY_MS (default 250) ms. A changed slack byte logs
   `[s7475] tail-hit why= blk= req= size= off= val= alloc_ra= free_ra= gpc= t=` (40 distinct rows max). A record whose header
   no longer matches (block re-carved by an arena reset that bypasses rs_free) is dropped as stale, not scored. A malloc
   drops every record overlapping the new block. Planted control ROGUESQ_S7475_CANARY_PLANT=<s> (1 -> 60): <s> s after the
   first record, write 0x5A at ptr+req of the live slack block with the largest req; the next walk MUST log it with PLANT. */
namespace {
struct S7475R { uint32_t req, sz, ra; double t; void* hpc; void* bt[8]; int nbt; };
static std::map<uint32_t, S7475R> s_s7475_live;
static std::mutex s_s7475_mu;
static uint64_t s_s7479_padded = 0;  /* s7479 class EG pad count (rs64_s7479_pad) */
static std::set<std::pair<uint32_t, uint32_t>> s_s7475_seen;
static uint64_t s_s7475_rec = 0, s_s7475_noslack = 0, s_s7475_hdrbad = 0, s_s7475_stale = 0, s_s7475_hits = 0, s_s7475_walks = 0,
                s_s7475_freechk = 0, s_s7475_overlap = 0;
static double s_s7475_t0 = 0, s_s7475_last = 0, s_s7475_ptime = 0;
static int s_s7475_plant = 0; static uint32_t s_s7475_pblk = 0;
static inline uint8_t s7475_rb(volatile uint8_t* r, uint32_t va) { return r[(va - 0x80000000u) ^ 3u]; }
static inline void s7475_wb(volatile uint8_t* r, uint32_t va, uint8_t v) { r[(va - 0x80000000u) ^ 3u] = v; }
}
extern "C" { unsigned char* g_rs64_s7475_bm = nullptr; }  /* 1 bit per slack byte, KSEG0 0x80000000..0x81800000 (tools/apply_s7475_slackwatch.py) */
namespace {
static inline void s7475_mark(uint32_t blk, const S7475R& b, bool on) {
    if (!g_rs64_s7475_bm) return;
    for (uint32_t a = blk + b.req; a < blk + b.sz; ++a) { const uint32_t o = a - 0x80000000u; if (o >= 0x1800000u) break;
        if (on) g_rs64_s7475_bm[o >> 3] |= (unsigned char)(1u << (o & 7u)); else g_rs64_s7475_bm[o >> 3] &= (unsigned char)~(1u << (o & 7u)); } }
struct S7475W { uint64_t n; uint32_t blk, req, sz, off; int w; void* hpc; const char* fn; };
static std::map<uint32_t, S7475W> s_s7475_wpc;  /* per store pc */
static void s7480_sum(double now);  /* s7480 class EH, defined below */
static void s7484_tick(double now);  /* s7484 class EI load plant, defined below */
static void s7486_tick(double now);  /* s7486 class EK host-read plant, defined below */
extern "C" { int g_rs64_s7486_on = 0; int g_rs64_s7489_on = 0; }  /* s7489 class EN: host-WRITE kinds 6-8 ride the s7486 path */
static int s_s7489_wplant = 0;  /* ROGUESQ_S7489_WPLANT=1: the s7486 plant targets host-write destinations (kinds 6-8) instead of read sources */
  /* s7486 class EK host-read watch gate */
extern "C" { int g_rs64_s7484_on = 0; }  /* s7484 class EI load watch gate (tools/apply_s7484_loadwatch.py) */
static volatile int g_s7480_inmalloc = 0;  /* s7480: between rs_malloc entry (rs64_s7479_pad) and exit (s6063 hook) */
static uint64_t s_s7475_stores = 0;
static std::string s7475_sym(void* pc) { char b[160]; rs64_s7324_sym(pc, b, sizeof b); return b; }
/* s7478 class EF: ROGUESQ_S7475_BT=1 keeps an 8-frame host backtrace per canary record (alloc chain) and prints it, plus the
   store's own host chain, on each first slack-store row ([s7478] alloc-bt / store-bt). Names the guest caller of rs_memset /
   rs_malloc, whose $ra the recompiled jal does not set. */
static bool s7478_bt_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7475_BT"); return e && e[0] && e[0] != '0'; }(); return on; }
static std::string s7478_chain(void* const* f, int n) { std::string s; for (int i = 0; i < n; ++i) { if (i) s += " < "; char h[24]; snprintf(h, sizeof h, "@%lx:", (unsigned long)((uintptr_t)f[i] - (uintptr_t)_dyld_get_image_vmaddr_slide(0))); s += h; s += s7475_sym(f[i]); } return s; }
static uint8_t s7475_fill() { static const uint8_t f = [] { const char* e = std::getenv("ROGUESQ_S7475_FILL"); return (uint8_t)(e && *e ? std::strtoul(e, nullptr, 0) : 0xA5u); }(); return f; }
static bool s7475_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7475_CANARY"); return e && e[0] && e[0] != '0'; }(); return on; }
/* returns false if the record is stale (header changed) */
static bool s7475_hdr_ok(volatile uint8_t* r, uint32_t blk, const S7475R& b) {
    const uint32_t w0 = s7472_rd(r, blk - 0x10u), sz = s7472_rd(r, blk - 0x0Cu), fl = w0 >> 16;
    return (fl == 2u || fl == 6u) && sz == b.sz; }
/* checks one record; returns number of hit bytes */
static int s7475_check1(volatile uint8_t* r, uint32_t blk, const S7475R& b, const char* why, uint32_t fra, double now) {
    int nh = 0;
    for (uint32_t o = b.req; o < b.sz; ++o) {
        const uint8_t v = s7475_rb(r, blk + o);
        if (v == s7475_fill()) continue;
        ++nh; const bool pl = (s_s7475_plant == 1 && blk == s_s7475_pblk);
        if (s_s7475_seen.insert({blk, o}).second && s_s7475_seen.size() <= 40)
            std::fprintf(stderr, "[s7475] tail-hit why=%s blk=%08X req=%X size=%X off=%X val=%02X alloc=%s free_ra=%08X gpc=%08X age=%.2f t=%.1f%s\n",
                         why, blk, b.req, b.sz, o, v, s7475_sym(b.hpc).c_str(), fra, (uint32_t)g_rs64_last_guest_pc, now - b.t, now - s_s7475_t0, pl ? " PLANT" : "");
    }
    if (nh) { ++s_s7475_hits; if (s_s7475_plant == 1 && blk == s_s7475_pblk) { s_s7475_plant = 2; std::fprintf(stderr, "[s7475] plant DETECTED blk=%08X after %.3f s why=%s\n", blk, now - s_s7475_ptime, why); }
              for (uint32_t o = b.req; o < b.sz; ++o) s7475_wb(r, blk + o, s7475_fill()); }  /* re-arm so a repeat writer is seen once per distinct (blk,off) */
    return nh; }
static void s7475_walk(volatile uint8_t* r, double now) {
    ++s_s7475_walks;
    for (auto it = s_s7475_live.begin(); it != s_s7475_live.end();) {
        if (!s7475_hdr_ok(r, it->first, it->second)) { ++s_s7475_stale; if (s_s7475_plant == 1 && it->first == s_s7475_pblk) { s_s7475_plant = 2; std::fprintf(stderr, "[s7475] plant LOST blk=%08X (stale)\n", it->first); } s7475_mark(it->first, it->second, false); it = s_s7475_live.erase(it); continue; }
        s7475_check1(r, it->first, it->second, "walk", 0, now); ++it; }
    if (s_s7475_walks % 40 == 1) { static int ns = 0; if (ns++ < 400)
        std::fprintf(stderr, "[s7475] sum walks=%llu t=%.1f live=%zu rec=%llu noslack=%llu hdrbad=%llu stale=%llu overlap=%llu freechk=%llu hits=%llu distinct=%zu plant=%d padded=%llu\n",
                     (unsigned long long)s_s7475_walks, now - s_s7475_t0, s_s7475_live.size(), (unsigned long long)s_s7475_rec, (unsigned long long)s_s7475_noslack,
                     (unsigned long long)s_s7475_hdrbad, (unsigned long long)s_s7475_stale, (unsigned long long)s_s7475_overlap, (unsigned long long)s_s7475_freechk,
                     (unsigned long long)s_s7475_hits, s_s7475_seen.size(), s_s7475_plant, (unsigned long long)s_s7479_padded);
        std::fprintf(stderr, "[s7475] stores=%llu wpcs=%zu\n", (unsigned long long)s_s7475_stores, s_s7475_wpc.size());
        s7480_sum(now);
        if (ns <= 400 && s_s7475_walks % 400 == 1) for (auto& kv : s_s7475_wpc) std::fprintf(stderr, "[s7475] wpc pc=%08X fn=%s n=%llu first_blk=%08X req=%X off=%X w=%d alloc=%s\n",
                     kv.first, kv.second.fn ? kv.second.fn : "?", (unsigned long long)kv.second.n, kv.second.blk, kv.second.req, kv.second.off, kv.second.w, s7475_sym(kv.second.hpc).c_str()); } }
static void s7475_tick(volatile uint8_t* r, double now) {
    static const double ms = [] { const char* e = std::getenv("ROGUESQ_S7475_CANARY_MS"); return e ? std::atof(e) : 250.0; }();
    static const double plant_s = [] { const char* e = std::getenv("ROGUESQ_S7475_CANARY_PLANT"); if (!e || !*e || *e == '0') return -1.0; double v = std::atof(e); return v <= 1.0 ? 60.0 : v; }();
    if (s_s7475_last != 0 && (now - s_s7475_last) * 1000.0 < ms && s_s7475_plant != 1) return;
    s_s7475_last = now; s7475_walk(r, now); s7484_tick(now); s7486_tick(now);
    if (s_s7475_plant == 0 && plant_s >= 0 && now - s_s7475_t0 >= plant_s) {
        uint32_t pb = 0, preq = 0; for (auto& kv : s_s7475_live) if (kv.second.req > preq) { preq = kv.second.req; pb = kv.first; }
        if (pb) { s7475_wb(r, pb + preq, (uint8_t)(s7475_fill() ^ 0xFFu)); s_s7475_pblk = pb; s_s7475_plant = 1; s_s7475_ptime = now;
                  std::fprintf(stderr, "[s7475] plant SET blk=%08X req=%X size=%X t=%.1f\n", pb, preq, s_s7475_live[pb].sz, now - s_s7475_t0); } } }
}
/* s7479 class EG: ROGUESQ_S7475_PAD=<n> (default 0, needs ROGUESQ_S7475_CANARY=1): the rs_malloc wrapper (tools/apply_s7479_mallocpad.py)
   asks the inner allocator for req+n (n rounded up to 16) while the canary records the ORIGINAL req, so every block - including the
   ~80% whose req is already 16-aligned (noslack) - carries a >=n-byte band [req, size). Measurement only; 0 = pass-through. */
extern "C" uint32_t rs64_s7479_pad(uint32_t rq) {
    static const uint32_t pad = [] { const char* e = std::getenv("ROGUESQ_S7475_PAD"); const char* c = std::getenv("ROGUESQ_S7475_CANARY");
        uint32_t v = (e && *e && c && c[0] && c[0] != '0') ? (uint32_t)std::strtoul(e, nullptr, 0) : 0u; v = (v + 15u) & ~15u;
        if (v) std::fprintf(stderr, "[s7479] pad armed n=%u\n", v); return v; }();
    g_s7480_inmalloc = 1;  /* s7480: rs_malloc entry (cleared at the s6063 exit hook) */
    if (!pad || !rq || rq > 0x7FFFFFF0u - pad) return rq;
    __atomic_add_fetch(&s_s7479_padded, 1, __ATOMIC_RELAXED); return rq + pad; }
/* s7480 class EH: guest stores into FREED rs_malloc blocks (use-after-free writes). ROGUESQ_S7480_UAF=1 (default off; needs
   ROGUESQ_S7475_CANARY=1 for the store bitmap and ROGUESQ_STORE_DIAG=1 for the per-store hook): at rs_free entry the block's data
   [ptr, ptr+size) (size from its header) is recorded and marked in g_rs64_s7475_bm; an rs_malloc exit trims every freed record
   overlapping the new block (keeping both remainders, minus the split header). A marked guest store then lands in rs64_s7475_store:
   allocator-internal writers (rs_malloc family / heap list helpers; rs_memset only between rs_malloc entry and exit) are counted
   per fn as `internal` (natural positive control: the split header of a reused freed block MUST land here) and only the stored
   bytes are unmarked; anything else logs `[s7480] uaf-store pc= fn= a= w= blk= n= off= age= hdr= size=` once per freed record
   (then the record is dropped) with ROGUESQ_S7475_BT=1 adding the host free/store chains (= guest call chains). Planted control
   ROGUESQ_S7480_PLANT=<s> (1 -> 60): <s> s after arming, the next rs_malloc block with req >= 0x40 is ALSO recorded as freed
   (guest memory untouched); the game's own first store into it MUST log `PLANT` + `[s7480] plant DETECTED`. Measurement only. */
namespace {
struct S7480F { uint32_t n; double t; int plant; void* bt[8]; int nbt; uint32_t far, fh[3]; uint32_t nld = 0; char lk = 0; uint16_t hk = 0; };  /* s7486: hk = host-read kinds seen (bit per kind; s7489: 9 kinds incl. host writes) */  /* s7484: plant 2 = load plant; nld/lk = load hits + class at first load */
static std::map<uint32_t, S7480F> s_s7480_freed;
static std::map<std::string, uint64_t> s_s7480_internal;
static std::map<uint32_t, uint64_t> s_s7480_pcs;
extern "C" { volatile uint32_t g_rs64_s7481_task_out = 0; }  /* s7481: last gfx RSP task output_buff (KSEG0), set in main.cpp at the [lle task] site */
static uint64_t s_s7480_loc[5] = {0, 0, 0, 0, 0};  /* [4] s7481 S = F hit whose covering free block is followed directly by the RSP task out block (data end + 0x10 hdr == out): the game's tail-of-free-span frame DL arena (s6202/s6205 coalesce carve), not a UAF */  /* non-plant hits located in U used (carve / torn-down arena parent) / F free (= real use-after-free) / N no chain (arena gone) / U whose block is a malloc-hook record (= trim defect) */
static uint64_t s_s7480_frees = 0, s_s7480_trims = 0, s_s7480_hits = 0, s_s7480_skip = 0;
static int s_s7480_plant = 0, s_s7480_ptries = 0; static double s_s7480_ptime = 0;
static int s_s7484_plant = 0, s_s7484_ptries = 0; static double s_s7484_ptime = 0;  /* s7484 class EI load plant */
static bool s7480_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7480_UAF"); const bool v = e && e[0] && e[0] != '0' && s7475_on();
    if (v) std::fprintf(stderr, "[s7480] uaf watch armed\n"); return v; }(); return on; }
static void s7480_range(uint32_t lo, uint32_t hi, bool on) {
    if (!g_rs64_s7475_bm) return;
    for (uint32_t a = lo; a < hi; ) { const uint32_t o = a - 0x80000000u; if (o >= 0x1800000u) break;
        if ((o & 7u) == 0 && a + 8u <= hi) { g_rs64_s7475_bm[o >> 3] = on ? 0xFFu : 0u; a += 8u; continue; }
        if (on) g_rs64_s7475_bm[o >> 3] |= (unsigned char)(1u << (o & 7u)); else g_rs64_s7475_bm[o >> 3] &= (unsigned char)~(1u << (o & 7u)); ++a; } }
static void s7480_add(uint32_t blk, uint32_t n, double now, int plant) {
    S7480F f{n, now, plant, {}, 0, 0, {0, 0, 0}}; if (s7478_bt_on()) f.nbt = backtrace(f.bt, 8);
    s_s7480_freed[blk] = f; s7480_range(blk, blk + n, true); }
/* drop/trim every freed record overlapping [lo, hi); right remainder starts after a 0x10 split header */
static void s7480_trim(uint32_t lo, uint32_t hi) {
    auto it = s_s7480_freed.upper_bound(lo); if (it != s_s7480_freed.begin()) --it;
    std::vector<std::pair<uint32_t, S7480F>> keep;
    while (it != s_s7480_freed.end() && it->first < hi) {
        const uint32_t s = it->first, e = s + it->second.n;
        if (e <= lo) { ++it; continue; }
        ++s_s7480_trims; S7480F f = it->second;
        if (f.plant == 1 && s_s7480_plant == 1) { s_s7480_plant = 0; std::fprintf(stderr, "[s7480] plant LOST blk=%08X (realloc/free before a store)\n", s); }
        if (f.plant == 2 && s_s7484_plant == 1) { s_s7484_plant = 0; std::fprintf(stderr, "[s7484] plant LOST blk=%08X (realloc/free before a load)\n", s); }
        s7480_range(s, e, false); it = s_s7480_freed.erase(it);
        if (f.plant) continue;
        if (s < lo && lo - s >= 0x10u) { S7480F l = f; l.n = lo - s; keep.emplace_back(s, l); }
        if (e > hi + 0x10u) { S7480F r2 = f; r2.n = e - (hi + 0x10u); keep.emplace_back(hi + 0x10u, r2); } }
    for (auto& k : keep) { s_s7480_freed[k.first] = k.second; s7480_range(k.first, k.first + k.second.n, true); } }
/* which guest-chain block holds a right now: walks the 3 arena heads (s7472 layout). kind U=used F=free N=in no chain */
static char s7480_locate(volatile uint8_t* r, uint32_t a, uint32_t* lb, uint32_t* ls, uint32_t* lf, uint32_t* arena) {
    *lb = 0; *ls = 0;
    static const uint32_t heads[3] = {0x8010FEFCu, 0x8010FF00u, 0x8010FF18u}; const uint32_t top = rs64_ram_top; uint32_t seen[3] = {0, 0, 0}; int na = 0;
    for (int i = 0; i < 3; ++i) { const uint32_t h0 = s7472_rd(r, heads[i]); if (h0 < 0x80000000u || h0 >= top) continue;
        bool dup = false; for (int j = 0; j < na; ++j) dup |= seen[j] == h0; if (dup) continue; seen[na++] = h0;
        uint32_t b = h0; for (int g = 0; g < 400000; ++g) { const uint32_t w0 = s7472_rd(r, b), sz = s7472_rd(r, b + 4u), fl = w0 >> 16;
            if ((fl & 8u) || (fl != 1u && fl != 2u && fl != 6u) || (sz & 0xFu) || b + 0x10u + sz <= b || b + 0x10u + sz >= top) break;
            if (a >= b && a < b + 0x10u + sz && (!*lb || sz < *ls)) { *lb = b + 0x10u; *ls = sz; *lf = fl; *arena = h0; }  /* innermost over all arenas */
            b += 0x10u + sz; } }
    if (!*lb) { *ls = *lf = *arena = 0; return 'N'; } return *lf == 1u ? 'F' : 'U'; }
static void s7480_free(volatile uint8_t* r, uint32_t ptr, double now) {
    if (!s7480_on() || !g_rs64_s7475_bm || ptr < 0x80000010u || ptr >= rs64_ram_top) return;
    const uint32_t w0 = s7472_rd(r, ptr - 0x10u), sz = s7472_rd(r, ptr - 0x0Cu), fl = w0 >> 16;
    if (!((fl == 2u || fl == 6u) && sz && !(sz & 0xFu) && ptr + sz <= rs64_ram_top)) { ++s_s7480_skip; return; }
    s7480_trim(ptr - 0x10u, ptr + sz); s7480_add(ptr, sz, now, 0); ++s_s7480_frees;
    { S7480F& f = s_s7480_freed[ptr]; uint32_t lb, ls, lf; s7480_locate(r, ptr, &lb, &ls, &lf, &f.far);
      f.fh[0] = s7472_rd(r, 0x8010FEFCu); f.fh[1] = s7472_rd(r, 0x8010FF00u); f.fh[2] = s7472_rd(r, 0x8010FF18u); } }
static void s7480_malloc(uint32_t req, uint32_t ptr, double now) {
    g_s7480_inmalloc = 0;
    if (!s7480_on() || !g_rs64_s7475_bm || !ptr || ptr < 0x80000010u || ptr >= rs64_ram_top) return;
    const uint32_t sz = s7472_rd(g_recomp_rdram_for_wp_raw, ptr - 0x0Cu); const uint32_t hi = ptr + (sz >= req && sz < 0x1000000u ? sz : req);
    s7480_trim(ptr - 0x10u, hi);
    static const double plant_s = [] { const char* e = std::getenv("ROGUESQ_S7480_PLANT"); if (!e || !*e || *e == '0') return -1.0; double v = std::atof(e); return v <= 1.0 ? 60.0 : v; }();
    if (s_s7480_plant == 0 && plant_s >= 0 && now - s_s7475_t0 >= plant_s && req >= 0x40u && s_s7480_ptries < 20) {
        ++s_s7480_ptries; s7480_add(ptr, req, now, 1); s_s7480_plant = 1; s_s7480_ptime = now;
        std::fprintf(stderr, "[s7480] plant SET blk=%08X req=%X try=%d t=%.1f\n", ptr, req, s_s7480_ptries, now - s_s7475_t0); } }
static bool s7480_internal_fn(const char* fn) {
    static const char* const k[] = {"rs_malloc", "rs_malloc_s5041_inner", "rs_free", "ensureHeapInitialized", "buildHeapFreeList", "coalesceFreeHeapBlocks",
        "coalesceFreeHeapBlocks_s7325_inner", "heapFreeListDequeue", "heapFreeListInsert", "initMainHeap", "initRsMallocHeap", "findLargestFreeHeapChunk"};
    if (!fn) return false; for (const char* s : k) if (!std::strcmp(fn, s)) return true;
    return g_s7480_inmalloc && !std::strcmp(fn, "rs_memset"); }
/* s7488 class EM: swl/swr (tools/apply_s7488_ustorewatch.py). g_rs64_s7488_cnt[idx] = executions per generated site; t_s7488_ust = the
   current rs64_s7475_store call came from an swl/swr site (exact bytes written: swl [a,a|3], swr [a&~3,a]); plant 5 = EM control (a LIVE
   heap block an swl/swr just wrote, recorded as freed: the next swl/swr store into it MUST log `[s7488] ust-ctl DETECTED`).
   s_s7488_loc = class of each swl/swr pc's first freed-record hit (U F N Urec S); s_s7488_slack = swl/swr stores into canary slack. */
extern "C" { int g_rs64_s7488_on = 0; unsigned int g_rs64_s7488_cnt[1024] = {0}; }
static thread_local int t_s7488_ust = 0;
struct S7488S { uint32_t pc = 0; uint64_t samp = 0, heap = 0; std::string fn; };
static std::map<int, S7488S> s_s7488_site;
static std::map<uint32_t, uint64_t> s_s7488_pcs;
static uint64_t s_s7488_marked = 0, s_s7488_hits = 0, s_s7488_slack = 0, s_s7488_loc[5] = {0, 0, 0, 0, 0};
static int s_s7488_ctl = 0, s_s7488_ctries = 0; static double s_s7488_ctime = 0; static uint32_t s_s7488_cblk = 0;
/* returns 1 when the store hit a freed record (handled) */
static int s7480_store(uint32_t pc, uint32_t a, int w, const char* fn) {
    if (!s7480_on() || s_s7480_freed.empty()) return 0;
    auto it = s_s7480_freed.upper_bound(a + (uint32_t)w - 1u); if (it == s_s7480_freed.begin()) return 0; --it;
    const uint32_t blk = it->first; const S7480F f = it->second;
    if (a >= blk + f.n || a + (uint32_t)w <= blk) return 0;
    if (s7480_internal_fn(fn)) { ++s_s7480_internal[fn]; s7480_range(a < blk ? blk : a, a + (uint32_t)w, false); return 1; }
    if (f.plant == 5) { if (!t_s7488_ust) return 1;  /* s7488 EM control: live block, only an swl/swr store counts */
        if (s_s7488_ctl == 1) { s_s7488_ctl = 2; std::fprintf(stderr, "[s7488] ust-ctl DETECTED blk=%08X after %.3f s pc=%08X fn=%s a=%08X w=%d\n", blk, s7325_now() - s_s7488_ctime, pc, fn ? fn : "?", a, w); }
        s7480_range(blk, blk + f.n, false); s_s7480_freed.erase(it); return 1; }
    if (f.plant == 3 || f.plant == 4) return 1;  /* s7486 host-read plant / s7487 EL control: a LIVE block, guest stores into it are expected */
    if (f.plant == 2) { if (s_s7484_plant == 1) { s_s7484_plant = 0; std::fprintf(stderr, "[s7484] plant STORE-FIRST blk=%08X pc=%08X fn=%s (re-plant)\n", blk, pc, fn ? fn : "?"); }
        s7480_range(blk, blk + f.n, false); s_s7480_freed.erase(it); return 1; }  /* s7484 load plant: a store came first, retry on another block */
    ++s_s7480_hits; const bool first = s_s7480_pcs[pc]++ == 0; volatile uint8_t* rr = g_recomp_rdram_for_wp_raw; const double now = s7325_now();
    uint32_t lb = 0, ls = 0, lf = 0, lar = 0; const char lk = rr ? s7480_locate(rr, a, &lb, &ls, &lf, &lar) : '?';
    char lk2 = lk; if (lk == 'F' && g_rs64_s7481_task_out && lb + ls + 0x10u == g_rs64_s7481_task_out) lk2 = 'S';
    if (lk == 'F' && rr) { const uint32_t e8 = s7472_rd(rr, 0x801163E8u);  /* s7481: frame pool ptr; the s6202 g1d retarget puts it at ec-t2 inside a FREE heap block */
        if (e8 >= lb && e8 < lb + ls && a >= e8 && a < lb + ls) lk2 = 'S'; }
    { static int s7481_nf = 0; if (!f.plant && lk2 == 'F' && s7481_nf < 60) { ++s7481_nf;  /* s7481: every F (non-S) hit, capped, with the span end vs task out */
        std::fprintf(stderr, "[s7481] F-hit pc=%08X fn=%s a=%08X blk=%08X n=%X age=%.3f lblk=%08X lend=%08X task_out=%08X t=%.1f\n", pc, fn ? fn : "?", a, blk, f.n, now - f.t, lb, lb + ls + 0x10u, (unsigned)g_rs64_s7481_task_out, now - s_s7475_t0); } }
    if (!f.plant) { const int ki = lk2 == 'S' ? 4 : lk == 'U' ? 0 : lk == 'F' ? 1 : 2; ++s_s7480_loc[ki]; if (lk == 'U' && s_s7475_live.count(lb)) ++s_s7480_loc[3]; }
    if (!f.plant && t_s7488_ust) { ++s_s7488_hits; if (s_s7488_pcs[pc]++ == 0) { const char c8 = (lk == 'U' && s_s7475_live.count(lb)) ? 'R' : lk2;
        ++s_s7488_loc[c8 == 'U' ? 0 : c8 == 'F' ? 1 : c8 == 'R' ? 3 : c8 == 'S' ? 4 : 2];
        std::fprintf(stderr, "[s7488] ust-hit pc=%08X fn=%s a=%08X w=%d blk=%08X loc=%c age=%.3f t=%.1f\n", pc, fn ? fn : "?", a, w, blk, c8, now - f.t, now - s_s7475_t0); } }  /* plant excluded: F = still free in its chain (UAF), Urec = trim defect */
    if (first && s_s7480_pcs.size() <= 60)
        std::fprintf(stderr, "[s7480] uaf-store pc=%08X fn=%s a=%08X w=%d blk=%08X n=%X off=%X age=%.3f hdr=%08X size=%08X inmalloc=%d loc=%c lblk=%08X lsz=%X lfl=%X arena=%08X lrec=%d free_arena=%08X heads_free=%08X/%08X/%08X heads_now=%08X/%08X/%08X t=%.1f%s\n", pc, fn ? fn : "?", a, w, blk, f.n,
                     a - blk, now - f.t, rr ? s7472_rd(rr, blk - 0x10u) : 0u, rr ? s7472_rd(rr, blk - 0x0Cu) : 0u, (int)g_s7480_inmalloc, lk2, lb, ls, lf, lar, (int)s_s7475_live.count(lb), f.far, f.fh[0], f.fh[1], f.fh[2],
                     rr ? s7472_rd(rr, 0x8010FEFCu) : 0u, rr ? s7472_rd(rr, 0x8010FF00u) : 0u, rr ? s7472_rd(rr, 0x8010FF18u) : 0u, now - s_s7475_t0, f.plant ? " PLANT" : "");
    if (first && s7478_bt_on() && s_s7480_pcs.size() <= 60) { void* sb[10]; const int ns = backtrace(sb, 10);
        std::fprintf(stderr, "[s7480] store-bt pc=%08X chain=%s\n", pc, s7478_chain(sb, ns).c_str());
        std::fprintf(stderr, "[s7480] free-bt blk=%08X chain=%s\n", blk, s7478_chain(f.bt, f.nbt).c_str()); }
    if (f.plant && s_s7480_plant == 1) { s_s7480_plant = 2; std::fprintf(stderr, "[s7480] plant DETECTED blk=%08X after %.3f s pc=%08X fn=%s\n", blk, now - s_s7480_ptime, pc, fn ? fn : "?"); }
    s7480_range(blk, blk + f.n, false); s_s7480_freed.erase(it); return 1; }
/* s7484 class EI: guest LOADS from freed rs_malloc blocks (use-after-free reads). ROGUESQ_S7484_UAFLOAD=1 on top of
   ROGUESQ_S7480_UAF=1 (+ S7475_CANARY): tools/apply_s7484_loadwatch.py wraps every generated lw/lh/lb/ld(c1) with a bitmap test
   of g_rs64_s7475_bm (gate g_rs64_s7484_on); a marked byte lands here. Hits in a freed record are located in the guest's own
   chains at the record's first load and at each pc's first load (same classes as s7480: F = still free = real UAF read, Urec =
   trim defect, U/N = re-carved / torn-down arena, S = s6202 frame span); each pc logs one `[s7484] uaf-load` row. A record is
   retired after 4096 load hits (bounded cost; counted). Loads into s7475 slack (past the request, PAD band) are counted as
   slack, first 30 pcs logged. Controls: the s7475 frame-counter word 0x8011A890 (marked at arming) -> `[s7484] watch-ctl PASS`;
   ROGUESQ_S7484_PLANT=<s>: <s> s after arming, the most recent live canary block (age >= 0.5 s, req >= 0x40) is ALSO recorded as
   freed (guest memory untouched); the game's next load of it MUST log `[s7484] plant DETECTED` (a store first = STORE-FIRST,
   re-plant after 10 s silence too, 20 tries). Measurement only. */
static std::map<uint32_t, uint64_t> s_s7484_pcs, s_s7484_spcs;
/* s7487 class EL: lwl/lwr (tools/apply_s7487_lwlwatch.py). g_rs64_s7487_cnt[idx] = executions per generated site; t_s7487_lwx = the
   current s7484_load call came from an lwl/lwr site; plant 4 = EL control (a LIVE heap block an lwl/lwr just read, recorded as freed:
   the next lwl/lwr read of it MUST log `[s7487] lwl-ctl DETECTED`). s_s7487_loc = class of each lwl/lwr pc's first freed-record hit. */
extern "C" { int g_rs64_s7487_on = 0; unsigned int g_rs64_s7487_cnt[1024] = {0}; }
static thread_local int t_s7487_lwx = 0;
struct S7487S { uint32_t pc = 0; uint64_t samp = 0, heap = 0; uint32_t a0 = 0, ah = 0; std::string fn; };
static std::map<int, S7487S> s_s7487_site;
static uint64_t s_s7487_marked = 0, s_s7487_hits = 0, s_s7487_loc[5] = {0, 0, 0, 0, 0};  /* U F N Urec S */
static int s_s7487_ctl = 0, s_s7487_ctries = 0; static double s_s7487_ctime = 0; static uint32_t s_s7487_cblk = 0;
static uint64_t s_s7484_hits = 0, s_s7484_slack = 0, s_s7484_intl = 0, s_s7484_retired = 0, s_s7484_recs = 0, s_s7484_ctl = 0, s_s7484_p1 = 0;
static uint64_t s_s7484_loc[5] = {0, 0, 0, 0, 0};  /* per record at its first load: U F N Urec S */
static int s7484_load(uint32_t pc, uint32_t a, int w, const char* fn) {
    auto it = s_s7480_freed.upper_bound(a + (uint32_t)w - 1u);
    bool in = it != s_s7480_freed.begin(); if (in) { --it; in = a < it->first + it->second.n && a + (uint32_t)w > it->first; }
    if (!in) { ++s_s7484_slack; if (s_s7484_spcs[pc]++ == 0 && s_s7484_spcs.size() <= 30) std::fprintf(stderr, "[s7484] slack-load pc=%08X fn=%s a=%08X w=%d t=%.1f\n", pc, fn ? fn : "?", a, w, s7325_now() - s_s7475_t0); return 0; }
    if (s7480_internal_fn(fn)) { ++s_s7484_intl; return 1; }
    const uint32_t blk = it->first; S7480F& f = it->second; const double now = s7325_now();
    if (f.plant == 2) { if (s_s7484_plant == 1) { s_s7484_plant = 2; std::fprintf(stderr, "[s7484] plant DETECTED blk=%08X after %.3f s pc=%08X fn=%s a=%08X\n", blk, now - s_s7484_ptime, pc, fn ? fn : "?", a); }
        s7480_range(blk, blk + f.n, false); s_s7480_freed.erase(it); return 1; }
    if (f.plant == 4) { if (!t_s7487_lwx) return 1;  /* s7487 EL control: live block, only an lwl/lwr read counts */
        if (s_s7487_ctl == 1) { s_s7487_ctl = 2; std::fprintf(stderr, "[s7487] lwl-ctl DETECTED blk=%08X after %.3f s pc=%08X fn=%s a=%08X w=%d\n", blk, now - s_s7487_ctime, pc, fn ? fn : "?", a, w); }
        s7480_range(blk, blk + f.n, false); s_s7480_freed.erase(it); return 1; }
    if (f.plant == 1) { ++s_s7484_p1; return 1; }
    if (f.plant == 3 || f.plant == 5) return 1;  /* s7486 host-read plant / s7488 EM control: live block, guest loads expected */  /* s7480 store plant read before its first store: not a free block */
    ++s_s7484_hits; const bool first = s_s7484_pcs[pc]++ == 0; volatile uint8_t* rr = g_recomp_rdram_for_wp_raw;
    char lk = '?', lk2 = '?'; uint32_t lb = 0, ls = 0, lf = 0, lar = 0;
    if ((!f.lk || first) && rr) { lk = s7480_locate(rr, a, &lb, &ls, &lf, &lar); lk2 = lk;
        if (lk == 'F' && g_rs64_s7481_task_out && lb + ls + 0x10u == g_rs64_s7481_task_out) lk2 = 'S';
        if (lk == 'F') { const uint32_t e8 = s7472_rd(rr, 0x801163E8u); if (e8 >= lb && e8 < lb + ls && a >= e8 && a < lb + ls) lk2 = 'S'; }
        if (!f.lk) { f.lk = (lk == 'U' && s_s7475_live.count(lb)) ? 'R' : lk2; ++s_s7484_recs;
            ++s_s7484_loc[f.lk == 'U' ? 0 : f.lk == 'F' ? 1 : f.lk == 'R' ? 3 : f.lk == 'S' ? 4 : 2]; } }
    if (t_s7487_lwx) { ++s_s7487_hits; if (first) { const char c7 = (lk == 'U' && s_s7475_live.count(lb)) ? 'R' : lk2;
        ++s_s7487_loc[c7 == 'U' ? 0 : c7 == 'F' ? 1 : c7 == 'R' ? 3 : c7 == 'S' ? 4 : 2];
        std::fprintf(stderr, "[s7487] lwl-hit pc=%08X fn=%s a=%08X w=%d blk=%08X loc=%c age=%.3f t=%.1f\n", pc, fn ? fn : "?", a, w, blk, c7, now - f.t, now - s_s7475_t0); } }
    if (first && s_s7484_pcs.size() <= 80)
        std::fprintf(stderr, "[s7484] uaf-load pc=%08X fn=%s a=%08X w=%d blk=%08X n=%X off=%X age=%.3f loc=%c rec=%c lblk=%08X lsz=%X lfl=%X arena=%08X lrec=%d free_arena=%08X hdr=%08X size=%08X val=%08X heads_free=%08X/%08X/%08X heads_now=%08X/%08X/%08X t=%.1f\n",
                     pc, fn ? fn : "?", a, w, blk, f.n, a - blk, now - f.t, lk2, f.lk ? f.lk : '?', lb, ls, lf, lar, (int)s_s7475_live.count(lb), f.far,
                     rr ? s7472_rd(rr, blk - 0x10u) : 0u, rr ? s7472_rd(rr, blk - 0x0Cu) : 0u, rr ? s7472_rd(rr, a & ~3u) : 0u, f.fh[0], f.fh[1], f.fh[2],
                     rr ? s7472_rd(rr, 0x8010FEFCu) : 0u, rr ? s7472_rd(rr, 0x8010FF00u) : 0u, rr ? s7472_rd(rr, 0x8010FF18u) : 0u, now - s_s7475_t0);
    if (first && lk2 == 'F' && s7478_bt_on()) { static int nb = 0; if (nb++ < 40) { void* sb[10]; const int ns = backtrace(sb, 10);
        std::fprintf(stderr, "[s7484] load-bt pc=%08X chain=%s\n", pc, s7478_chain(sb, ns).c_str());
        std::fprintf(stderr, "[s7484] free-bt blk=%08X chain=%s\n", blk, s7478_chain(f.bt, f.nbt).c_str()); } }
    if (++f.nld >= 4096u) { ++s_s7484_retired; s7480_range(blk, blk + f.n, false); s_s7480_freed.erase(it); }
    return 1; }
static void s7484_tick(double now) {
    static const double plant_s = [] { const char* e = std::getenv("ROGUESQ_S7484_PLANT"); if (!e || !*e || *e == '0') return -1.0; double v = std::atof(e); return v <= 1.0 ? 60.0 : v; }();
    if (plant_s < 0 || !g_rs64_s7484_on) return;
    if (s_s7484_plant == 1 && now - s_s7484_ptime > 10.0) {  /* not read in 10 s: drop and re-plant */
        for (auto it = s_s7480_freed.begin(); it != s_s7480_freed.end(); ++it) if (it->second.plant == 2) { s7480_range(it->first, it->first + it->second.n, false); s_s7480_freed.erase(it); break; }
        s_s7484_plant = 0; std::fprintf(stderr, "[s7484] plant TIMEOUT try=%d\n", s_s7484_ptries); }
    if (s_s7484_plant != 0 || now - s_s7475_t0 < plant_s || s_s7484_ptries >= 60) return;
    uint32_t best = 0; double bt = -1;
    for (auto& kv : s_s7475_live) if (kv.second.req >= 0x40u && now - kv.second.t >= 0.5 && kv.second.t > bt && !s_s7480_freed.count(kv.first)) { best = kv.first; bt = kv.second.t; }
    if (!best) return;
    ++s_s7484_ptries; s7480_add(best, s_s7475_live[best].req, now, 2); s_s7484_plant = 1; s_s7484_ptime = now;
    std::fprintf(stderr, "[s7484] plant SET blk=%08X req=%X age=%.2f try=%d t=%.1f\n", best, s_s7475_live[best].req, now - bt, s_s7484_ptries, now - s_s7475_t0); }
/* s7486 class EK: HOST readers of freed rs_malloc blocks. ROGUESQ_S7486_HOSTUAF=1 on top of ROGUESQ_S7480_UAF=1 (+ S7475_CANARY):
   every host read of guest RDRAM that follows a guest pointer calls rs64_s7486_hostread(kind, addr, len): kind 0 sp_dma_gfx /
   1 sp_dma_aud (librecomp rsp.hpp dma_rdram_to_dmem via the s7094 hook, IMEM boot DMAs excluded), 2 rdp_cmd (the RDP command range
   as dpc_bridge.cpp rsp_dpc_submit_impl hands it to RT64), 3 rdp_tex (LoadBlock / LoadTile / LoadTLUT source span from the last
   SetTextureImage), 5 ai_dma (osAiSetNextBuffer source). The range is tested against g_rs64_s7475_bm; a marked byte is attributed
   under s_s7475_mu: inside a freed s7480 record -> the record's class AT THIS READ from the guest's own chains (F = still free =
   real host use-after-free, Urec = trim defect, U/N = re-carved / torn-down arena, S = s6202 frame span), once per (record, kind);
   inside a live canary record's slack -> C (= positive control: the bitmap path sees host reads); else stale. Controls (same run):
   ctl = C ranges per kind (must be > 0 for sp_dma_gfx); ROGUESQ_S7486_PLANT=<s>: <s> s after arming, the LIVE heap block holding a
   recent sp_dma_gfx source (located in the guest chains) is recorded as freed with plant=3 (guest stores / loads into it ignored,
   guest memory untouched); the next host read of it MUST log `[s7486] plant DETECTED kind=` (2 s timeout, 30 tries). Measurement only. */
/* s7489 class EN: kinds 6 sp_wr_gfx / 7 sp_wr_aud (librecomp rsp.hpp dma_dmem_to_rdram via the s7094 hook, called BEFORE the copy) and
   8 pi_dma (pi.cpp do_dma ROM -> RDRAM, called before do_rom_read) are host WRITES into guest RDRAM, classified exactly like the reads:
   F = a host DMA wrote a still-free block (real host use-after-free write), Urec = trim defect, ctl = write into a live block's canary
   slack (DMA length rounding inside the block's own allocation, harmless; proves the bitmap path sees host writes). Gate
   ROGUESQ_S7489_HOSTWRITE=1 on top of S7486_HOSTUAF; ROGUESQ_S7489_WPLANT=1 points the s7486 plant at a recent host-write destination
   (with S7486_PLANT=<s>), so `[s7486] plant DETECTED kind=sp_wr_*|pi_dma` is the write-path positive control. Measurement only. */
static const char* const k_s7486_kind[9] = {"sp_dma_gfx", "sp_dma_aud", "rdp_cmd", "rdp_tex", "rdp_tlut", "ai_dma", "sp_wr_gfx", "sp_wr_aud", "pi_dma"};
static uint64_t s_s7486_rng[9], s_s7486_mark[9], s_s7486_ctl[9], s_s7486_rec[9], s_s7486_stale[9], s_s7486_loc[9][5], s_s7486_bytes[9];
static int s_s7486_plant = 0, s_s7486_ptries = 0; static double s_s7486_ptime = 0; static uint32_t s_s7486_pblk = 0;
static std::atomic<uint32_t> s_s7486_recent[16]; static std::atomic<uint32_t> s_s7486_ri{0};
static int s_s7486_nlog = 0; static uint32_t s_s7486_ctlblk = 0; static int s_s7486_ctlkind = 0;  /* last live canary block a host read covered (plant target) */
extern "C" int rs64_s7501_on; extern "C" void rs64_s7501_w(uint32_t, uint32_t, int); extern "C" int rs64_s7501_cpu(uint32_t, uint32_t, int, const char*);  /* s7501 EZ (main.cpp) */
extern "C" void rs64_s7486_hostread(int kind, uint32_t addr, uint32_t len) {
    if (rs64_s7501_on && kind >= 6 && kind <= 8 && len) rs64_s7501_w(addr, len, kind);  /* s7501 EZ: host DMA write, before any gate */
    if (!g_rs64_s7486_on || kind < 0 || kind > 8 || !len) return;
    if (kind >= 6 && !g_rs64_s7489_on) return;
    const uint32_t a = (addr & 0x00FFFFFFu) | 0x80000000u; if (len > 0x100000u) len = 0x100000u;
    if (a + len > rs64_ram_top || a + len < a) return;
    __atomic_add_fetch(&s_s7486_rng[kind], 1, __ATOMIC_RELAXED); __atomic_add_fetch(&s_s7486_bytes[kind], len, __ATOMIC_RELAXED);
    if ((s_s7489_wplant ? kind >= 6 : (kind == 0 || kind == 3)) && len >= 8u) s_s7486_recent[s_s7486_ri.fetch_add(1, std::memory_order_relaxed) & 15u].store(a, std::memory_order_relaxed);  /* plant fallback sources (len >= 8 => [a, a+8) inside the read) */
    const unsigned char* bm = g_rs64_s7475_bm; if (!bm) return;
    const uint32_t o0 = a - 0x80000000u, o1 = o0 + len;
    uint32_t hit = 0; bool any = false;
    for (uint32_t o = o0; o < o1;) {  /* byte-of-bitmap stride where possible */
        const unsigned char b = bm[o >> 3];
        if (!b) { o = (o | 7u) + 1u; continue; }
        if (b & (1u << (o & 7u))) { hit = o; any = true; break; } ++o; }
    if (!any) return;
    __atomic_add_fetch(&s_s7486_mark[kind], 1, __ATOMIC_RELAXED);
    const uint32_t ha = hit + 0x80000000u; const double now = s7325_now();
    std::lock_guard<std::mutex> lk(s_s7475_mu);
    /* every freed record overlapping the range (a DMA can span several) */
    bool rec_any = false;
    auto it = s_s7480_freed.upper_bound(a); if (it != s_s7480_freed.begin()) --it;
    for (; it != s_s7480_freed.end() && it->first < a + len; ++it) {
        const uint32_t blk = it->first; S7480F& f = it->second;
        if (blk + f.n <= a) continue;
        rec_any = true; const uint32_t ra = a > blk ? a : blk;
        if (f.plant == 3) { if (s_s7486_plant == 1) { s_s7486_plant = 2; std::fprintf(stderr, "[s7486] plant DETECTED kind=%s blk=%08X after %.3f s a=%08X len=%X\n", k_s7486_kind[kind], blk, now - s_s7486_ptime, a, len);
                std::fflush(stderr); s7480_range(blk, blk + f.n, false); s_s7480_freed.erase(it); } return; }
        if (f.plant) continue;
        if (f.hk & (1u << kind)) continue; f.hk |= (uint16_t)(1u << kind); ++s_s7486_rec[kind];
        volatile uint8_t* rr = g_recomp_rdram_for_wp_raw; uint32_t lb = 0, ls = 0, lf = 0, lar = 0;
        const char lk0 = rr ? s7480_locate(rr, ra, &lb, &ls, &lf, &lar) : 'N'; char lk2 = lk0;
        if (lk0 == 'F' && g_rs64_s7481_task_out && lb + ls + 0x10u == g_rs64_s7481_task_out) lk2 = 'S';
        if (lk0 == 'F' && rr) { const uint32_t e8 = s7472_rd(rr, 0x801163E8u); if (e8 >= lb && e8 < lb + ls && ra >= e8 && ra < lb + ls) lk2 = 'S'; }
        if (lk0 == 'U' && s_s7475_live.count(lb)) lk2 = 'R';
        const int ki = lk2 == 'U' ? 0 : lk2 == 'F' ? 1 : lk2 == 'R' ? 3 : lk2 == 'S' ? 4 : 2; ++s_s7486_loc[kind][ki];
        if (s_s7486_nlog < 120 && (lk2 == 'F' || lk2 == 'R' || s_s7486_nlog < 60)) { ++s_s7486_nlog;
            std::fprintf(stderr, "[s7486] host-uaf kind=%s a=%08X len=%X ra=%08X blk=%08X n=%X off=%X age=%.3f loc=%c lblk=%08X lsz=%X lfl=%X arena=%08X free_arena=%08X gpc=%08X heads_free=%08X/%08X/%08X heads_now=%08X/%08X/%08X t=%.1f\n",
                k_s7486_kind[kind], a, len, ra, blk, f.n, ra - blk, now - f.t, lk2, lb, ls, lf, lar, f.far, (uint32_t)g_rs64_last_guest_pc, f.fh[0], f.fh[1], f.fh[2],
                rr ? s7472_rd(rr, 0x8010FEFCu) : 0u, rr ? s7472_rd(rr, 0x8010FF00u) : 0u, rr ? s7472_rd(rr, 0x8010FF18u) : 0u, now - s_s7475_t0);
            if ((lk2 == 'F' || lk2 == 'R') && s7478_bt_on()) { void* sb[12]; const int ns = backtrace(sb, 12);
                std::fprintf(stderr, "[s7486] read-bt kind=%s chain=%s\n", k_s7486_kind[kind], s7478_chain(sb, ns).c_str());
                std::fprintf(stderr, "[s7486] free-bt blk=%08X chain=%s\n", blk, s7478_chain(f.bt, f.nbt).c_str()); } } }
    if (rec_any) return;
    auto lv = s_s7475_live.upper_bound(ha); if (lv != s_s7475_live.begin()) { --lv; if (ha >= lv->first + lv->second.req && ha < lv->first + lv->second.sz) {
        if (s_s7489_wplant ? kind >= 6 : kind == 0) { s_s7486_ctlblk = lv->first; s_s7486_ctlkind = kind; }
        if (s_s7486_ctl[kind]++ == 0) std::fprintf(stderr, "[s7486] ctl PASS kind=%s a=%08X len=%X slack_blk=%08X req=%X size=%X hit=%08X\n", k_s7486_kind[kind], a, len, lv->first, lv->second.req, lv->second.sz, ha);
        return; } }
    ++s_s7486_stale[kind]; }
static void s7486_tick(double now) {  /* called from s7475_tick, s_s7475_mu held */
    static const double plant_s = [] { const char* e = std::getenv("ROGUESQ_S7486_PLANT"); if (!e || !*e || *e == '0') return -1.0; double v = std::atof(e); return v <= 1.0 ? 60.0 : v; }();
    if (plant_s < 0 || !g_rs64_s7486_on) return;
    if (s_s7486_plant == 1) {
        auto it = s_s7480_freed.find(s_s7486_pblk); const bool gone = it == s_s7480_freed.end() || it->second.plant != 3;
        if (!gone && now - s_s7486_ptime <= 2.0) return;
        if (!gone) { s7480_range(it->first, it->first + it->second.n, false); s_s7480_freed.erase(it); }
        s_s7486_plant = 0; std::fprintf(stderr, "[s7486] plant %s try=%d blk=%08X\n", gone ? "LOST" : "TIMEOUT", s_s7486_ptries, s_s7486_pblk); }
    if (s_s7486_plant != 0 || now - s_s7475_t0 < plant_s || s_s7486_ptries >= 30) return;
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    if (s_s7486_ctlblk && s_s7475_live.count(s_s7486_ctlblk) && !s_s7480_freed.count(s_s7486_ctlblk)) {  /* preferred: a live block a host read just covered */
        const uint32_t lb = s_s7486_ctlblk, n = s_s7475_live[lb].req; bool ov = false;
        { auto it = s_s7480_freed.upper_bound(lb + n - 1u); if (it != s_s7480_freed.begin()) { --it; ov = it->first + it->second.n > lb; } }
        if (!ov && n) { ++s_s7486_ptries; s7480_add(lb, n, now, 3); s_s7486_plant = 1; s_s7486_ptime = now; s_s7486_pblk = lb; s_s7486_ctlblk = 0;
            std::fprintf(stderr, "[s7486] plant SET blk=%08X size=%X via=ctl(%s) try=%d t=%.1f\n", lb, n, k_s7486_kind[s_s7486_ctlkind], s_s7486_ptries, now - s_s7475_t0); return; } }
    for (unsigned i = 0; i < 16; ++i) { const uint32_t a = s_s7486_recent[(s_s7486_ptries + i) & 15u].load(std::memory_order_relaxed); if (!a || s_s7480_freed.count(a)) continue;
        { auto it = s_s7480_freed.upper_bound(a + 7u); if (it != s_s7480_freed.begin()) { --it; if (it->first + it->second.n > a) continue; } }  /* fallback: the exact 8 bytes a recent gfx DMA / texture load read */
        ++s_s7486_ptries; s7480_add(a, 8u, now, 3); s_s7486_plant = 1; s_s7486_ptime = now; s_s7486_pblk = a;
        std::fprintf(stderr, "[s7486] plant SET blk=%08X size=8 via=recent try=%d t=%.1f\n", a, s_s7486_ptries, now - s_s7475_t0); return; } }
static void s7486_sum(double now) {
    if (!g_rs64_s7486_on) return;
    std::string b; uint64_t F = 0, R = 0, wF = 0, wR = 0;
    for (int k = 0; k < (g_rs64_s7489_on ? 9 : 6); ++k) { if (k == 4) continue; char t[320]; if (k >= 6) { wF += s_s7486_loc[k][1]; wR += s_s7486_loc[k][3]; } else { F += s_s7486_loc[k][1]; R += s_s7486_loc[k][3]; }
        snprintf(t, sizeof t, " %s=%llu/%llu/%llu/%llu:U%llu,F%llu,N%llu,R%llu,S%llu,ctl%llu,stale%llu", k_s7486_kind[k], (unsigned long long)s_s7486_rng[k], (unsigned long long)s_s7486_bytes[k], (unsigned long long)s_s7486_mark[k], (unsigned long long)s_s7486_rec[k],
                 (unsigned long long)s_s7486_loc[k][0], (unsigned long long)s_s7486_loc[k][1], (unsigned long long)s_s7486_loc[k][2], (unsigned long long)s_s7486_loc[k][3], (unsigned long long)s_s7486_loc[k][4], (unsigned long long)s_s7486_ctl[k], (unsigned long long)s_s7486_stale[k]); b += t; }
    std::fprintf(stderr, "[s7486] sum t=%.1f host_F=%llu host_Urec=%llu plant=%d tries=%d kinds(rng/bytes/marked/recs:class)%s\n", now - s_s7475_t0, (unsigned long long)F, (unsigned long long)R, s_s7486_plant, s_s7486_ptries, b.c_str());
    if (g_rs64_s7489_on) std::fprintf(stderr, "[s7489] sum t=%.1f host_wF=%llu host_wUrec=%llu wplant=%d sp_wr_gfx_ctl=%llu sp_wr_aud_ctl=%llu pi_dma_ctl=%llu sp_wr_gfx_rng=%llu sp_wr_aud_rng=%llu pi_dma_rng=%llu marked=%llu/%llu/%llu\n", now - s_s7475_t0,
        (unsigned long long)wF, (unsigned long long)wR, s_s7489_wplant, (unsigned long long)s_s7486_ctl[6], (unsigned long long)s_s7486_ctl[7], (unsigned long long)s_s7486_ctl[8],
        (unsigned long long)s_s7486_rng[6], (unsigned long long)s_s7486_rng[7], (unsigned long long)s_s7486_rng[8], (unsigned long long)s_s7486_mark[6], (unsigned long long)s_s7486_mark[7], (unsigned long long)s_s7486_mark[8]); }
extern "C" void rs64_s7490_sum(double now);  /* s7490 class EO, defined at zmemcpy */
extern "C" void rs64_s7491_sum(double now);  /* s7491 class EP, defined before zmemcpy */
static void s7480_sum(double now) {
    if (!s7480_on()) return;
    rs64_s7490_sum(now);
    rs64_s7491_sum(now);
    s7486_sum(now);
    if (g_rs64_s7484_on) std::fprintf(stderr, "[s7484] sum t=%.1f hits=%llu recs=%llu loc_U=%llu loc_F=%llu loc_N=%llu loc_Urec=%llu loc_S=%llu pcs=%zu slack=%llu slack_pcs=%zu internal=%llu p1=%llu retired=%llu ctl=%llu plant=%d tries=%d\n", now - s_s7475_t0,
        (unsigned long long)s_s7484_hits, (unsigned long long)s_s7484_recs, (unsigned long long)s_s7484_loc[0], (unsigned long long)s_s7484_loc[1], (unsigned long long)s_s7484_loc[2], (unsigned long long)s_s7484_loc[3], (unsigned long long)s_s7484_loc[4],
        s_s7484_pcs.size(), (unsigned long long)s_s7484_slack, s_s7484_spcs.size(), (unsigned long long)s_s7484_intl, (unsigned long long)s_s7484_p1, (unsigned long long)s_s7484_retired, (unsigned long long)s_s7484_ctl, s_s7484_plant, s_s7484_ptries);
    if (g_rs64_s7487_on) { uint64_t ex = 0; int es = 0, hs = 0; uint64_t sm = 0, hp = 0;
        for (int i = 0; i < 1024; ++i) if (g_rs64_s7487_cnt[i]) { ex += g_rs64_s7487_cnt[i]; ++es; }
        for (auto& kv : s_s7487_site) { sm += kv.second.samp; hp += kv.second.heap; if (kv.second.heap) ++hs; }
        std::fprintf(stderr, "[s7487] sum t=%.1f exec=%llu exec_sites=%d samples=%llu heap_samples=%llu heap_sites=%d marked=%llu hits=%llu lwl_U=%llu lwl_F=%llu lwl_N=%llu lwl_Urec=%llu lwl_S=%llu ctl=%d ctl_tries=%d\n", now - s_s7475_t0,
            (unsigned long long)ex, es, (unsigned long long)sm, (unsigned long long)hp, hs, (unsigned long long)s_s7487_marked, (unsigned long long)s_s7487_hits,
            (unsigned long long)s_s7487_loc[0], (unsigned long long)s_s7487_loc[1], (unsigned long long)s_s7487_loc[2], (unsigned long long)s_s7487_loc[3], (unsigned long long)s_s7487_loc[4], s_s7487_ctl, s_s7487_ctries); }
    if (g_rs64_s7488_on) { uint64_t ex = 0; int es = 0, hs = 0; uint64_t sm = 0, hp = 0;
        for (int i = 0; i < 1024; ++i) if (g_rs64_s7488_cnt[i]) { ex += g_rs64_s7488_cnt[i]; ++es; }
        for (auto& kv : s_s7488_site) { sm += kv.second.samp; hp += kv.second.heap; if (kv.second.heap) ++hs; }
        std::fprintf(stderr, "[s7488] sum t=%.1f exec=%llu exec_sites=%d samples=%llu heap_samples=%llu heap_sites=%d marked=%llu hits=%llu slack=%llu ust_U=%llu ust_F=%llu ust_N=%llu ust_Urec=%llu ust_S=%llu ctl=%d ctl_tries=%d\n", now - s_s7475_t0,
            (unsigned long long)ex, es, (unsigned long long)sm, (unsigned long long)hp, hs, (unsigned long long)s_s7488_marked, (unsigned long long)s_s7488_hits, (unsigned long long)s_s7488_slack,
            (unsigned long long)s_s7488_loc[0], (unsigned long long)s_s7488_loc[1], (unsigned long long)s_s7488_loc[2], (unsigned long long)s_s7488_loc[3], (unsigned long long)s_s7488_loc[4], s_s7488_ctl, s_s7488_ctries); }
    { /* locator control: on the live main arena chain, a free block MUST classify F and a used one U (each logged once) */
      static int fok = 0, uok = 0; volatile uint8_t* r = g_recomp_rdram_for_wp_raw; const uint32_t h0 = r ? s7472_rd(r, 0x8010FF18u) : 0u;
      if (r && (!fok || !uok) && h0 >= 0x80000000u && h0 < rs64_ram_top) { uint32_t b = h0;
        for (int g = 0; g < 400000; ++g) { const uint32_t w0 = s7472_rd(r, b), sz = s7472_rd(r, b + 4u), fl = w0 >> 16;
            if ((fl & 8u) || (fl != 1u && fl != 2u && fl != 6u) || (sz & 0xFu) || !sz || b + 0x10u + sz >= rs64_ram_top) break;
            uint32_t lb, ls, lf, la; const char k = s7480_locate(r, b + 0x10u + (sz >> 1), &lb, &ls, &lf, &la);
            if (fl == 1u && !fok) { fok = 1; std::fprintf(stderr, "[s7480] locate-ctl free blk=%08X sz=%X got=%c %s\n", b + 0x10u, sz, k, k == 'F' ? "PASS" : "FAIL"); }
            if (fl == 2u && !uok) { uok = 1; std::fprintf(stderr, "[s7480] locate-ctl used blk=%08X sz=%X got=%c %s\n", b + 0x10u, sz, k, k == 'U' ? "PASS" : "FAIL"); }
            if (fok && uok) break; b += 0x10u + sz; } } } std::string in; for (auto& kv : s_s7480_internal) { char b[96]; snprintf(b, sizeof b, " %s:%llu", kv.first.c_str(), (unsigned long long)kv.second); in += b; }
    uint64_t bytes = 0; for (auto& kv : s_s7480_freed) bytes += kv.second.n;
    std::fprintf(stderr, "[s7480] sum t=%.1f loc_U=%llu loc_F=%llu loc_N=%llu loc_Urec=%llu loc_S=%llu task_out=%08X top=%08X frees=%llu skip=%llu freed_recs=%zu freed_bytes=%llu trims=%llu hits=%llu pcs=%zu plant=%d tries=%d internal={%s }\n", now - s_s7475_t0, (unsigned long long)s_s7480_loc[0], (unsigned long long)s_s7480_loc[1], (unsigned long long)s_s7480_loc[2], (unsigned long long)s_s7480_loc[3], (unsigned long long)s_s7480_loc[4], (unsigned)g_rs64_s7481_task_out, rs64_ram_top,
                 (unsigned long long)s_s7480_frees, (unsigned long long)s_s7480_skip, s_s7480_freed.size(), (unsigned long long)bytes, (unsigned long long)s_s7480_trims,
                 (unsigned long long)s_s7480_hits, s_s7480_pcs.size(), s_s7480_plant, s_s7480_ptries, in.c_str()); }
}
/* s7482: live s6202 wide frame-pool span, published by the partitionFramebufferMemory tail patch (tools/apply_s6031_far.py
   apply_s7482_reserve; 0/0 when no retarget is live). Every rs_malloc exit checks [ptr, ptr+req) against it: an overlap means
   the allocator handed out memory the DL builders are writing as the frame pool (H-collide). ROGUESQ_S7482_CTL=1 = positive
   control: the first malloc seen while a span is live is reported as a CONTROL line (not counted). Always on; cost = 2 loads. */
extern "C" { volatile uint32_t g_rs64_s7482_base = 0, g_rs64_s7482_ec = 0; }
static uint64_t s_s7482_live_mallocs = 0, s_s7482_collide = 0;
static void s7777_malloc(uint32_t ptr); static void s7777_free(uint32_t ptr);  /* s7777, defined below */
static void s7482_check(uint32_t req, uint32_t ptr, uint32_t ra) {
    const uint32_t b = g_rs64_s7482_base, e = g_rs64_s7482_ec; if (!b || !ptr || !req) return;
    static const bool ctl = [] { const char* v = std::getenv("ROGUESQ_S7482_CTL"); return v && v[0] && v[0] != '0'; }();
    static int nlog = 0; const uint64_t k = s_s7482_live_mallocs++;
    const bool hit = ptr < e && ptr + req > b, fake = ctl && k == 0;
    if (hit) ++s_s7482_collide;
    if ((hit || fake) && nlog < 24) { ++nlog; volatile uint8_t* r = g_recomp_rdram_for_wp_raw;
        std::fprintf(stderr, "[s7482] pool-collide%s ptr=%08X req=%X base=%08X ec=%08X e8=%08X ra=%08X live_mallocs=%llu collide=%llu\n", hit ? "" : " CONTROL", ptr, req, b, e,
                     r ? s7472_rd(r, 0x801163E8u) : 0u, ra, (unsigned long long)k + 1, (unsigned long long)s_s7482_collide); std::fflush(stderr); }
    if ((k & 0xFFFu) == 0xFFFu) { std::fprintf(stderr, "[s7482] sum live_mallocs=%llu collide=%llu span=%08X..%08X\n", (unsigned long long)k + 1, (unsigned long long)s_s7482_collide, b, e); std::fflush(stderr); } }
static void s7475_malloc(uint32_t req, uint32_t ptr, uint32_t ra, void* hpc) {
    s7777_malloc(ptr);  /* s7777 dangling-global class */
    s7482_check(req, ptr, ra);
    if (!s7475_on()) return;
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    const double now = s7325_now();
    std::lock_guard<std::mutex> lk(s_s7475_mu);
    if (s_s7475_t0 == 0) { s_s7475_t0 = now; g_rs64_s7475_bm = (unsigned char*)std::calloc(0x1800000u >> 3, 1); if (g_rs64_s7475_bm) g_rs64_s7475_bm[(0x8011A890u - 0x80000000u) >> 3] |= (unsigned char)(1u << (0x8011A890u & 7u)); std::fprintf(stderr, "[s7475] canary armed top=%08X bitmap=%d\n", rs64_ram_top, g_rs64_s7475_bm != nullptr);
        { const char* e = std::getenv("ROGUESQ_S7484_UAFLOAD"); if (g_rs64_s7475_bm && e && e[0] && e[0] != '0' && s7480_on()) { g_rs64_s7484_on = 1; std::fprintf(stderr, "[s7484] load watch armed\n");
              const char* e7 = std::getenv("ROGUESQ_S7487_LWLWATCH"); if (e7 && e7[0] && e7[0] != '0') { g_rs64_s7487_on = 1; std::fprintf(stderr, "[s7487] lwl/lwr watch armed\n"); } } }
        { const char* e = std::getenv("ROGUESQ_S7488_USTOREWATCH"); if (g_rs64_s7475_bm && e && e[0] && e[0] != '0' && s7480_on()) { g_rs64_s7488_on = 1; std::fprintf(stderr, "[s7488] swl/swr watch armed\n"); } }
        { const char* e = std::getenv("ROGUESQ_S7486_HOSTUAF"); if (g_rs64_s7475_bm && e && e[0] && e[0] != '0' && s7480_on()) { g_rs64_s7486_on = 1; std::fprintf(stderr, "[s7486] host-read watch armed\n");
              const char* e9 = std::getenv("ROGUESQ_S7489_HOSTWRITE"); if (e9 && e9[0] && e9[0] != '0') { g_rs64_s7489_on = 1; const char* p9 = std::getenv("ROGUESQ_S7489_WPLANT"); s_s7489_wplant = p9 && p9[0] && p9[0] != '0';
                  std::fprintf(stderr, "[s7489] host-write watch armed wplant=%d\n", s_s7489_wplant); } } } }
    if (ptr && ptr >= 0x80000010u && ptr < rs64_ram_top && req) {
        const uint32_t w0 = s7472_rd(r, ptr - 0x10u), sz = s7472_rd(r, ptr - 0x0Cu), fl = w0 >> 16;
        /* drop every record overlapping [ptr-0x10, ptr+sz) */
        const uint32_t lo = ptr - 0x10u, hi = ptr + ((fl == 2u || fl == 6u) && sz >= req ? sz : req);
        auto it = s_s7475_live.upper_bound(lo); if (it != s_s7475_live.begin()) --it;
        while (it != s_s7475_live.end() && it->first - 0x10u < hi) {
            if (it->first + it->second.sz > lo) { ++s_s7475_overlap; if (s_s7475_plant == 1 && it->first == s_s7475_pblk) { s_s7475_plant = 2; std::fprintf(stderr, "[s7475] plant LOST blk=%08X (overlap)\n", it->first); } s7475_mark(it->first, it->second, false); it = s_s7475_live.erase(it); }
            else ++it; }
        if (!((fl == 2u || fl == 6u) && sz >= req && !(sz & 0xFu) && ptr + sz <= rs64_ram_top)) {
            if (s_s7475_hdrbad++ < 8) std::fprintf(stderr, "[s7475] hdr-mismatch ptr=%08X req=%X w0=%08X size=%08X ra=%08X\n", ptr, req, w0, sz, ra); }
        else if (sz == req) ++s_s7475_noslack;
        else {
            /* ROGUESQ_S7475_SEL=<lo>-<hi>: canary only slack blocks with ordinal in [lo, hi] (bisect a slack reader); ROGUESQ_S7475_LOGREC=<n>: log the first n records */
            static uint64_t ord = 0; const uint64_t k = ord++;
            static const std::pair<uint64_t, uint64_t> sel = [] { const char* e = std::getenv("ROGUESQ_S7475_SEL"); uint64_t a = 0, b = ~0ull;
                if (e && *e) { char* q; a = std::strtoull(e, &q, 0); b = (*q == '-') ? std::strtoull(q + 1, nullptr, 0) : a; } return std::make_pair(a, b); }();
            static const long logrec = [] { const char* e = std::getenv("ROGUESQ_S7475_LOGREC"); return e ? std::atol(e) : 0L; }();
            if ((long)k < logrec) std::fprintf(stderr, "[s7475] rec #%llu blk=%08X req=%X size=%X alloc=%s t=%.2f%s\n", (unsigned long long)k, ptr, req, sz, s7475_sym(hpc).c_str(), now - s_s7475_t0, (k >= sel.first && k <= sel.second) ? "" : " unsel");
            if (k >= sel.first && k <= sel.second) {
                for (uint32_t o = req; o < sz; ++o) s7475_wb(r, ptr + o, s7475_fill()); s_s7475_live[ptr] = S7475R{req, sz, ra, now, hpc, {}, 0}; if (s7478_bt_on()) s_s7475_live[ptr].nbt = backtrace(s_s7475_live[ptr].bt, 8); s7475_mark(ptr, s_s7475_live[ptr], true); ++s_s7475_rec; } }
    }
    s7480_malloc(req, ptr, now);
    s7475_tick(r, now); }
extern "C" int rs64_s7484_load(uint32_t pc, uint32_t a, int w, const char* fn);
extern "C" int rs64_s7487_lwx(uint32_t pc, int idx, uint32_t a, int w, const char* fn, int marked) {
    if (marked) { { std::lock_guard<std::mutex> lk(s_s7475_mu); ++s_s7487_marked; } t_s7487_lwx = 1; const int r = rs64_s7484_load(pc, a, w, fn); t_s7487_lwx = 0; return r; }
    static const double ctl_s = [] { const char* e = std::getenv("ROGUESQ_S7487_LWLCTL"); if (!e || !*e || *e == '0') return -1.0; double v = std::atof(e); return v <= 1.0 ? 150.0 : v; }();
    std::lock_guard<std::mutex> lk(s_s7475_mu); const double now = s7325_now();
    S7487S& s = s_s7487_site[idx]; if (!s.samp) { s.pc = pc; s.a0 = a; s.fn = fn ? fn : "?"; } ++s.samp;
    uint32_t blk = 0, req = 0; { auto it = s_s7475_live.upper_bound(a); if (it != s_s7475_live.begin()) { --it; if (a < it->first + it->second.req) { blk = it->first; req = it->second.req; } } }
    if (blk) { if (!s.heap) { s.ah = a; std::fprintf(stderr, "[s7487] heap-site idx=%d pc=%08X fn=%s a=%08X blk=%08X req=%X t=%.1f\n", idx, pc, s.fn.c_str(), a, blk, req, now - s_s7475_t0); } ++s.heap; }
    if (ctl_s >= 0) {
        if (s_s7487_ctl == 1 && (now - s_s7487_ctime > 10.0 || !s_s7480_freed.count(s_s7487_cblk) || s_s7480_freed[s_s7487_cblk].plant != 4)) {
            auto it = s_s7480_freed.find(s_s7487_cblk); if (it != s_s7480_freed.end() && it->second.plant == 4) { s7480_range(it->first, it->first + it->second.n, false); s_s7480_freed.erase(it); }
            s_s7487_ctl = 0; std::fprintf(stderr, "[s7487] lwl-ctl TIMEOUT/LOST try=%d\n", s_s7487_ctries); }
        if (s_s7487_ctl == 0 && blk && s_s7487_ctries < 60 && now - s_s7475_t0 >= ctl_s && !s_s7480_freed.count(blk)) {
            ++s_s7487_ctries; s7480_add(blk, req, now, 4); s_s7487_ctl = 1; s_s7487_ctime = now; s_s7487_cblk = blk;
            std::fprintf(stderr, "[s7487] lwl-ctl SET blk=%08X req=%X by pc=%08X fn=%s a=%08X try=%d t=%.1f\n", blk, req, pc, s.fn.c_str(), a, s_s7487_ctries, now - s_s7475_t0); } }
    return 0; }
extern "C" int rs64_s7475_store(uint32_t pc, uint32_t a, int w, const char* fn);
extern "C" int rs64_s7488_ust(uint32_t pc, int idx, uint32_t a, int w, const char* fn, int marked) {
    if (marked) { { std::lock_guard<std::mutex> lk(s_s7475_mu); ++s_s7488_marked; } t_s7488_ust = 1; const int r = rs64_s7475_store(pc, a, w, fn); t_s7488_ust = 0; return r; }
    static const double ctl_s = [] { const char* e = std::getenv("ROGUESQ_S7488_USTCTL"); if (!e || !*e || *e == '0') return -1.0; double v = std::atof(e); return v <= 1.0 ? 150.0 : v; }();
    std::lock_guard<std::mutex> lk(s_s7475_mu); const double now = s7325_now();
    S7488S& s = s_s7488_site[idx]; if (!s.samp) { s.pc = pc; s.fn = fn ? fn : "?"; } ++s.samp;
    uint32_t blk = 0, req = 0; { auto it = s_s7475_live.upper_bound(a); if (it != s_s7475_live.begin()) { --it; if (a < it->first + it->second.req) { blk = it->first; req = it->second.req; } } }
    if (blk) { if (!s.heap) std::fprintf(stderr, "[s7488] heap-site idx=%d pc=%08X fn=%s a=%08X w=%d blk=%08X req=%X t=%.1f\n", idx, pc, s.fn.c_str(), a, w, blk, req, now - s_s7475_t0); ++s.heap; }
    if (ctl_s >= 0) {
        if (s_s7488_ctl == 1 && (now - s_s7488_ctime > 10.0 || !s_s7480_freed.count(s_s7488_cblk) || s_s7480_freed[s_s7488_cblk].plant != 5)) {
            auto it = s_s7480_freed.find(s_s7488_cblk); if (it != s_s7480_freed.end() && it->second.plant == 5) { s7480_range(it->first, it->first + it->second.n, false); s_s7480_freed.erase(it); }
            s_s7488_ctl = 0; std::fprintf(stderr, "[s7488] ust-ctl TIMEOUT/LOST try=%d\n", s_s7488_ctries); }
        if (s_s7488_ctl == 0 && blk && s_s7488_ctries < 60 && now - s_s7475_t0 >= ctl_s && !s_s7480_freed.count(blk)) {
            ++s_s7488_ctries; s7480_add(blk, req, now, 5); s_s7488_ctl = 1; s_s7488_ctime = now; s_s7488_cblk = blk;
            std::fprintf(stderr, "[s7488] ust-ctl SET blk=%08X req=%X by pc=%08X fn=%s a=%08X try=%d t=%.1f\n", blk, req, pc, s.fn.c_str(), a, s_s7488_ctries, now - s_s7475_t0); } }
    return 0; }
/* s7518 class FO second line: CPU loads that a VR4300 could serve from a stale D-cache line (ROGUESQ_S7518_STALEWATCH=1, needs
   ROGUESQ_LOG_CACHE_SHAPE=1). Per 16-byte line a residency state, driven by osInvalDCache, PI cart->RDRAM DMA and the guest loads
   the s7484 load watch sees (every invalidated or DMA'd line is marked in its bitmap, never unmarked):
     C unknown (may be resident)   N invalidated, not re-cached   R resident, fresh   F DMA'd while uncached (fresh)   S DMA'd while
     possibly resident (a cached copy is stale).
     inv -> N (n >= 8192: every line, ROM index writeback-invalidate path).  DMA: N/F -> F, C/R/S -> S.
     load: N/F -> R (counted fresh_load when F), R stays, S -> STALE row (hardware could return the pre-DMA bytes), C ignored.
   Conservative (no eviction modelled, an 8 KB cache evicts sooner) and loads only: stores (write-allocate) and lwl/lwr are not seen.
   Same-run controls: fresh_load > 0 (the CPU reads DMA'd data), and ROGUESQ_CACHE_SHAPE_CTL drops one invalidate-after-DMA, which
   must turn the next CPU read of that buffer into a STALE row. Measurement only. */
static std::vector<uint8_t> s_s7518_ln;
static std::atomic<uint64_t> s_s7518_stale{0}, s_s7518_fresh{0}, s_s7518_res{0}, s_s7518_dmaS{0}, s_s7518_dmaF{0};
static std::mutex s_s7518_mu; static std::map<uint32_t, std::pair<uint64_t, uint32_t>> s_s7518_pcs;
extern "C" void rs64_s7518_summary(void);
static void s7519_ev(int op, uint32_t lo, uint32_t hi, uint32_t a, uint32_t n); extern "C" void rs64_s7519_summary(void);  /* s7519 FP, below */
static bool s7518_watch() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7518_STALEWATCH"); return e && e[0] && e[0] != '0'; }(); return on; }
enum { S7518_C = 0, S7518_N, S7518_R, S7518_F, S7518_S };
static void s7518_markln(uint32_t l) { const uint32_t b = l * 16u; if (b + 16u > 0x17FFFF0u) return; g_rs64_s7475_bm[b >> 3] = 0xFF; g_rs64_s7475_bm[(b >> 3) + 1] = 0xFF; }
extern "C" void rs64_s7518_event(int op, uint32_t a, uint32_t n) {  /* op 0 inv, 1 dma0 */
    if (!s7518_watch()) return;
    /* s7560 AQ H-race fix: s_s7518_ln is also read/written by s7519_store / rs64_s7519_wbev, which run on host threads too
       (rs64_s7491_hst -> rs64_s7475_store from RT64 writeback / message-queue writers); every s_s7518_ln access now holds s_s7518_mu.
       s7519_ev locks s_s7518_mu itself, so it is called outside these blocks (it never reads s_s7518_ln). */
    { std::lock_guard<std::mutex> lk(s_s7518_mu);
      if (s_s7518_ln.empty()) { s_s7518_ln.assign(0x1800000u / 16u, S7518_C);
        if (!g_rs64_s7475_bm) g_rs64_s7475_bm = (unsigned char*)std::calloc(0x1800000u >> 3, 1);
        g_rs64_s7484_on = g_rs64_s7475_bm ? 1 : 0; std::fprintf(stderr, "[s7518] stale watch armed bm=%d\n", g_rs64_s7484_on); } }
    if (!g_rs64_s7484_on || !n) return;
    const uint32_t o = (a & 0x1FFFFFFFu); if (o >= 0x1800000u) return;
    const uint32_t lo = o / 16u, hi = std::min<uint32_t>((o + n - 1u) / 16u, 0x1800000u / 16u - 1u);
    if (op == 0) {
        if (n >= 8192) { s7519_ev(3, 0, 0, a, n); std::lock_guard<std::mutex> lk(s_s7518_mu); for (auto& v : s_s7518_ln) v = S7518_N; return; }
        s7519_ev(0, lo, hi, a, n);
        { std::lock_guard<std::mutex> lk(s_s7518_mu); for (uint32_t l = lo; l <= hi; l++) { s_s7518_ln[l] = S7518_N; s7518_markln(l); } }
        return; }
    s7519_ev(1, lo, hi, a, n);
    { std::lock_guard<std::mutex> lk(s_s7518_mu);
      for (uint32_t l = lo; l <= hi; l++) { uint8_t& v = s_s7518_ln[l];
        if (v == S7518_N || v == S7518_F) { v = S7518_F; ++s_s7518_dmaF; } else { v = S7518_S; ++s_s7518_dmaS; } s7518_markln(l); } }
    static uint64_t nd = 0; if ((++nd & 2047u) == 0) rs64_s7518_summary();
}
static int s7518_load(uint32_t pc, uint32_t a, int w, const char* fn) {
    const uint32_t o = a - 0x80000000u; if (o >= 0x1800000u) return 0;
    std::lock_guard<std::mutex> lk(s_s7518_mu); if (s_s7518_ln.empty()) return 0;  /* s7560: whole walk under s_s7518_mu */
    for (uint32_t l = o / 16u; l <= (o + (uint32_t)w - 1u) / 16u; l++) { uint8_t& v = s_s7518_ln[l];
        if (v == S7518_S) { const uint64_t k = ++s_s7518_stale; v = S7518_R; auto& e = s_s7518_pcs[pc];
            if (!e.first) { e.second = a; std::fprintf(stderr, "[s7518-load] STALE pc=%08X fn=%s a=%08X w=%d k=%llu\n", pc, fn ? fn : "?", a, w, (unsigned long long)k); }
            ++e.first; }
        else if (v == S7518_F) { const uint64_t k = ++s_s7518_fresh; v = S7518_R;
            if ((k & (k - 1)) == 0) std::fprintf(stderr, "[s7518-load] fresh pc=%08X fn=%s a=%08X k=%llu\n", pc, fn ? fn : "?", a, (unsigned long long)k); }
        else if (v == S7518_N) { v = S7518_R; ++s_s7518_res; } }
    return 1;
}
extern "C" void rs64_s7518_summary(void) {
    if (!s7518_watch()) return;
    size_t npcs; { std::lock_guard<std::mutex> lk(s_s7518_mu); npcs = s_s7518_pcs.size(); }
    std::fprintf(stderr, "[s7518-sum] stale_load=%llu fresh_load=%llu inv_then_load=%llu dma_lines_fresh=%llu dma_lines_over_resident=%llu stale_pcs=%zu\n",
        (unsigned long long)s_s7518_stale.load(), (unsigned long long)s_s7518_fresh.load(), (unsigned long long)s_s7518_res.load(),
        (unsigned long long)s_s7518_dmaF.load(), (unsigned long long)s_s7518_dmaS.load(), npcs);
    rs64_s7519_summary(); }
/* s7519 class FP: the STORE side of FO. The VR4300 D-cache is write-back + write-allocate: a guest store leaves a dirty 16-byte line
   that hardware writes back only on a writeback/eviction/index op, while the port writes RAM at once. Per tracked line (the s7518
   bitmap: every invalidated, written-back or DMA'd line) a dirty state:
     0 clean   1 D dirty (cache = RAM + stores)   2 X dirty over a DMA (RAM holds the DMA bytes, the cache holds pre-DMA + stores:
     port = DMA data, hardware = whatever wins later)   3 L lost (an interior Hit_Invalidate discarded a dirty line: hardware RAM lacks
     the store, port has it).
   store: 0/1 -> 1 (on residency S: -> 2, counted st_on_S, conservative), 2 stays, 3 stays.  wb / wball / index inv (n >= 8192) /
   osInvalDCache edge line (Hit_Writeback_Invalidate): 1 -> 0 clean; 2 -> LIVE row kind=wb (hardware writes the cached line over the
   DMA bytes). osInvalDCache interior line (Hit_Invalidate): 1 -> 3 DISCARD row; 2 -> 0 resolved dead (dd_inv_ok, DMA wins as in the
   port). DMA cart->RDRAM: 1 -> 2 (DMA_OVER_DIRTY row), 3 -> 0 (lost bytes overwritten, dead). load: 2 -> LIVE row kind=load
   (hardware returns the cached bytes), 3 -> LIVE row kind=lost. Still 2/3 at the end = pending (an eviction would resolve it).
   Ctl ROGUESQ_CACHE_SHAPE_CTL_WB=<k>: the first osWritebackDCache at or after the k-th that starts at a past DMA address (a slot)
   and covers a dirty tracked line is dropped
   (logged [cache-ctl] dropped wb ... dirty=N), so its lines must reach a DMA_OVER_DIRTY row if the next DMA covers them.
   Gaps: stores to a line before it is first marked are unseen; no eviction model. Measurement only. */
static std::vector<uint8_t> s_s7519_dt; static std::vector<uint32_t> s_s7519_pc; static std::set<uint32_t> s_s7519_set;
static std::map<std::pair<int, uint32_t>, uint64_t> s_s7519_rows;
static uint64_t s_s7519_n[12];  /* 0 st_seen 1 st_on_S 2 wb_clean 3 dma_over_dirty 4 dd_inv_ok 5 live_wb 6 live_load 7 discard 8 live_lost 9 lost_dma_ok 10 ctl_lines 11 st_ctl_wb */
static const char* const s7519_kn[] = {"st_seen","st_on_S","wb_clean","dma_over_dirty","dd_inv_ok","live_wb","live_load","discard","live_lost","lost_dma_ok","ctl_lines","ctl_wb_hit"};
static std::set<uint32_t> s_s7519_ctlln;  /* lines whose wb the control dropped */
static std::set<uint32_t> s_s7519_dmaA;  /* start addresses of past cart->RDRAM DMAs (ctl targets a wb of a DMA slot) */
static void s7519_init() { if (s_s7519_dt.empty()) { s_s7519_dt.assign(0x1800000u / 16u, 0); s_s7519_pc.assign(0x1800000u / 16u, 0); } }
static void s7519_row(int k, uint32_t l, uint32_t pc, const char* fn) {
    ++s_s7519_n[k]; const bool ctl = s_s7519_ctlln.count(l) != 0; auto& c = s_s7519_rows[{k, s_s7519_pc[l]}];
    if (c++ < 2 || ctl) { static int nl = 0; if (nl++ < 400 || ctl) std::fprintf(stderr, "[s7519] %s line=%08X st_pc=%08X at_pc=%08X fn=%s ctl=%d n=%llu\n", s7519_kn[k],
        0x80000000u + l * 16u, s_s7519_pc[l], pc, fn ? fn : "?", ctl ? 1 : 0, (unsigned long long)c); } }
static void s7519_wbline(uint32_t l, uint32_t pc) {  /* caller holds s_s7518_mu; l is dirty */
    uint8_t& d = s_s7519_dt[l]; if (d == 1) { d = 0; ++s_s7519_n[2]; s_s7519_set.erase(l); } else if (d == 2) { s7519_row(5, l, pc, "writeback"); d = 0; s_s7519_set.erase(l); } }
static void s7519_ev(int op, uint32_t lo, uint32_t hi, uint32_t a, uint32_t n) {  /* op 0 inv, 1 dma0, 2 wb, 3 wball / index */
    std::lock_guard<std::mutex> lk(s_s7518_mu); s7519_init();
    if (op == 3) { std::vector<uint32_t> v(s_s7519_set.begin(), s_s7519_set.end()); for (uint32_t l : v) s7519_wbline(l, 0); return; }
    auto it = s_s7519_set.lower_bound(lo);
    std::vector<uint32_t> v; for (; it != s_s7519_set.end() && *it <= hi; ++it) v.push_back(*it);
    if (op == 1) { if (s_s7519_dmaA.size() < 65536) s_s7519_dmaA.insert(a & 0x1FFFFFFFu);
        for (uint32_t l = lo; l <= hi; l++) { uint8_t& d = s_s7519_dt[l];
            if (d == 1) { d = 2; s7519_row(3, l, 0, "dma"); } else if (d == 3) { d = 0; ++s_s7519_n[9]; s_s7519_set.erase(l); } } return; }
    if (op == 2) { for (uint32_t l : v) s7519_wbline(l, 0); return; }
    const bool e0 = (a & 15u) != 0, e1 = ((a + n) & 15u) != 0;
    for (uint32_t l : v) { if ((l == lo && e0) || (l == hi && e1)) { s7519_wbline(l, 0); continue; }
        uint8_t& d = s_s7519_dt[l]; if (d == 1) { d = 3; s7519_row(7, l, 0, "inv"); } else if (d == 2) { d = 0; ++s_s7519_n[4]; s_s7519_set.erase(l); } }
}
extern "C" int rs64_s7519_wbev(uint32_t a, uint32_t n, int all) {  /* from ultra_translation.cpp; returns 1 = ctl dropped this wb */
    if (!s7518_watch() || !g_rs64_s7484_on) return 0;
    { std::lock_guard<std::mutex> lk(s_s7518_mu); if (s_s7518_ln.empty()) return 0; }  /* s7560: assigned once, never cleared */
    if (all || n >= 8192) { s7519_ev(3, 0, 0, a, n); return 0; }
    if (!n) return 0;
    const uint32_t o = (a & 0x1FFFFFFFu); if (o >= 0x1800000u) return 0;
    const uint32_t lo = o / 16u, hi = std::min<uint32_t>((o + n - 1u) / 16u, 0x1800000u / 16u - 1u);
    static const long ctl = [] { const char* e = std::getenv("ROGUESQ_CACHE_SHAPE_CTL_WB"); return e ? std::strtol(e, nullptr, 0) : 0L; }();
    static long k = 0; static bool done = false; ++k;
    if (ctl > 0 && !done && k >= ctl) { std::lock_guard<std::mutex> lk(s_s7518_mu); s7519_init(); uint32_t nd = 0; if (!s_s7519_dmaA.count(o)) goto noctl;
        for (auto it = s_s7519_set.lower_bound(lo); it != s_s7519_set.end() && *it <= hi; ++it) if (s_s7519_dt[*it] == 1) { ++nd; s_s7519_ctlln.insert(*it); }
        if (nd) { done = true; s_s7519_n[10] = nd; std::fprintf(stderr, "[cache-ctl] dropped wb k=%ld a=%08X n=%X dirty=%u\n", k, a, n, nd); return 1; }
        s_s7519_ctlln.clear(); }
    noctl:
    { std::lock_guard<std::mutex> lk(s_s7518_mu); for (uint32_t l = lo; l <= hi; l++) { s7518_markln(l); if (s_s7518_ln[l] == S7518_C) s_s7518_ln[l] = S7518_R; } }
    s7519_ev(2, lo, hi, a, n); return 0; }
static int s7519_store(uint32_t pc, uint32_t a, int w, const char* fn) {
    const uint32_t o = a - 0x80000000u; if (o >= 0x1800000u) return 1;
    std::lock_guard<std::mutex> lk(s_s7518_mu); if (s_s7518_ln.empty()) return 1; s7519_init();
    for (uint32_t l = o / 16u; l <= (o + (uint32_t)w - 1u) / 16u; l++) { uint8_t& v = s_s7518_ln[l];
        ++s_s7519_n[0]; uint8_t& d = s_s7519_dt[l];
        if (v == S7518_S) { ++s_s7519_n[1]; if (d < 2) { d = 2; s_s7519_pc[l] = pc; s_s7519_set.insert(l); s7519_row(1, l, pc, fn); } }
        else if (d < 2) { d = 1; s_s7519_pc[l] = pc; s_s7519_set.insert(l); }
        if (s_s7519_ctlln.count(l)) ++s_s7519_n[11];
        v = S7518_R; }
    return 1; }  /* 1 always: the s5798 tail must not see a marked address (s7475 v1 SIGBUS; s7519 run 1 SIGSEGV in loadTxtFile) */
static void s7519_load(uint32_t pc, uint32_t a, int w, const char* fn) {
    const uint32_t o = a - 0x80000000u; if (o >= 0x1800000u) return;
    std::lock_guard<std::mutex> lk(s_s7518_mu); if (s_s7519_dt.empty()) return;  /* s7560: s7519_init assigns it on host threads too */
    for (uint32_t l = o / 16u; l <= (o + (uint32_t)w - 1u) / 16u; l++) { uint8_t& d = s_s7519_dt[l];
        if (d == 2) { s7519_row(6, l, pc, fn); d = 1; } else if (d == 3) { s7519_row(8, l, pc, fn); d = 0; s_s7519_set.erase(l); } } }
extern "C" void rs64_s7519_summary(void) {
    if (!s7518_watch()) return;
    std::lock_guard<std::mutex> lk(s_s7518_mu); if (s_s7519_dt.empty()) return; uint64_t px = 0, pl = 0, pd = 0;
    for (uint32_t l : s_s7519_set) { const uint8_t d = s_s7519_dt[l]; if (d == 2) ++px; else if (d == 3) ++pl; else if (d == 1) ++pd; }
    std::string s; char b[64]; for (int i = 0; i < 12; i++) { std::snprintf(b, sizeof b, " %s=%llu", s7519_kn[i], (unsigned long long)s_s7519_n[i]); s += b; }
    std::fprintf(stderr, "[s7519-sum]%s pending_dirty=%llu pending_over_dma=%llu pending_lost=%llu row_keys=%zu\n", s.c_str(), (unsigned long long)pd,
        (unsigned long long)px, (unsigned long long)pl, s_s7519_rows.size()); }
/* s7545 class GE runtime witness (ROGUESQ_S7545_THRWATCH=1, exclusive with the s7475/s7484/s7518 watches). s7544's static census
   found 0 guest accesses to OSThread fields but resolves only constant addresses and direct calls. Here every OSThread the runtime
   creates (osCreateThread -> the RS64_S7491 "os_createthread" hook, no lib edit) has [t, t+0x1B0) marked in g_rs64_s7475_bm, so the
   generated lw/lh/lb/ld test (tools/apply_s7484_loadwatch.py) and the s5798 store test (apply_s7475_slackwatch.py, needs
   ROGUESQ_STORE_DIAG=1) route every guest access to it here. Off < 0x30 = port OSThread fields (next/pri/queue/state/flags/id;
   0x20..0x2F = host context pointer + sp), >= 0x30 = the retail __OSThreadContext tail the port leaves unused. Host writes through
   the S7491 hooks are counted per kind (kind=H). Controls: the frame counter 0x8011A890 is marked (generated-code path live:
   ctl_ld/ctl_st > 0), and ROGUESQ_S7545_PLANT=<s> (default 150) calls the same load/store entry points for siServiceThread
   (0x8010FF70, else the first thread) +0x10 after the bitmap test, as a generated access would -> `[s7545] plant DETECTED`.
   osDestroyThread is not hooked (destroyed structs stay marked; rows name the thread so a reuse is visible). Measurement only. */
static bool s7545_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7545_THRWATCH"); return e && e[0] && e[0] != '0'; }(); return on; }
struct S7545Row { uint64_t n = 0; const char* fn = nullptr; uint32_t t = 0, val = 0; double t1 = 0; };
static std::mutex s_s7545_mu; static std::vector<uint32_t> s_s7545_thr; static std::vector<double> s_s7545_tc;
static std::map<uint64_t, S7545Row> s_s7545_rows;  /* key = pc<<32 | kind<<24 | w<<16 | off */
static std::map<uint32_t, uint32_t> s_s7545_pcn;
static std::map<std::string, uint64_t> s_s7545_hostk;
static uint64_t s_s7545_ld = 0, s_s7545_st = 0, s_s7545_tail = 0, s_s7545_ctl_ld = 0, s_s7545_ctl_st = 0, s_s7545_pl_ld = 0, s_s7545_pl_st = 0, s_s7545_unk = 0;
static double s_s7545_t0 = 0;
static void s7545_mark(uint32_t a, uint32_t n) { if (!g_rs64_s7475_bm) return; for (uint32_t b = a; b < a + n; ++b) { const uint32_t o = b - 0x80000000u; if (o < 0x1800000u) g_rs64_s7475_bm[o >> 3] |= (unsigned char)(1u << (o & 7u)); } }
static bool s7545_marked(uint32_t a) { const uint32_t o = a - 0x80000000u; return g_rs64_s7475_bm && o < 0x1800000u && ((g_rs64_s7475_bm[o >> 3] >> (o & 7u)) & 1u); }
static uint32_t s7545_rdw(uint32_t a) { volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return 0; const uint32_t o = (a & ~3u) - 0x80000000u; if (o >= 0x1800000u) return 0; return *(volatile uint32_t*)(r + o); }
static int s7545_find(uint32_t a) { for (size_t i = 0; i < s_s7545_thr.size(); ++i) if (a - s_s7545_thr[i] < 0x1B0u) return (int)i; return -1; }
static void s7545_sum(bool rows) {
    std::lock_guard<std::mutex> lk(s_s7545_mu);
    uint64_t port = 0, ctxp = 0; for (auto& kv : s_s7545_rows) { const uint32_t off = (uint32_t)(kv.first & 0xFFFFu); if (off < 0x30u) { port += kv.second.n; if (off >= 0x20u) ctxp += kv.second.n; } }
    std::string hk; for (auto& kv : s_s7545_hostk) { char b[96]; std::snprintf(b, sizeof b, "%s%s:%llu", hk.empty() ? "" : ",", kv.first.c_str(), (unsigned long long)kv.second); hk += b; }
    std::fprintf(stderr, "[s7545] sum t=%.1f thr=%zu loads=%llu stores=%llu port_field=%llu ctxptr=%llu tail=%llu unk=%llu rows=%zu pcs=%zu ctl_ld=%llu ctl_st=%llu plant_ld=%llu plant_st=%llu host={%s}\n",
        s7325_now() - s_s7545_t0, s_s7545_thr.size(), (unsigned long long)s_s7545_ld, (unsigned long long)s_s7545_st, (unsigned long long)port, (unsigned long long)ctxp,
        (unsigned long long)s_s7545_tail, (unsigned long long)s_s7545_unk, s_s7545_rows.size(), s_s7545_pcn.size(), (unsigned long long)s_s7545_ctl_ld, (unsigned long long)s_s7545_ctl_st,
        (unsigned long long)s_s7545_pl_ld, (unsigned long long)s_s7545_pl_st, hk.c_str());
    if (rows) for (auto& kv : s_s7545_rows) std::fprintf(stderr, "[s7545] row pc=%08X fn=%s kind=%c w=%u off=%02X thr=%08X n=%llu last_val=%08X\n", (uint32_t)(kv.first >> 32), kv.second.fn ? kv.second.fn : "?",
        (char)((kv.first >> 24) & 0xFFu), (unsigned)((kv.first >> 16) & 0xFFu), (unsigned)(kv.first & 0xFFFFu), kv.second.t, (unsigned long long)kv.second.n, kv.second.val);
    std::fflush(stderr); }
static int s7545_access(uint32_t pc, uint32_t a, int w, const char* fn, char kind) {
    if (!s7545_marked(a) && !s7545_marked(a + (uint32_t)w - 1u)) return 0;  /* s5798 range hits reach rs64_s7475_store unmarked: not ours */
    if (a <= 0x8011A890u && 0x8011A890u < a + (uint32_t)w) { std::lock_guard<std::mutex> lk(s_s7545_mu); uint64_t& c = kind == 'L' ? s_s7545_ctl_ld : s_s7545_ctl_st;
        if (c++ == 0) std::fprintf(stderr, "[s7545] watch-ctl PASS kind=%c pc=%08X fn=%s w=%d\n", kind, pc, fn ? fn : "?", w); return 1; }
    const bool plant = fn && !std::strcmp(fn, "s7545_plant");
    std::lock_guard<std::mutex> lk(s_s7545_mu);
    const int i = s7545_find(a); if (i < 0) { ++s_s7545_unk; return 1; }
    const uint32_t t = s_s7545_thr[i], off = a - t;
    if (plant) { uint64_t& c = kind == 'L' ? s_s7545_pl_ld : s_s7545_pl_st; if (c++ == 0) std::fprintf(stderr, "[s7545] plant DETECTED kind=%c thr=%08X off=%02X t=%.1f\n", kind, t, off, s7325_now() - s_s7545_t0); return 1; }
    (kind == 'L' ? s_s7545_ld : s_s7545_st)++; if (off >= 0x30u) ++s_s7545_tail;
    S7545Row& r = s_s7545_rows[((uint64_t)pc << 32) | ((uint64_t)(uint8_t)kind << 24) | ((uint64_t)(w & 0xFF) << 16) | off];
    r.fn = fn; r.t = t; r.val = s7545_rdw(a); r.t1 = s7325_now() - s_s7545_t0;
    if (r.n++ == 0 && s_s7545_pcn[pc]++ < 64u && s_s7545_rows.size() <= 4000u)
        std::fprintf(stderr, "[s7545] thr-access pc=%08X fn=%s addr=%08X thr=%08X off=%02X kind=%c w=%d val=%08X id=%08X t=%.1f\n", pc, fn ? fn : "?", a, t, off, kind, w, r.val,
                     s7545_rdw(t + 0x14u), r.t1);
    return 1; }
extern "C" void rs64_s7545_create(uint32_t t) {
    if (!s7545_on() || t < 0x80000000u || t >= 0x81800000u - 0x1B0u) return;
    bool first = false;
    {   std::lock_guard<std::mutex> lk(s_s7545_mu);
        if (s_s7545_t0 == 0) { s_s7545_t0 = s7325_now(); first = true;
            if (!g_rs64_s7475_bm) g_rs64_s7475_bm = (unsigned char*)std::calloc(0x1800000u >> 3, 1);
            s7545_mark(0x8011A890u, 4); g_rs64_s7484_on = g_rs64_s7475_bm ? 1 : 0;
            std::fprintf(stderr, "[s7545] thread watch armed bm=%d store_diag_needed=ROGUESQ_STORE_DIAG=1\n", g_rs64_s7484_on); }
        for (uint32_t x : s_s7545_thr) if (x == t) { std::fprintf(stderr, "[s7545] thr-recreate thr=%08X\n", t); return; }
        s_s7545_thr.push_back(t); s_s7545_tc.push_back(s7325_now() - s_s7545_t0); s7545_mark(t, 0x1B0u);
        std::fprintf(stderr, "[s7545] thr-add thr=%08X n=%zu t=%.1f\n", t, s_s7545_thr.size(), s_s7545_tc.back()); }
    if (first) std::thread([] {
        const double plant_s = [] { const char* e = std::getenv("ROGUESQ_S7545_PLANT"); return (e && *e) ? std::atof(e) : 150.0; }();
        bool planted = false; int k = 0;
        for (;;) { std::this_thread::sleep_for(std::chrono::seconds(5)); ++k; const double now = s7325_now() - s_s7545_t0;
            if (!planted && plant_s > 0 && now >= plant_s) { planted = true; uint32_t t = 0;
                { std::lock_guard<std::mutex> lk(s_s7545_mu); for (uint32_t x : s_s7545_thr) if (x == 0x8010FF70u) t = x; if (!t && !s_s7545_thr.empty()) t = s_s7545_thr[0]; }
                std::fprintf(stderr, "[s7545] plant SET thr=%08X marked=%d t=%.1f\n", t, t ? (int)s7545_marked(t + 0x10u) : 0, now);
                if (t && s7545_marked(t + 0x10u)) { rs64_s7484_load(0x80DEAD10u, t + 0x10u, 2, "s7545_plant"); rs64_s7475_store(0x80DEAD14u, t + 0x10u, 2, "s7545_plant"); } }
            s7545_sum(k % 12 == 0); } }).detach(); }
static void s7545_unmark(uint32_t a, uint32_t n) { if (!g_rs64_s7475_bm) return; for (uint32_t b = a; b < a + n; ++b) { const uint32_t o = b - 0x80000000u; if (o < 0x1800000u) g_rs64_s7475_bm[o >> 3] &= (unsigned char)~(1u << (o & 7u)); } }
static void rs64_s7545_destroy(uint32_t t) {  /* osDestroyThread (self or other; thread exit runs it with NULL -> self): stop watching */
    std::lock_guard<std::mutex> lk(s_s7545_mu);
    for (size_t i = 0; i < s_s7545_thr.size(); ++i) if (s_s7545_thr[i] == t) { s7545_unmark(t, 0x1B0u); s_s7545_thr.erase(s_s7545_thr.begin() + i); s_s7545_tc.erase(s_s7545_tc.begin() + i);
        std::fprintf(stderr, "[s7545] thr-del thr=%08X n=%zu t=%.1f\n", t, s_s7545_thr.size(), s7325_now() - s_s7545_t0); return; }
    std::fprintf(stderr, "[s7545] thr-del-unknown thr=%08X\n", t); }
static void s7545_host(uint32_t a, uint32_t w, const char* kind) {
    std::lock_guard<std::mutex> lk(s_s7545_mu);
    for (uint32_t t : s_s7545_thr) if (a < t + 0x1B0u && t < a + w) { ++s_s7545_hostk[kind ? kind : "?"]; return; } }
/* s7776 dangling NPC-slot table watch (ROGUESQ_S7776_TBLWATCH=1, exclusive load-watch mode, measurement only). s7774 saw
   *(u32*)0x80130BB0 (NPC slot table: 2048 x {u32 obj; u16 prev; u16 next}) point at entries that are not RAM pointers for ~60 s
   between the menu overlay and initMission. Every generated read of the table pointer (59 static lw 0xBB0(0x8013) sites, all
   RS64_S7484_LD-wrapped) lands here: per (pc, fn) we count reads while the table is clean vs dangling (any non-zero obj that is
   not a 4-aligned KSEG0 pointer below 16 MB), and log every change of the pointer value. Positive controls: the frame counter
   0x8011A890 is marked too (watch mechanism), and in-flight reads with state=clean must be > 0 (the readers do fire). */
static bool s7776_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7776_TBLWATCH"); return e && e[0] && e[0] != '0'; }(); return on; }
struct S7776Row { const char* fn = nullptr; uint64_t clean = 0, dangling = 0, badptr = 0; double t_first_dangling = -1; };
static std::mutex s_s7776_mu;
static std::map<uint32_t, S7776Row> s_s7776_rows;
static uint64_t s_s7776_ctl = 0, s_s7776_hits = 0, s_s7776_dang = 0;
static uint32_t s_s7776_tbl = 0xFFFFFFFFu, s_s7776_bad = 0, s_s7776_live = 0; static double s_s7776_scan_t = -1, s_s7776_t0 = 0;
static bool s7776_okva(uint32_t va) { return va >= 0x80000000u && va < 0x81000000u && (va & 3u) == 0; }
static void s7776_rescan(uint32_t tbl, double now) {
    s_s7776_bad = 0; s_s7776_live = 0;
    if (!s7776_okva(tbl)) { s_s7776_bad = 1; }
    else for (uint32_t i = 0; i < 2048; i++) { const uint32_t o = s7545_rdw(tbl + i * 8u); if (!o) continue; ++s_s7776_live; if (!s7776_okva(o)) ++s_s7776_bad; }
    s_s7776_scan_t = now; }
static void s7776_sum(bool rows) {
    std::lock_guard<std::mutex> lk(s_s7776_mu); const double now = s7325_now() - s_s7776_t0;
    std::fprintf(stderr, "[s7776] sum t=%.1f ctl=%llu hits=%llu dangling_hits=%llu tbl=%08X live=%u bad=%u pcs=%zu\n", now, (unsigned long long)s_s7776_ctl,
                 (unsigned long long)s_s7776_hits, (unsigned long long)s_s7776_dang, s_s7776_tbl, s_s7776_live, s_s7776_bad, s_s7776_rows.size());
    if (rows) for (const auto& kv : s_s7776_rows) std::fprintf(stderr, "[s7776] row pc=%08X fn=%s clean=%llu dangling=%llu badptr=%llu t_first_dangling=%.1f\n", kv.first,
                 kv.second.fn ? kv.second.fn : "?", (unsigned long long)kv.second.clean, (unsigned long long)kv.second.dangling, (unsigned long long)kv.second.badptr, kv.second.t_first_dangling);
    std::fflush(stderr); }
static int s7776_load(uint32_t pc, uint32_t a, int w, const char* fn) {
    std::lock_guard<std::mutex> lk(s_s7776_mu); const double now = s7325_now() - s_s7776_t0;
    if (a <= 0x8011A890u && 0x8011A890u < a + (uint32_t)w) { if (s_s7776_ctl++ == 0) std::fprintf(stderr, "[s7776] watch-ctl PASS pc=%08X fn=%s t=%.1f\n", pc, fn ? fn : "?", now); return 1; }
    if (!(a <= 0x80130BB0u && 0x80130BB0u < a + (uint32_t)w)) return 1;
    ++s_s7776_hits; const uint32_t tbl = s7545_rdw(0x80130BB0u);
    if (tbl != s_s7776_tbl) { std::fprintf(stderr, "[s7776] tbl-change old=%08X new=%08X pc=%08X fn=%s t=%.1f\n", s_s7776_tbl, tbl, pc, fn ? fn : "?", now); s_s7776_tbl = tbl; s7776_rescan(tbl, now); }
    else if (now - s_s7776_scan_t >= 0.02) s7776_rescan(tbl, now);
    S7776Row& r = s_s7776_rows[pc]; if (!r.fn) r.fn = fn;
    if (!s7776_okva(tbl)) ++r.badptr;
    if (s_s7776_bad) { ++s_s7776_dang; if (r.dangling++ == 0) { r.t_first_dangling = now; std::fprintf(stderr, "[s7776] dangling-reader pc=%08X fn=%s tbl=%08X live=%u bad=%u t=%.1f\n", pc, fn ? fn : "?", tbl, s_s7776_live, s_s7776_bad, now); } }
    else ++r.clean;
    return 1; }
namespace { struct S7776Arm { S7776Arm() {
    if (!s7776_on()) return;
    s_s7776_t0 = s7325_now();
    if (!g_rs64_s7475_bm) g_rs64_s7475_bm = (unsigned char*)std::calloc(0x1800000u >> 3, 1);
    if (!g_rs64_s7475_bm) return;
    s7545_mark(0x80130BB0u, 4); s7545_mark(0x8011A890u, 4); g_rs64_s7484_on = 1;
    std::fprintf(stderr, "[s7776] table-pointer watch armed\n");
    std::thread([] { for (int k = 1;; ++k) { std::this_thread::sleep_for(std::chrono::seconds(5)); s7776_sum(k % 6 == 0); } }).detach(); } } s_s7776_arm; }
/* s7777 class: resident global words holding a heap pointer that outlive their block (ROGUESQ_S7777_DANGLE=1, exclusive
   load/store watch mode, measurement only; stores need ROGUESQ_STORE_DIAG=1). Generalises s7776 (*0x80130BB0). A sweep thread
   (every 250 ms) reads every word of resident main code/data/overlay/main-bss [0x80000400, 0x80154690) and walks the three
   rs_malloc arena chains (heads 0x8010FEFC/0x8010FF00/0x8010FF18). A word whose value lies inside a USED block is tracked
   (value, block, block alloc serial) and marked in the s7475 bitmap so its guest loads and stores land here. It turns DANGLING
   when, value unchanged and not stored since: rs_free of its block ('f'), the block is free in the chain ('F'), no chain block
   holds it any more ('N': arena torn down), or the block was re-carved / re-allocated ('R'). A guest store to the word ends the
   dangling state (re-init). Every guest load of a dangling word is a dangling read, logged per (word, pc).
   Positive controls: the frame counter 0x8011A890 load+store (watch mechanism) and 0x80130BB0 must dangle in the menu phase.
   Offline: tools/s7777_dangle_score.py classifies words against the symbol table (code words that look like pointers are
   never data-loaded, so they cannot produce reads). */
static bool s7777_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7777_DANGLE"); return e && e[0] && e[0] != '0'; }(); return on; }
struct S7777W { uint32_t v = 0, bs = 0, bsz = 0, ser = 0; int st = 0; char why = 0; bool rewr = false; double t_seen = 0, t_dang = 0; uint64_t rd_clean = 0, rd_dang = 0, nd = 0; };
struct S7777R { const char* fn = nullptr; uint64_t n = 0; double t = 0; uint32_t v = 0; char why = 0; };
struct S7777B { uint32_t b, e, fl; };
static std::mutex s_s7777_mu;
static std::map<uint32_t, S7777W> s_s7777_w;
static std::map<uint32_t, uint32_t> s_s7777_ser;
static std::map<std::pair<uint32_t, uint32_t>, S7777R> s_s7777_rd;
static uint32_t s_s7777_serc = 0; static double s_s7777_t0 = 0;
static uint64_t s_s7777_ctl_ld = 0, s_s7777_ctl_st = 0, s_s7777_sweeps = 0, s_s7777_dev = 0, s_s7777_drd = 0, s_s7777_crd = 0, s_s7777_st = 0, s_s7777_reinit = 0, s_s7777_nlog = 0;
static const uint32_t S7777_LO = 0x80000400u, S7777_HI = 0x80154690u;
/* deref watch (run 2): on the first dangling read of a word whose block was freed (f/F/N, block <= 256 KB) the stale block
   [bs, bs+bsz) is marked too, so guest loads/stores into it land in s7777_access and are attributed per (word, pc, kind).
   Accesses by the dangling reader's own function = stale derefs; other functions = the block's new owner. Ends at word re-init. */
struct S7777S { uint32_t word, lo, hi; const char* rfn; bool open; double t; };
struct S7777D { const char* fn = nullptr; uint64_t n = 0; double t = 0; uint32_t a0 = 0; bool same = false; bool open = true; };
static std::vector<S7777S> s_s7777_sr;
static std::map<std::tuple<uint32_t, uint32_t, char>, S7777D> s_s7777_dr;
static void s7777_bm(uint32_t a, bool on) { if (!g_rs64_s7475_bm) return; for (uint32_t b = a; b < a + 4u; ++b) { const uint32_t o = b - 0x80000000u; if (o >= 0x1800000u) continue;
    if (on) g_rs64_s7475_bm[o >> 3] |= (unsigned char)(1u << (o & 7u)); else g_rs64_s7475_bm[o >> 3] &= (unsigned char)~(1u << (o & 7u)); } }
static void s7777_dangle(uint32_t a, S7777W& w, char why, double now) {
    w.st = 1; w.why = why; w.t_dang = now; ++w.nd; ++s_s7777_dev;
    if (s_s7777_nlog++ < 400 || a == 0x80130BB0u || w.rd_clean || w.rd_dang)
        std::fprintf(stderr, "[s7777] dangle a=%08X v=%08X why=%c blk=%08X bsz=%X ser=%u age=%.2f t=%.1f\n", a, w.v, why, w.bs, w.bsz, w.ser, now - w.t_seen, now); }
static void s7777_sweep() {
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    std::vector<S7777B> bl; const uint32_t top = rs64_ram_top;
    static const uint32_t heads[3] = {0x8010FEFCu, 0x8010FF00u, 0x8010FF18u}; uint32_t seen[3] = {0, 0, 0}; int na = 0;
    for (int i = 0; i < 3; ++i) { const uint32_t h0 = s7472_rd(r, heads[i]); if (h0 < S7777_HI || h0 >= top) continue;
        bool dup = false; for (int j = 0; j < na; ++j) dup |= seen[j] == h0; if (dup) continue; seen[na++] = h0;
        uint32_t b = h0; for (int g = 0; g < 400000; ++g) { const uint32_t w0 = s7472_rd(r, b), sz = s7472_rd(r, b + 4u), fl = w0 >> 16;
            if ((fl & 8u) || (fl != 1u && fl != 2u && fl != 6u) || (sz & 0xFu) || b + 0x10u + sz <= b || b + 0x10u + sz >= top) break;
            bl.push_back({b, b + 0x10u + sz, fl}); b += 0x10u + sz; } }
    std::sort(bl.begin(), bl.end(), [](const S7777B& x, const S7777B& y) { return x.b < y.b || (x.b == y.b && x.e > y.e); });
    const uint32_t hlo = bl.empty() ? 0xFFFFFFFFu : bl.front().b; uint32_t hhi = 0; for (auto& x : bl) hhi = std::max(hhi, x.e);
    std::lock_guard<std::mutex> lk(s_s7777_mu); const double now = s7325_now() - s_s7777_t0; ++s_s7777_sweeps;
    auto find = [&](uint32_t v) -> const S7777B* { const S7777B* best = nullptr;  /* innermost block holding v */
        auto it = std::upper_bound(bl.begin(), bl.end(), v, [](uint32_t x, const S7777B& y) { return x < y.b; });
        for (int k = 0; it != bl.begin() && k < 8; ++k) { --it; if (v >= it->b && v < it->e && (!best || it->e - it->b < best->e - best->b)) best = &*it; } return best; };
    uint64_t ntr = 0, ndg = 0;
    for (uint32_t a = S7777_LO; a < S7777_HI; a += 4u) {
        const uint32_t v = s7472_rd(r, a); auto wit = s_s7777_w.find(a);
        if (v < hlo || v >= hhi) { if (wit != s_s7777_w.end()) { s7777_bm(a, false); s_s7777_w.erase(wit); } continue; }
        const S7777B* b = find(v); const bool used = b && b->fl != 1u; const uint32_t bs = b ? b->b + 0x10u : 0;
        if (wit == s_s7777_w.end() || wit->second.v != v || wit->second.rewr) {
            if (!used) { if (wit != s_s7777_w.end()) { s7777_bm(a, false); s_s7777_w.erase(wit); } continue; }  /* born pointing at free/no block: not an owning pointer we saw live */
            S7777W& w = s_s7777_w[a]; const uint64_t rc = w.rd_clean, rdg = w.rd_dang, nd = w.nd;
            w = S7777W{}; w.v = v; w.bs = bs; w.bsz = b->e - b->b - 0x10u; w.ser = s_s7777_ser.count(bs) ? s_s7777_ser[bs] : 0; w.t_seen = now; w.rd_clean = rc; w.rd_dang = rdg; w.nd = nd;
            s7777_bm(a, true); ++ntr; continue; }
        S7777W& w = wit->second; ++ntr;
        if (w.st == 1) { ++ndg; continue; }
        if (!b) s7777_dangle(a, w, 'N', now);
        else if (!used) s7777_dangle(a, w, 'F', now);
        else if (bs != w.bs || (s_s7777_ser.count(bs) ? s_s7777_ser[bs] : 0) != w.ser) s7777_dangle(a, w, 'R', now);
        if (w.st == 1) ++ndg; }
    if (s_s7777_sweeps % 20 == 1)
        std::fprintf(stderr, "[s7777] sum t=%.1f sweeps=%llu blocks=%zu heap=%08X..%08X tracked=%llu dangling=%llu dangle_events=%llu clean_reads=%llu dangling_reads=%llu stores=%llu reinit=%llu ctl_ld=%llu ctl_st=%llu\n",
                     now, (unsigned long long)s_s7777_sweeps, bl.size(), hlo, hhi, (unsigned long long)ntr, (unsigned long long)ndg, (unsigned long long)s_s7777_dev, (unsigned long long)s_s7777_crd,
                     (unsigned long long)s_s7777_drd, (unsigned long long)s_s7777_st, (unsigned long long)s_s7777_reinit, (unsigned long long)s_s7777_ctl_ld, (unsigned long long)s_s7777_ctl_st);
    if (s_s7777_sweeps % 240 == 0) {  /* every 60 s: per-word rows that ever dangled, and every dangling-read row */
        for (auto& kv : s_s7777_w) if (kv.second.nd) std::fprintf(stderr, "[s7777] word a=%08X v=%08X st=%d why=%c nd=%llu rd_clean=%llu rd_dang=%llu\n", kv.first, kv.second.v, kv.second.st, kv.second.why ? kv.second.why : '-',
                                                                (unsigned long long)kv.second.nd, (unsigned long long)kv.second.rd_clean, (unsigned long long)kv.second.rd_dang);
        for (auto& kv : s_s7777_dr) std::fprintf(stderr, "[s7777] drow word=%08X pc=%08X kind=%c fn=%s n=%llu same_fn=%d open=%d a0=%08X t_first=%.1f\n", std::get<0>(kv.first), std::get<1>(kv.first), std::get<2>(kv.first),
                                                 kv.second.fn ? kv.second.fn : "?", (unsigned long long)kv.second.n, (int)kv.second.same, (int)kv.second.open, kv.second.a0, kv.second.t);
        for (auto& kv : s_s7777_rd) std::fprintf(stderr, "[s7777] rdrow a=%08X pc=%08X fn=%s n=%llu v=%08X why=%c t_first=%.1f\n", kv.first.first, kv.first.second, kv.second.fn ? kv.second.fn : "?", (unsigned long long)kv.second.n, kv.second.v, kv.second.why, kv.second.t); } }
static void s7777_malloc(uint32_t ptr) { if (!s7777_on() || !ptr) return; std::lock_guard<std::mutex> lk(s_s7777_mu); s_s7777_ser[ptr] = ++s_s7777_serc; }
static void s7777_free(uint32_t ptr) {
    if (!s7777_on() || !ptr) return; std::lock_guard<std::mutex> lk(s_s7777_mu); const double now = s7325_now() - s_s7777_t0;
    for (auto& kv : s_s7777_w) if (kv.second.st == 0 && kv.second.bs == ptr) s7777_dangle(kv.first, kv.second, 'f', now); }
static int s7777_access(uint32_t pc, uint32_t a, int w, const char* fn, bool st) {
    if (a <= 0x8011A890u && 0x8011A890u < a + (uint32_t)w) { std::lock_guard<std::mutex> lk(s_s7777_mu); uint64_t& c = st ? s_s7777_ctl_st : s_s7777_ctl_ld;
        if (c++ == 0) std::fprintf(stderr, "[s7777] watch-ctl-%s PASS pc=%08X fn=%s\n", st ? "store" : "load", pc, fn ? fn : "?"); return 1; }
    std::lock_guard<std::mutex> lk(s_s7777_mu); const double now = s7325_now() - s_s7777_t0;
    for (uint32_t wa = a & ~3u; wa < a + (uint32_t)w; wa += 4u) {
        auto it = s_s7777_w.find(wa);
        if (it == s_s7777_w.end()) {
            if (wa < S7777_HI) continue;
            for (auto& s : s_s7777_sr) if (wa >= s.lo && wa < s.hi) {
                S7777D& d = s_s7777_dr[{s.word, pc, st ? 'S' : 'L'}]; const bool same = fn && s.rfn && !std::strcmp(fn, s.rfn);
                if (d.n++ == 0) { d.fn = fn; d.t = now; d.a0 = wa; d.same = same; d.open = s.open;
                    if (s_s7777_dr.size() <= 400) std::fprintf(stderr, "[s7777] stale-%s word=%08X a=%08X off=%X pc=%08X fn=%s same_fn_as_reader=%d open=%d t=%.1f\n", st ? "store" : "load", s.word, wa, wa - s.lo, pc, fn ? fn : "?", (int)same, (int)s.open, now); }
                break; }
            continue; }
        S7777W& x = it->second;
        if (st) { ++s_s7777_st; if (x.st == 1) { ++s_s7777_reinit; x.st = 2; for (auto& s : s_s7777_sr) if (s.word == wa && s.open) { s.open = false; std::fprintf(stderr, "[s7777] deref-watch OFF word=%08X (store re-init pc=%08X fn=%s) t=%.1f\n", wa, pc, fn ? fn : "?", now); } } x.rewr = true; continue; }
        if (x.st == 1 && s7545_rdw(wa) == x.v && !x.rewr) {
            ++s_s7777_drd; ++x.rd_dang; S7777R& rr = s_s7777_rd[{wa, pc}];
            if (rr.n == 0 && x.why != 'R' && x.bsz <= 0x40000u && x.bs >= S7777_HI) { bool have = false; for (auto& s : s_s7777_sr) have |= s.word == wa && s.lo == x.bs && s.open;
                if (!have) { s_s7777_sr.push_back({wa, x.bs, x.bs + x.bsz, fn, true, now}); for (uint32_t b = x.bs; b < x.bs + x.bsz; b += 4u) s7777_bm(b, true);
                    std::fprintf(stderr, "[s7777] deref-watch ON word=%08X blk=%08X..%08X reader=%s t=%.1f\n", wa, x.bs, x.bs + x.bsz, fn ? fn : "?", now); } }
            if (rr.n++ == 0) { rr.fn = fn; rr.t = now; rr.v = x.v; rr.why = x.why;
                if (s_s7777_rd.size() <= 300) std::fprintf(stderr, "[s7777] dangling-read a=%08X v=%08X why=%c pc=%08X fn=%s since=%.2f t=%.1f\n", wa, x.v, x.why, pc, fn ? fn : "?", now - x.t_dang, now); } }
        else { ++s_s7777_crd; ++x.rd_clean; } }
    return 1; }
namespace { struct S7777Arm { S7777Arm() {
    if (!s7777_on()) return;
    s_s7777_t0 = s7325_now();
    if (!g_rs64_s7475_bm) g_rs64_s7475_bm = (unsigned char*)std::calloc(0x1800000u >> 3, 1);
    if (!g_rs64_s7475_bm) return;
    s7777_bm(0x8011A890u, true); g_rs64_s7484_on = 1;
    std::fprintf(stderr, "[s7777] dangling-global watch armed range=%08X..%08X\n", S7777_LO, S7777_HI);
    std::thread([] { for (;;) { std::this_thread::sleep_for(std::chrono::milliseconds(250)); s7777_sweep(); } }).detach(); } } s_s7777_arm; }
extern "C" int rs64_s7484_load(uint32_t pc, uint32_t a, int w, const char* fn) {
    if (s7777_on()) return s7777_access(pc, a, w, fn, false);  /* s7777 dangling-global class watch (exclusive) */
    if (s7776_on()) return s7776_load(pc, a, w, fn);  /* s7776 dangling slot-table watch (exclusive) */
    if (s7545_on()) return s7545_access(pc, a, w, fn, 'L');  /* s7545 class GE thread watch (exclusive) */
    if (s7518_watch()) { s7519_load(pc, a, w, fn); return s7518_load(pc, a, w, fn); }
    if (a <= 0x8011A890u && 0x8011A890u < a + (uint32_t)w) { if (s_s7484_ctl++ == 0) std::fprintf(stderr, "[s7484] watch-ctl PASS pc=%08X fn=%s w=%d\n", pc, fn ? fn : "?", w); return 1; }
    std::lock_guard<std::mutex> lk(s_s7475_mu); return s7484_load(pc, a, w, fn); }
extern "C" int rs64_s7475_store(uint32_t pc, uint32_t a, int w, const char* fn) {
    if (s7777_on()) return s7777_access(pc, a, w, fn, true);  /* s7777 (exclusive) */
    if (s7545_on()) return s7545_access(pc, a, w, fn, pc >= 0xE0000000u ? 'H' : 'S');  /* s7545 class GE */
    if (s7518_watch()) return s7519_store(pc, a, w, fn);  /* s7519 class FP (exclusive mode, as the s7518 load watch) */
    if (rs64_s7501_on && rs64_s7501_cpu(pc, a, w, fn)) return 1;  /* s7501 EZ: guest store into a seen framebuffer (bits marked by main.cpp) */
    /* returns 1 when the store is ours (slack or the control word): the s5798 dispatcher then returns */
    /* watch positive control (ROGUESQ_S7475_CANARY on): the frame counter 0x8011A890 is marked at arming; the first guest store to it must land here */
    if (a <= 0x8011A890u && 0x8011A890u < a + (uint32_t)w) { static uint64_t nc = 0; if (nc++ == 0) std::fprintf(stderr, "[s7475] watch-ctl PASS pc=%08X fn=%s w=%d\n", pc, fn ? fn : "?", w); return 1; }
    std::lock_guard<std::mutex> lk(s_s7475_mu);
    if (s7480_store(pc, a, w, fn)) return 1;  /* s7480 class EH */
    auto it = s_s7475_live.upper_bound(a + (uint32_t)w - 1u); if (it == s_s7475_live.begin()) return 1; --it;
    const uint32_t blk = it->first; const S7475R& b = it->second;
    const uint32_t lo = blk + b.req, hi = blk + b.sz;
    if (a + (uint32_t)w <= lo || a >= hi) return 1;  /* bitmap bit stale or store outside this block's slack */
    /* s7478 class EF: a record whose header no longer matches is a dead block (arena re-carved or overwritten without rs_free:
       loadOverlay DMA + bss memset over a cutscene arena, s7478), not an overrun: drop it, as the walk path does. ROGUESQ_S7478_STALECHK=0 = old scoring. */
    static const bool stalechk = [] { const char* e = std::getenv("ROGUESQ_S7478_STALECHK"); return !(e && e[0] == '0'); }();
    if (stalechk) { volatile uint8_t* rr = g_recomp_rdram_for_wp_raw;
        if (rr && !s7475_hdr_ok(rr, blk, b)) { static int nl = 0; ++s_s7475_stale;
            if (nl++ < 20) std::fprintf(stderr, "[s7478] stale-drop pc=%08X fn=%s a=%08X blk=%08X req=%X w0=%08X size=%08X age=%.2f alloc=%s\n", pc, fn ? fn : "?", a, blk, b.req,
                                        s7472_rd(rr, blk - 0x10u), s7472_rd(rr, blk - 0x0Cu), s7325_now() - b.t, s7475_sym(b.hpc).c_str());
            s7475_mark(blk, b, false); s_s7475_live.erase(it); return 1; } }
    ++s_s7475_stores;
    if (t_s7488_ust) { ++s_s7488_slack; static int n8 = 0; if (n8++ < 30) std::fprintf(stderr, "[s7488] ust-slack pc=%08X fn=%s a=%08X w=%d blk=%08X req=%X over=%u t=%.1f\n", pc, fn ? fn : "?", a, w, blk, b.req, a + (uint32_t)w - lo, s7325_now() - s_s7475_t0); }
    const bool plant = false;
    auto& e = s_s7475_wpc[pc]; const bool first = e.n == 0; ++e.n;
    if (first) { e = S7475W{1, blk, b.req, b.sz, a - blk, w, b.hpc, fn};
        if (s_s7475_wpc.size() <= 60) std::fprintf(stderr, "[s7475] slack-store pc=%08X fn=%s a=%08X w=%d blk=%08X req=%X size=%X off=%X over=%u alloc=%s t=%.1f%s\n",
            pc, fn ? fn : "?", a, w, blk, b.req, b.sz, a - blk, a + (uint32_t)w - lo, s7475_sym(b.hpc).c_str(), s7325_now() - s_s7475_t0, plant ? " PLANT" : ""); 
        if (s7478_bt_on() && s_s7475_wpc.size() <= 60) { void* sb[10]; const int ns = backtrace(sb, 10);
            std::fprintf(stderr, "[s7478] store-bt pc=%08X a=%08X ra_rec=%08X chain=%s\n", pc, a, b.ra, s7478_chain(sb, ns).c_str());
            std::fprintf(stderr, "[s7478] alloc-bt blk=%08X req=%X chain=%s\n", blk, b.req, s7478_chain(b.bt, b.nbt).c_str());
            volatile uint8_t* rr = g_recomp_rdram_for_wp_raw; if (rr) { uint32_t nz = 0; for (uint32_t o = 0; o < b.req; o += 4) nz += s7472_rd(rr, blk + o) != 0;
                std::fprintf(stderr, "[s7478] store-hdr blk=%08X w0=%08X size=%08X hdr_ok=%d body_nonzero_words=%u/%u age=%.2f\n", blk, s7472_rd(rr, blk - 0x10u), s7472_rd(rr, blk - 0x0Cu),
                             (int)s7475_hdr_ok(rr, blk, b), nz, (b.req + 3) / 4, s7325_now() - b.t); } } }
    return 1; }
static void s7475_free(uint32_t ptr, uint32_t ra) {
    s7777_free(ptr);  /* s7777 dangling-global class */
    if (!s7475_on()) return;
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    const double now = s7325_now();
    std::lock_guard<std::mutex> lk(s_s7475_mu);
    if (s_s7475_t0 == 0) return;
    auto it = s_s7475_live.find(ptr);
    if (it != s_s7475_live.end()) {
        if (s7475_hdr_ok(r, ptr, it->second)) { ++s_s7475_freechk; s7475_check1(r, ptr, it->second, "free", ra, now); } else ++s_s7475_stale;
        if (s_s7475_plant == 1 && ptr == s_s7475_pblk) { s_s7475_plant = 2; std::fprintf(stderr, "[s7475] plant LOST blk=%08X (freed before check)\n", ptr); }
        s7475_mark(it->first, it->second, false); s_s7475_live.erase(it); }
    s7480_free(r, ptr, now);
    s7475_tick(r, now); }
extern "C" void rs64_s6063_malloc(uint32_t req, uint32_t ptr, uint32_t ra) {
    s7472_check("malloc", ra);
    { void** fp = (void**)__builtin_frame_address(0); void* hpc = (fp && fp[0]) ? ((void**)fp[0])[1] : nullptr; s7475_malloc(req, ptr, ra, hpc); }
    rs64_floor_ownership("malloc", ptr, req, ra);
    if (ptr && s7317_on()) {
        S7317B b{ req, { __builtin_return_address(0), nullptr, nullptr }, 0.0, g_s6127_flags };
        if (rs64_s7324_on) b.t = s7325_now();
        void** fp = (void**)__builtin_frame_address(0);  /* arm64: fp[0] = caller fp, fp[1] = return address */
        for (int k = 1; k < 3 && fp && fp[0]; ++k) { fp = (void**)fp[0]; b.pc[k] = fp[1]; }
        if (rs64_s7331_on) rs64_s7331_malloc(ptr, req, b.pc[1]);
        std::lock_guard<std::mutex> lk(s_s7317_mu);
        { auto ex = s_s7317_live.find(ptr); s7333_ev("malloc", ptr, ex != s_s7317_live.end() ? ex->second.req : 0u, ex != s_s7317_live.end() && ex->second.pc[0] == (void*)&s7332_carve_tag, req); }
        s_s7317_live[ptr] = b; if (s7317_isspill(ptr)) ++s_s7317_sprec;
        else { s_s7325_lastmalloc = ptr; if (ptr < s_s7325_hmin) s_s7325_hmin = ptr; if (ptr + req > s_s7325_hmax) s_s7325_hmax = ptr + req; } }
    if (!s6063_on()) return;
    if (!ptr && req == 0x1000u) s6127_walk(req);
    if (ptr && req == 0x1000u) { static int k1 = 0; if (k1++ < 40) { s6127_walk(req, true); uint8_t* r = g_s6127_rd; std::fprintf(stderr, "[heaplog-1000ok] flags=%X -> %08X slot100=%08X slotE8=%08X slot104=%08X\n", g_s6127_flags, ptr, r?s5042_rd(r,0x10FF00u):0xFFFFFFFFu, r?s5042_rd(r,0x10FF18u):0xFFFFFFFFu, r?s5042_rd(r,0x10FEFCu):0xFFFFFFFFu); } }
    { static int ntrig = 0; /* s6129: heap block list around the unexplained big (top-down arena?) block */
      if (ptr && ((req == 0x1CFE0u && ptr == 0x802EC480u) || (req == 0xC0C0u && ptr == 0x80318950u) || (req == 0x8000u && (g_s6127_flags & 0xF) == 4 && ntrig == 2)) && ntrig < 4) { ++ntrig; char w[48]; std::snprintf(w, sizeof w, "trig%d req=%X ptr=%08X fl=%X", ntrig, req, ptr, g_s6127_flags); s6129_dump(w, 0x802EC000u); } }
    static int nnull = 0;
    if (ptr) { auto it = s_s6063_live.find(ptr); if (it != s_s6063_live.end()) s_s6063_bytes -= it->second; s_s6063_live[ptr] = req; s_s6063_bytes += req; if (s_s6063_bytes > s_s6063_peak) s_s6063_peak = s_s6063_bytes; }
    if (!ptr && req == 0x1000u) std::fprintf(stderr, "[heaplog-null1000] flags=%08X req=0x1000 -> NULL ra=%08X live=0x%llX nblk=%zu\n", g_s6127_flags, ra, (unsigned long long)s_s6063_bytes, s_s6063_live.size()); /* s6126: null-dest DMA scratch alloc */
    if (req >= 0x4000u || (!ptr && nnull < 4))
        std::fprintf(stderr, "[heaplog] flags=%X malloc req=0x%X -> %08X ra=%08X live=0x%llX peak=0x%llX nblk=%zu\n", g_s6127_flags, req, ptr, ra, (unsigned long long)s_s6063_bytes, (unsigned long long)s_s6063_peak, s_s6063_live.size());
    if (!ptr && nnull++ < 2) {
        std::multimap<uint32_t, uint32_t, std::greater<uint32_t>> big; for (auto& kv : s_s6063_live) big.emplace(kv.second, kv.first);
        int k = 0; for (auto& b : big) { if (k++ >= 8) break; std::fprintf(stderr, "[heaplog]   live top%d size=0x%X ptr=%08X\n", k, b.first, b.second); }
    }
}
extern "C" void rs64_s6063_free(uint32_t ptr) {
    s7472_check("free", 0);
    s7475_free(ptr, 0);
    rs64_floor_ownership("free", ptr, 0, 0);
    s7317_free(ptr);
    if (!s6063_on() || !ptr) return;
    auto it = s_s6063_live.find(ptr); if (it == s_s6063_live.end()) return;
    s_s6063_bytes -= it->second; s_s6063_live.erase(it);
}
static inline uint32_t s5042_rd(const uint8_t* rd, uint32_t off);
extern "C" void rs64_s6090_init(uint32_t a0, uint32_t a1, uint32_t ra) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_BUCKETLOG"); return e && e[0] && e[0] != '0'; }();
    if (on) std::fprintf(stderr, "[bucketlog] initTextureLUT a0=%u a1=%u ra=%08X\n", a0 & 0xFFFFu, a1 & 0xFFFFu, ra);
}
extern "C" uint32_t rs64_s6091_scale(uint32_t v) {
    static const uint32_t k = [] { const char* e = std::getenv("ROGUESQ_LUTSCALE"); int x = e ? std::atoi(e) : 1; return (uint32_t)(x < 1 ? 1 : x > 16 ? 16 : x); }();
    if (k == 1 || v != 2048u) return v;
    std::fprintf(stderr, "[lutscale] %u -> %u\n", v, v * k);
    return v * k;
}
static unsigned long s_s6093_cnt[8];
extern "C" void rs64_s6096_skip(uint32_t r16, uint32_t off) { ++s_s6093_cnt[6]; static int n = 0; if (n++ < 12) std::fprintf(stderr, "[bucketlog] s6096 guard-skip r16=%08X s1off=%u\n", r16, off); }
extern "C" void rs64_s6097_inline(uint32_t nb, uint32_t heads, uint32_t ent, uint32_t bad) { static unsigned long nt = 0; ++nt; if (nt <= 6 || nt % 100 == 0) std::fprintf(stderr, "[bucketlog] s6097 inline tick#%lu nb=%u heads=%u ent=%u oob=%u\n", nt, nb, heads, ent, bad); }
static void rs64_s6287_flush(unsigned long begin, uint32_t len);
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;
static std::vector<uint32_t> s_s6558_blocks;  /* s6558: rs64_s6099_alloc block bases */
static void rs64_s6558_cut(unsigned long begin, uint32_t len) {  /* s6558: ROGUESQ_CHUNKCUT=1 -> on a >200-chunk free-list drop between begins, locate the walk's terminal node vs the previous snapshot */
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_CHUNKCUT"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static const bool selftest = [] { const char* e = std::getenv("ROGUESQ_CHUNKCUT_SELFTEST"); return e && e[0] && e[0] != '0'; }();
    volatile uint8_t* rd = g_recomp_rdram_for_wp_raw; if (!rd) return;
    auto ok = [](uint32_t a) { return a >= 0x80000000u && a < 0x80800000u && !(a & 3u); };
    auto r32 = [&](uint32_t a) -> uint32_t { return ok(a) || (a >= 0x80800000u && a < 0x81000000u && !(a & 3u)) ? rs64_rdram_u32(rd, a & 0x1FFFFFFFu) : 0u; };
    static std::vector<uint32_t> prev; static bool haveprev = false;
    std::vector<uint32_t> cur; uint32_t n = r32(0x801163B0u);
    while (n >= 0x80000000u && n < 0x81000000u && !(n & 3u) && cur.size() < 4096) { cur.push_back(n); n = r32(n); }
    if (selftest && begin == 100 && cur.size() > 5) {
        uint32_t t = cur[3]; volatile uint8_t* p = rd + ((t & 0x1FFFFFFFu) & ~3u); p[0] = p[1] = p[2] = p[3] = 0;
        std::fprintf(stderr, "[chunkcut] SELFTEST zeroed link of node %08X (idx 3 of %zu) at begin %lu\n", t, cur.size(), begin);
    }
    if (haveprev && len + 200 < (uint32_t)prev.size()) {
        uint32_t T = cur.empty() ? 0 : cur.back(); long idx = -1;
        for (size_t i = 0; i < prev.size(); ++i) if (prev[i] == T) { idx = (long)i; break; }
        std::fprintf(stderr, "[chunkcut] begin %lu prevlen=%zu walk=%zu (cap4096) T=%08X *T=%08X *(T+4)=%08X idxInPrev=%ld nextOld:", begin, prev.size(), cur.size(), T, r32(T), r32(T + 4), idx);
        if (idx >= 0) for (long k = idx + 1; k <= idx + 3 && k < (long)prev.size(); ++k) std::fprintf(stderr, " %08X(valid=%d)", prev[k], (int)(r32(prev[k] + 4) != 0 || prev[k] == prev.front()));
        size_t pin = 0; for (uint32_t a : prev) { bool f = false; for (uint32_t b : cur) if (a == b) { f = true; break; } if (!f) ++pin; }
        uint32_t blk = 0; for (uint32_t b : s_s6558_blocks) if (T >= b && T < b + 128u * 0x108u) blk = b;
        std::fprintf(stderr, " oldNodesGone=%zu Tblock=%08X Toff=%u\n", pin, blk, blk ? (T - blk) / 0x108u : 0u);
    }
    prev.swap(cur); haveprev = true;
}
static unsigned long s_s6559_begin = 0;
extern "C" volatile int g_s6559_pend = 0;
static struct { uint32_t pc, nv, oh; unsigned long b; } s_s6559_p;
static unsigned long s_s6559_push = 0, s_s6559_splice = 0, s_s6559_rows = 0;
extern "C" void rs64_s6559_tick(uint32_t pc, uint32_t addr, uint32_t value) {  /* s6559: resolve a pending off-chain head store at the next guest store to nv+0 (the push's link write) */
    if (addr != s_s6559_p.nv) return;
    g_s6559_pend = 0;
    if (value == s_s6559_p.oh) { ++s_s6559_push; return; }
    ++s_s6559_splice;
    if (s_s6559_rows < 300) { ++s_s6559_rows; std::fprintf(stderr, "[headwatch] SPLICE begin %lu headpc=%08X newhead=%08X oldhead=%08X link(pc=%08X)=%08X\n", s_s6559_p.b, s_s6559_p.pc, s_s6559_p.nv, s_s6559_p.oh, pc, value); }
}
static uint32_t s_s6560_tracked = 0; static bool s_s6560_have = false;
extern "C" void rs64_s6559_head(uint32_t pc, uint32_t nv) {  /* s6559: ROGUESQ_HEADWATCH=1 -> every guest store to the DL-chunk cache head 0x801163B0 (frames >= ROGUESQ_HEADWATCH_FROM, default 5900): classify pop (new head on old chain, idx<=50), far pop (idx>50), push (off-chain, next store to nv+0 == old head) or SPLICE (off-chain, link != old head) */
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_HEADWATCH"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static const unsigned long from = [] { const char* e = std::getenv("ROGUESQ_HEADWATCH_FROM"); return e ? (unsigned long)std::atol(e) : 5900ul; }();
    if (s_s6559_begin < from) return;
    volatile uint8_t* rd = g_recomp_rdram_for_wp_raw; if (!rd) return;
    auto r32 = [&](uint32_t a) -> uint32_t { return (a >= 0x80000000u && a < 0x81000000u && !(a & 3u)) ? rs64_rdram_u32(rd, a & 0x1FFFFFFFu) : 0u; };
    uint32_t oh = r32(0x801163B0u), n = oh; long idx = -1;
    for (long i = 0; i < 4096 && n >= 0x80000000u && n < 0x81000000u; ++i) { if (n == nv) { idx = i; break; } n = r32(n); }
    static unsigned long nnear = 0, nnull = 0; static unsigned long nfar = 0, farrows = 0;
    s_s6560_tracked = nv; s_s6560_have = true;
    if (nv == 0) ++nnull;
    else if (nv == r32(oh)) ++nnear;  /* plain pop: new head == old head's next */
    else if (r32(nv) == oh) ++s_s6559_push;  /* push, link written first */
    else if (idx < 0) { ++s_s6559_splice;
        /* s6561: heapWalker (0x800079F0) splices a per-mode list in FRONT of the free list (tail->next=oldhead; head=a0), so an off-chain nv is expected. The loss test is whether walk(nv) still reaches oh (old chain preserved) and how the lengths compare. */
        long reach = -1, lnv = 0, loh = 0; { uint32_t m = nv; for (long i = 0; i < 8192 && m >= 0x80000000u && m < 0x81000000u; ++i, ++lnv) { if (m == oh && reach < 0) reach = i; m = r32(m); } }
        { uint32_t m = oh; for (long i = 0; i < 8192 && m >= 0x80000000u && m < 0x81000000u; ++i, ++loh) m = r32(m); }
        static unsigned long nreach = 0, nnoreach = 0; if (reach >= 0) ++nreach; else ++nnoreach;
        if (s_s6559_rows < 120 || (nnoreach <= 40 && reach < 0)) { ++s_s6559_rows; std::fprintf(stderr, "[headwatch] OTHER begin %lu pc=%08X oh=%08X nv=%08X *oh=%08X *(oh+4)=%08X *nv=%08X *(nv+4)=%08X REACH=%ld lenNV=%ld lenOH=%ld tot_reach=%lu tot_noreach=%lu\n", s_s6559_begin, pc, oh, nv, r32(oh), r32(oh + 4), r32(nv), r32(nv + 4), reach, lnv, loh, nreach, nnoreach); } }
    else if (idx > 50) { ++nfar; if (farrows < 400) { ++farrows; std::fprintf(stderr, "[headwatch] FARPOP begin %lu pc=%08X newhead=%08X idx=%ld\n", s_s6559_begin, pc, nv, idx); } }
    else { ++nnear; static unsigned long i0 = 0, i2 = 0, isum = 0; if (idx == 0) ++i0; else { ++i2; isum += idx; if (i2 % 64 == 1) std::fprintf(stderr, "[headwatch] MIDPOP begin %lu pc=%08X idx=%ld (n=%lu sum=%lu noop0=%lu)\n", s_s6559_begin, pc, idx, i2, isum, i0); } }
    static std::map<uint32_t, unsigned long> bypc; if (nv && nv == r32(oh)) ++bypc[pc];
    static unsigned long lastdump = 0; if (s_s6559_begin >= lastdump + 20) { lastdump = s_s6559_begin; std::fprintf(stderr, "[headwatch] tally begin %lu near=%lu null=%lu push=%lu splice=%lu far=%lu\n", s_s6559_begin, nnear, nnull, s_s6559_push, s_s6559_splice, nfar); for (auto& kv : bypc) std::fprintf(stderr, "[headwatch]   pc=%08X pops=%lu\n", kv.first, kv.second); }
}
extern "C" int rs64_s6098_en(void) { static const int on = [] { const char* e = std::getenv("ROGUESQ_DLPOOLLOG"); return (e && e[0] && e[0] != '0') ? 1 : 0; }(); return on; }
extern "C" void rs64_s6098(int kind, uint32_t len, uint32_t tail, uint32_t ra) {  /* s6098: DL-chunk cache length at begin(0)/reclaim(1) entry */
    static unsigned long calls[2], zero[2]; static uint32_t minlen = 0xFFFFFFFFu, maxlen = 0, first = 0xFFFFFFFFu, last = 0; static unsigned long grew = 0;
    ++calls[kind & 1]; if (len == 0) ++zero[kind & 1];
    if (kind == 0) { s_s6559_begin = calls[0]; rs64_s6287_flush(calls[0], len); }
    { /* s6560: compare the hook-tracked head (last guest 'W' store seen by rs64_s6559_head) with the actual head at every begin/reclaim entry; a mismatch = a rewrite outside the hooked store path */
      static const bool hw = [] { const char* e = std::getenv("ROGUESQ_HEADWATCH"); return e && e[0] && e[0] != '0'; }();
      static const bool st = [] { const char* e = std::getenv("ROGUESQ_HEADWATCH_SELFTEST"); return e && e[0] && e[0] != '0'; }();
      volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
      if (hw && rd && s_s6559_begin >= 5800) {
        auto r32 = [&](uint32_t a) -> uint32_t { return (a >= 0x80000000u && a < 0x81000000u && !(a & 3u)) ? rs64_rdram_u32(rd, a & 0x1FFFFFFFu) : 0u; };
        auto walk = [&](uint32_t h) { long l = 0; while (l < 8192 && h >= 0x80000000u && h < 0x81000000u) { ++l; h = r32(h); } return l; };
        if (st && kind == 0 && s_s6559_begin == 6000) { uint32_t h = r32(0x801163B0u); uint32_t nn = r32(r32(h)); volatile uint8_t* q = rd + 0x1163B0u; q[0 ^ 3] = nn >> 24; q[1 ^ 3] = nn >> 16; q[2 ^ 3] = nn >> 8; q[3 ^ 3] = nn; std::fprintf(stderr, "[headwatch2] SELFTEST poked head %08X -> %08X\n", h, nn); }
        uint32_t act = r32(0x801163B0u);
        static unsigned long nmis = 0, nok = 0, rows = 0;
        if (s_s6560_have && act != s_s6560_tracked) { ++nmis; if (rows < 200) { ++rows; std::fprintf(stderr, "[headwatch2] MISMATCH kind=%d begin %lu actual=%08X tracked=%08X walk(actual)=%ld walk(tracked)=%ld lastpc=%08X ra=%08X (mis=%lu ok=%lu)\n", kind, s_s6559_begin, act, s_s6560_tracked, walk(act), walk(s_s6560_tracked), (uint32_t)g_rs64_last_guest_pc, ra, nmis, nok); } }
        else if (s_s6560_have) ++nok;
        s_s6560_tracked = act; s_s6560_have = true;  /* resync so each mismatch is a distinct event */
      }
    }
    if (kind == 0) rs64_s6558_cut(calls[0], len);
    { static uint32_t pl = 0xFFFFFFFFu; static std::map<uint32_t, std::pair<unsigned long, unsigned long>> by; /* ra -> (calls, chunks consumed) */
      if (kind == 0) { auto& e = by[ra]; ++e.first; if (pl != 0xFFFFFFFFu && pl > len) e.second += pl - len; pl = len; }
      if (kind == 0 && calls[0] % 1000 == 0) { std::fprintf(stderr, "[dlpool-ra] begin#%lu len=%u:", calls[0], len); for (auto& kv : by) std::fprintf(stderr, " ra=%08X n=%lu cons=%lu;", kv.first, kv.second.first, kv.second.second); std::fprintf(stderr, "\n"); } }
    if (first == 0xFFFFFFFFu) first = len;
    if (len > last && calls[0] + calls[1] > 1) ++grew;
    bool newmin = len < minlen, newmax = len > maxlen; if (newmin) minlen = len; if (newmax) maxlen = len; last = len;
    unsigned long n = calls[0] + calls[1];
    if (n <= 3 || newmin || (kind == 0 && len == 0 && zero[0] <= 20) || n % 2000 == 0)
        std::fprintf(stderr, "[dlpool] kind=%s len=%u tail=%08X begin=%lu reclaim=%lu empty_b=%lu empty_r=%lu first=%u min=%u max=%u grew=%lu\n", kind ? "reclaim" : "begin", len, tail, calls[0], calls[1], zero[0], zero[1], first, minlen, maxlen, grew);
}
static int s_s6287_on = -1; static std::map<uint32_t, unsigned long> s_s6287_pc[2];  /* s6287: per-begin-frame push(1)/pop(0) counts by guest pc at the DL-chunk cache head */
extern "C" void rs64_s6287(int kind, uint32_t pc) { if (s_s6287_on < 0) { const char* e = std::getenv("ROGUESQ_PPLOG"); s_s6287_on = (e && e[0] && e[0] != '0') ? 1 : 0; } if (s_s6287_on) ++s_s6287_pc[kind & 1][pc]; }
static void rs64_s6287_flush(unsigned long begin, uint32_t len) {
    if (s_s6287_on <= 0) return;
    static const unsigned long lo = [] { const char* e = std::getenv("ROGUESQ_PPLOG_LO"); return e ? (unsigned long)std::atol(e) : 38ul; }();
    static const unsigned long hi = [] { const char* e = std::getenv("ROGUESQ_PPLOG_HI"); return e ? (unsigned long)std::atol(e) : 48ul; }();
    if (begin >= lo && begin <= hi) {
        unsigned long tp = 0, tq = 0; for (auto& kv : s_s6287_pc[0]) tp += kv.second; for (auto& kv : s_s6287_pc[1]) tq += kv.second;
        std::fprintf(stderr, "[ppcount] frame_before_begin#%lu len_at_begin=%u pops=%lu pushes=%lu\n", begin, len, tp, tq);
        for (int k = 0; k < 2; ++k) { std::fprintf(stderr, "[ppcount]   %s:", k ? "push" : "pop"); int c = 0; for (auto& kv : s_s6287_pc[k]) if (kv.second >= 3 && c++ < 40) std::fprintf(stderr, " %08X=%lu", kv.first, kv.second); std::fprintf(stderr, "\n"); }
    }
    s_s6287_pc[0].clear(); s_s6287_pc[1].clear();
}
extern "C" int rs64_s6099_en(void) { static const int on = [] { const char* e = std::getenv("ROGUESQ_DLPOOLX"); return (e && e[0] && e[0] != '0') ? 1 : 0; }(); return on; }
static int s_s6286_armed = 0;  /* s6286: per-site grows must not touch the cache before beginFrameDLChunk has seen it initialised (topup at 0x80001F88 broke boot) */
extern "C" void rs64_s6286_arm(void) { s_s6286_armed = 1; }
extern "C" int rs64_s6286_armed_q(void) { return s_s6286_armed; }  /* s6288: the begin-time GROW hook was ungated and emptied the menu cache at begin 43 */
extern "C" int rs64_s6285_en(void) { static const int off = [] { const char* e = std::getenv("ROGUESQ_DLPOOLX_PRE"); return (e && std::atoi(e) > 0) ? 1 : 0; }(); return rs64_s6099_en() && !off && s_s6286_armed; }  /* s6286: per-site grows (b030/topup/finder-grow) are off when the one-shot pre-grow is requested */
extern "C" int rs64_s6286_pre(void) {  /* s6286: 0 until the AT-th beginFrameDLChunk call (ROGUESQ_DLPOOLX_AT, default 3000: past boot and level load, where early grows broke the game), then PRE chunks (or -1 = arm per-site grows only) */
    static const int pre = [] { const char* e = std::getenv("ROGUESQ_DLPOOLX_PRE"); return e ? std::atoi(e) : 0; }();
    static const int at = [] { const char* e = std::getenv("ROGUESQ_DLPOOLX_AT"); return e ? std::atoi(e) : 3000; }();
    static int calls = 0; if (++calls < at) return 0; if (!s_s6286_armed) std::fprintf(stderr, "[s7368] dlpoolx armed at begin %d\n", calls); s_s6286_armed = 1; return pre > 0 ? pre : -1; }
static uint32_t s_s6909_bump = 0;  /* s6909: arena high water, reset when the game rebuilds its chunk pool (tools/apply_s6909_dlreclaim.py) */
extern "C" void rs64_s6909_rebuild(void) {
    static const bool off = [] { const char* e = std::getenv("ROGUESQ_DLPOOLX_RECLAIM"); return e && e[0] == '0'; }();
    if (!rs64_s6099_en()) return;
    /* s7368: arm the per-site grows once the game has initialised its own chunk pool (this hook = buildAndRegisterDefaultMaterial's
       relink, head store at 0x80018094) instead of only at the AT-th beginFrameDLChunk (3000). The begin count is a frame-count proxy
       for "past boot": a slowed host or a quick player reaches a dd>1 3D scene in fewer game frames (TSan arm: ~330 frames at the
       mission), the fixed 1356-chunk pool runs dry with the arena unarmed (0 chunks held), the finder finds nothing and a NULL chunk
       is stored (allocateDisplayListBuffer / renderFlatMeshFaceGroup, si_addr 0x380000004). s6286's boot death was top-ups on the
       UNinitialised cache before this point. ROGUESQ_DLPOOLX_ARM_REBUILD=<n> arms at the n-th rebuild (default 1), 0 = old (AT only). */
    static const int arm_at = [] { const char* e = std::getenv("ROGUESQ_DLPOOLX_ARM_REBUILD"); return e ? std::atoi(e) : 1; }();
    static int nreb = 0; ++nreb;
    if (arm_at > 0 && nreb >= arm_at && !s_s6286_armed) { s_s6286_armed = 1; std::fprintf(stderr, "[s7368] dlpoolx armed at rebuild %d (pc=%08X)\n", nreb, (uint32_t)g_rs64_last_guest_pc); }
    std::fprintf(stderr, "[dlpoolx] rebuild: arena held %u chunks%s pc=%08X\n", s_s6909_bump / 0x108u, off ? " (kept)" : "", (uint32_t)g_rs64_last_guest_pc);
    if (!off) { s_s6909_bump = 0; s_s6558_blocks.clear(); }
}
/* s7335: the guest's own memory top. partitionFramebufferMemory (0x80000DD4) puts the scene framebuffers + gfx RDP FIFO at
   [top - fb, top) with top = 0x80000000|osMemSize (cfg+0x44 bit 0x2000 = 4 MB mode), and the persistent heap ends just below
   (0x801163E4, s7334). librecomp writes osMemSize from ROGUESQ_OSMEM_MB clamped to 4..16 (default 8; recomp.cpp s6114/s6130),
   mirrored here. Host arenas in 0x80800000..0x81000000 must start at or above it: with the dd>1 bundle (OSMEM 12, DLPOOLX 4)
   the DL arena starts exactly at 0x80C00000 = top, so DLPOOLX_MB 5..8 or OSMEM_MB 13..16 used to hand the guest's fb tail
   and heap top to the DL chunk pool. ROGUESQ_S7335_CLAMP=0 = old (no clamp). */
static uint32_t rs64_s7335_guest_top() {
    const char* e = std::getenv("ROGUESQ_OSMEM_MB"); int mb = (e && *e) ? std::atoi(e) : 8; if (mb < 4 || mb > 16) mb = 8;
    return 0x80000000u + ((uint32_t)mb << 20); }
static uint32_t rs64_s7335_dlpool_cap(uint32_t cap) {
    const char* off = std::getenv("ROGUESQ_S7335_CLAMP"); const uint32_t top = rs64_s7335_guest_top();
    const uint32_t lim = top < 0x81000000u ? 0x81000000u - top : 0u;
    std::fprintf(stderr, "[s7335] dlpool arena %08X..81000000 (%u KB) guest top %08X%s\n", 0x81000000u - cap, cap >> 10, top,
                 cap > lim ? ((off && off[0] == '0') ? " OVERLAP (clamp off)" : " overlap -> clamped") : "");
    if (cap > lim && !(off && off[0] == '0')) { cap = lim & ~0xFFFFu;
        std::fprintf(stderr, "[s7335] dlpool clamp -> %08X..81000000 (%u KB)\n", 0x81000000u - cap, cap >> 10); }
    return cap; }
/* s7336: host-arena layout census (tools/s7336_host_arena_table.py models the same rules over 9216 env combos). Every host arena
   that hands guest addresses to the game must (1) start at or above the guest top, (2) not overlap another host arena, (3) end at
   or below rs64_ram_top (the RS64_RAM_TOP pointer guards and RT64 reads reject anything above it, and rs_free's s6086 early return
   `ptr >= RS64_RAM_TOP` swallows its frees, so a spill block there leaks). Defaults (dd1, dd>1 bundle, OSMEM_MB=8 bundle) already
   pass; opt-in combos did not: legacy spill 0x80800000 under an OSMEM>8 guest top (s7335 only warned), DLPOOLX_MB 5..8 over the
   legacy spill arena, SPILL_HI or DLPOOLX without the matching RAMTOP_MB. Fixes: legacy spill moves to 0x81000000 when the guest
   top is above 0x80800000, DLPOOLX is clamped below the legacy spill end too, and rs64_ram_top is widened to the end of the arenas
   in use (max 0x81800000, librecomp's RAMTOP_MB 24 ceiling). ROGUESQ_S7336=0 = old. */
static bool rs64_s7336_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7336"); return !(e && e[0] == '0'); }(); return on; }
static uint32_t rs64_s6587_spill_base();
static uint32_t rs64_s7326_spill_cap();
static bool rs64_s7336_spill_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_MALLOC_SPILL"); return e && e[0] && e[0] != '0'; }(); return on; }
static void rs64_s7336_widen(uint32_t end, const char* who) {
    if (!rs64_s7336_on() || end <= rs64_ram_top) return;
    const uint32_t nt = end > 0x81800000u ? 0x81800000u : end;
    std::fprintf(stderr, "[s7336] ram_top %08X -> %08X (%s arena end %08X)\n", rs64_ram_top, nt, who, end); rs64_ram_top = nt; }
static uint32_t rs64_s7336_dlpool_cap() {
    static const uint32_t cap = [] { const char* e = std::getenv("ROGUESQ_DLPOOLX_MB"); int m = e ? std::atoi(e) : 1; if (m < 1) m = 1; if (m > 8) m = 8;
        uint32_t c = rs64_s7335_dlpool_cap((uint32_t)m << 20);
        if (rs64_s7336_on() && rs64_s7336_spill_on()) { const uint32_t sb = rs64_s6587_spill_base(), se = sb + rs64_s7326_spill_cap();
            if (sb < 0x81000000u && se > 0x81000000u - c) { const uint32_t nc = se < 0x81000000u ? ((0x81000000u - se) & ~0xFFFFu) : 0u;
                std::fprintf(stderr, "[s7336] dlpool %08X..81000000 overlaps spill %08X..%08X -> clamped to %08X..81000000 (%u KB)\n", 0x81000000u - c, sb, se, 0x81000000u - nc, nc >> 10); c = nc; } }
        rs64_s7336_widen(0x81000000u, "dlpool"); return c; }();
    return cap; }
extern "C" void rs64_s7336_layout() {  /* once, at the first rs_malloc: evaluate every arena, print the layout and any violation */
    static bool done = false; if (done) return; done = true;
    struct A { const char* n; uint32_t b, e; } a[3]; int na = 0;
    const uint32_t top = rs64_s7335_guest_top();
    if (rs64_s7336_spill_on()) { const uint32_t b = rs64_s6587_spill_base(); a[na++] = { "spill", b, b + rs64_s7326_spill_cap() }; }
    if (rs64_s6099_en()) { const uint32_t c = rs64_s7336_dlpool_cap(); a[na++] = { "dlpool", 0x81000000u - c, 0x81000000u }; }
    char buf[400]; int o = std::snprintf(buf, sizeof buf, "[s7336] layout guest 80000000..%08X ram_top %08X", top, rs64_ram_top);
    for (int i = 0; i < na; ++i) o = rs64_apf(buf, sizeof buf, o, " %s %08X..%08X", a[i].n, a[i].b, a[i].e);
    int bad = 0;
    for (int i = 0; i < na; ++i) { if (a[i].e <= a[i].b) continue;
        if (a[i].b < top) { o = rs64_apf(buf, sizeof buf, o, " OVERLAP %s/guest", a[i].n); ++bad; }
        if (a[i].e > rs64_ram_top) { o = rs64_apf(buf, sizeof buf, o, " GUARD %s", a[i].n); ++bad; }
        for (int j = i + 1; j < na; ++j) if (a[j].e > a[j].b && a[i].b < a[j].e && a[j].b < a[i].e) { o = rs64_apf(buf, sizeof buf, o, " OVERLAP %s/%s", a[i].n, a[j].n); ++bad; } }
    std::fprintf(stderr, "%s%s%s\n", buf, bad ? "" : " clean", rs64_s7336_on() ? "" : " (s7336 off)"); }
extern "C" uint32_t rs64_s6099_alloc(uint32_t ra) {  /* s6099/s6284: 128 DL chunks (0x108 B) from a bump arena ending at 0x81000000 (ROGUESQ_DLPOOLX_MB, default 1, max 4); 0 when exhausted */
    const uint32_t cap = rs64_s7336_dlpool_cap();  /* s6587/s7335/s7336: env cap, clamped to the guest top and the spill arena */
    uint32_t& bump = s_s6909_bump; const uint32_t bytes = 128u * 0x108u;
    if (bump + bytes > cap) { static int w = 0; if (!w++) std::fprintf(stderr, "[dlpoolx] arena exhausted (cap %u MB)\n", cap >> 20); return 0; }
    uint32_t p = (0x81000000u - cap) + bump; bump += bytes; s_s6558_blocks.push_back(p);
    std::fprintf(stderr, "[dlpoolx] +128 chunks at %08X (total %u) ra=%08X pc=%08X\n", p, bump / 0x108u, ra, (uint32_t)g_rs64_last_guest_pc);
    return p;
}
extern "C" void rs64_s6093_cnt(int w) { ++s_s6093_cnt[w & 7]; }
extern "C" void rs64_s6094_tick(uint8_t* rdram, uint32_t nbm, uint32_t basem) {  /* s6094: age histogram at each tickTextureMaterialExpiry entry */
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_BUCKETLOG"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static unsigned long nt = 0; ++nt;
    static int n2048 = 0; bool big = (nbm == 2048u) && n2048 < 40; if (big) ++n2048; if (!(nt <= 3 || (nt % 600) == 0 || big) || nt > 20000) return;
    auto rd = [&](uint32_t g) -> uint32_t { if (g < 0x80000000u || g >= 0x90000000u || (g & 3u)) return 0u; const uint8_t* q = rdram + (g - 0x80000000u); /* s7362: was rdram + (int32)g = rdram - 2 GB + phys (host memory) */ return ((uint32_t)q[0 ^ 3] << 24) | ((uint32_t)q[1 ^ 3] << 16) | ((uint32_t)q[2 ^ 3] << 8) | (uint32_t)q[3 ^ 3]; };
    uint32_t nb = nbm, base = basem;
    unsigned long hi8 = 0, ne = 0, a0 = 0, an = 0, sum = 0; unsigned mx = 0;
    for (uint32_t i = 0; i < nb && i < 16384; ++i) { uint32_t n = rd(base + 4 * i); int len = 0; while (n && len++ < 4096) { unsigned a = rd(n + 8) >> 16; ++ne; if (n >= rs64_ram_top) ++hi8; if (a) ++an; else ++a0; sum += a; if (a > mx) mx = a; n = rd(n); } }
    std::fprintf(stderr, "[bucketlog] s6095 visit=%lu agestore=%lu expire=%lu advance=%lu skip=%lu top=%lu\n", s_s6093_cnt[2], s_s6093_cnt[3], s_s6093_cnt[4], s_s6093_cnt[5], s_s6093_cnt[6], s_s6093_cnt[7]);
    std::fprintf(stderr, "[bucketlog] s6094 tick#%lu nb=%u base=%08X ent=%lu age0=%lu agenz=%lu sumage=%lu maxage=%u nodes_ge_8MB=%lu\n", nt, nb, base, ne, a0, an, sum, mx, hi8);
}
extern "C" void rs64_s6088_fuse(uint8_t* rdram, uint32_t ret, uint32_t ra, uint32_t gcount, uint32_t gbase, uint32_t gcache) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_BUCKETLOG"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    { static uint32_t lastnb = 0xFFFFFFFFu, lastbase = 0; static int chg = 0;
      uint32_t nb0 = gcount, b0 = gbase;
      if ((nb0 != lastnb || b0 != lastbase) && chg++ < 20) std::fprintf(stderr, "[bucketlog] CHANGE nb %u->%u base %08X->%08X ret=%08X ra=%08X ncall_next\n", lastnb, nb0, lastbase, b0, ret, ra);
      lastnb = nb0; lastbase = b0; }
    static unsigned long ncall = 0, nzero = 0; static int dumps = 0;
    ++ncall; if (!ret) ++nzero;
    bool want = (!ret && nzero <= 3) || ncall == 1 || (ncall & 4095u) == 0;
    if (!want || dumps >= 40) return;
    ++dumps;
    auto rd = [&](uint32_t g) -> uint32_t { if (g < 0x80000000u || g >= rs64_ram_top || (g & 3u)) return 0u; const uint8_t* q = rdram + (g - 0x80000000u); /* s7362: was rdram + (int32)g = rdram - 2 GB + phys (host memory) */ return ((uint32_t)q[0 ^ 3] << 24) | ((uint32_t)q[1 ^ 3] << 16) | ((uint32_t)q[2 ^ 3] << 8) | q[3 ^ 3]; };
    uint32_t nb = gcount, base = gbase;
    std::fprintf(stderr, "[bucketlog] raw: macro count=%u base=%08X cache=%08X | s5042_rd count=%u base=%08X cache=%08X\n", gcount, gbase, gcache, rd(0x8012EEF0u) >> 16, rd(0x8012F000u), rd(0x801163B0u));
    unsigned long totc = 0, nz = 0, nent = 0, a0n = 0, a1n = 0, a2n = 0, maxlen = 0; unsigned maxage = 0; char buf[512]; int o = 0; /* s6092: scan ALL buckets + age histogram */
    for (uint32_t i = 0; i < nb && i < 16384; ++i) {
        uint32_t n = rd(base + 4 * i); unsigned len = 0, cs = 0;
        while (n && len < 4096) { unsigned age = rd(n + 8) >> 16; cs += age; ++len; ++nent; if (age == 0) ++a0n; else if (age < 16) ++a1n; else ++a2n; if (age > maxage) maxage = age; n = rd(n); }
        totc += cs; if (len) ++nz; if (len > maxlen) maxlen = len;
        if (i < 40 && o < 480) o = rs64_apf(buf, sizeof buf, o, "%u:%u/%u ", i, len, cs);
    }
    std::fprintf(stderr, "[bucketlog] s6092 all: entries=%lu age0=%lu age1_15=%lu age16+=%lu maxage=%u maxchain=%lu\n", nent, a0n, a1n, a2n, maxage, maxlen);
    std::fprintf(stderr, "[bucketlog] s6093 tickcalls=%lu resetcalls=%lu\n", s_s6093_cnt[0], s_s6093_cnt[1]);
    std::fprintf(stderr, "[bucketlog] call=%lu zero=%lu ret=%08X ra=%08X nbuckets=%u nonempty=%lu totcnt=%lu cachehead=%08X live=0x%llX peak=0x%llX | %s\n",
        ncall, nzero, ret, ra, nb, nz, totc, rd(0x801163B0u), (unsigned long long)s_s6063_bytes, (unsigned long long)s_s6063_peak, buf);
}
static uint32_t s_s6086_expect = 0, s_s6086_bump = 0;
extern "C" void rs64_s6086_arm(uint32_t o, uint32_t n) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_BIGARENA"); return e && e[0] && e[0] != '0'; }();
    if (on && n > o) { s_s6086_expect = n * 184u; s_s6086_bump = 0; }
}
/* s7328: ROGUESQ_SPILL_FORCE=<hex>[,<hex>...] and/or min:<hex> serves matching rs_malloc requests from the spill arena BEFORE the
   main heap is tried (needs ROGUESQ_MALLOC_SPILL, which main.cpp sets for dd>1). Experiment lever only: it places a chosen block (e.g.
   the dd8 0x2DFF00 grid-layer buffer that only the hangar route spills, s7327) above 16 MB on the deterministic forced-level route, so
   same-pose arms can test what reads it. The block skips the s5041/s6063 malloc hooks (as the s6086 divert does) and its s7326 reset
   tag is the previous call's a1 (rs64_s6127_fl runs after the divert). Every request >= 1 MB is logged with the decision. Unset = off. */
extern "C" uint32_t rs64_s6569_spill(uint32_t req);
static bool s7328_force(uint32_t req) {
    static std::vector<uint32_t> lst; static uint32_t mn = 0;
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_SPILL_FORCE"); if (!e || !e[0]) return false;
        std::string s(e); size_t i = 0; while (i < s.size()) { size_t j = s.find(',', i); if (j == std::string::npos) j = s.size();
            std::string w = s.substr(i, j - i); if (w.rfind("min:", 0) == 0) mn = (uint32_t)std::strtoul(w.c_str() + 4, nullptr, 16);
            else if (!w.empty()) lst.push_back((uint32_t)std::strtoul(w.c_str(), nullptr, 16)); i = j + 1; }
        std::fprintf(stderr, "[s7328] spill force list=%zu min=0x%X\n", lst.size(), mn); return true; }();
    if (!on) return false;
    bool hit = (mn && req >= mn); for (uint32_t v : lst) hit |= (v == req);
    if (req >= 0x100000u) std::fprintf(stderr, "[s7328] big req=0x%X force=%d\n", req, hit ? 1 : 0);
    return hit;
}
extern "C" uint32_t rs64_s6086_divert(uint32_t req) {
    rs64_s7336_layout();
    if (s7328_force(req)) { uint32_t p = rs64_s6569_spill(req); std::fprintf(stderr, "[s7328] forced req=0x%X -> %08X\n", req, p); if (p) return p; }
    if (!s_s6086_expect || req != s_s6086_expect) return 0;
    s_s6086_expect = 0;
    uint32_t p = rs64_ram_top + s_s6086_bump; s_s6086_bump += (req + 15u) & ~15u;
    std::fprintf(stderr, "[bigarena] pool req=0x%X -> %08X\n", req, p);
    return p;
}
static uint32_t s_s6569_bump = 0;
static std::mutex s_s6702_mu;
static std::map<uint32_t, uint32_t> s_s6702_free, s_s6702_live;  /* s6702: spill free list / live blocks, addr -> rounded size */
static uint32_t s_s6702_live_bytes = 0; static unsigned long s_s6702_reused = 0, s_s6702_freed = 0;
static std::map<uint32_t, uint32_t> s_s7326_tag;  /* s7326: spill block -> rs_malloc a1 recorded at spill time (guarded by s_s6702_mu) */
static std::map<uint32_t, uint32_t> s_s7326_released;  /* s7326: blocks released by the scene reset, until reallocated (post-reset rs_free detector) */
static unsigned long s_s7326_rel_n = 0, s_s7326_rel_post = 0; static uint64_t s_s7326_rel_bytes = 0;
/* s6893 G5a: every spill event in a ring with the guest malloc ra, dumped when the s6892 guard fires, so the block that
   overran or stayed in use after a free can be read back. rs64_s6893_ra is set by the rs_malloc hook. */
struct S6893Ev { uint32_t op, req, p, ra; };
static S6893Ev s6893_ring[1u << 16]; static uint32_t s6893_n = 0;
extern "C" { uint32_t rs64_s6893_ra = 0; }
static inline void s6893_ev(uint32_t op, uint32_t req, uint32_t p) { s6893_ring[s6893_n++ & 0xFFFFu] = { op, req, p, rs64_s6893_ra }; }
static uint32_t rs64_s6587_spill_base() { static const uint32_t b = [] { const char* e = std::getenv("ROGUESQ_SPILL_HI"); uint32_t v = (e && e[0] && e[0] != '0') ? 0x81000000u : 0x80800000u;
    if (v == 0x80800000u && rs64_s7336_on() && rs64_s7335_guest_top() > v) { std::fprintf(stderr, "[s7336] legacy spill 80800000 below guest top %08X -> 81000000\n", rs64_s7335_guest_top()); v = 0x81000000u; }
    return v; }(); return b; }  /* s6587: spill arena above the RSP-visible 16 MB so the DL pool can take 8 MB */
/* s7326: spill arena size. 4 MB (s6569) was too small for the dd8 21:9 hangar-route mission load (0x1E000C + 0x2DFF00 after the
   scene reset, s7326 arm b: "[spill] arena full" -> rs_malloc NULL -> SIGBUS). With the 0x81000000 layout the arena is 8 MB
   (0x81000000-0x81800000; main.cpp sets ROGUESQ_RAMTOP_MB=24, librecomp's maximum, so the pointer guards accept it), clamped to
   rs64_ram_top. ROGUESQ_SPILL_MB=<n> overrides (4 = old). The 0x80800000 legacy layout keeps 4 MB (game heap starts at 0x80C00000 there). */
extern "C" uint32_t rs64_ram_top;
extern "C" int rs64_standins_on(void);  /* s7623 G6c, src/main/rs64_standins.cpp */
static uint32_t rs64_s7326_spill_cap() {
    static const uint32_t c = [] { const uint32_t b = rs64_s6587_spill_base(); uint32_t mb = b == 0x81000000u ? 8u : 4u;
        if (const char* e = std::getenv("ROGUESQ_SPILL_MB")) { int v = std::atoi(e); if (v >= 1 && v <= 16) mb = (uint32_t)v; }
        uint32_t cap = mb << 20; if (b == 0x81000000u && rs64_ram_top <= b) rs64_s7336_widen(b + cap, "spill");  /* s7336: SPILL_HI without RAMTOP_MB */
        if (b == 0x81000000u && rs64_ram_top > b && b + cap > rs64_ram_top) cap = rs64_ram_top - b;
        if (b != 0x81000000u && cap > 0x400000u) cap = 0x400000u;
        { if (b == 0x81000000u && rs64_standins_on() && cap > 0x700000u) { cap = 0x700000u;  /* s7623 G6c: top 1 MB = stand-in region 0x81700000 */
            std::fprintf(stderr, "[s7623] spill arena capped at 7 MB for the stand-in region 81700000..81800000\n"); } }
        if (b != 0x81000000u) rs64_s7336_widen(b + cap, "spill");  /* s7336: legacy spill without RAMTOP_MB 16 */
        if (b < rs64_s7335_guest_top()) std::fprintf(stderr, "[s7335] WARNING spill arena %08X below guest top %08X: overlaps the guest heap / fb tail (set ROGUESQ_SPILL_HI=1)\n", b, rs64_s7335_guest_top());
        std::fprintf(stderr, "[s7326] spill arena %08X..%08X (%u KB, ram_top %08X)\n", b, b + cap, cap >> 10, rs64_ram_top); return cap; }();
    return c; }
extern "C" uint32_t rs64_s6569_spill(uint32_t req) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_MALLOC_SPILL"); return e && e[0] && e[0] != '0'; }();
    if (!on || !req) return 0;
    uint32_t sz = (req + 15u) & ~15u;
    std::lock_guard<std::mutex> lk(s_s6702_mu);
    /* s6702: reuse freed spill blocks (first fit, split) before bumping; s6569 leaked every block and lvl1 dd8 filled 4 MB in 219 s */
    for (auto it = s_s6702_free.begin(); it != s_s6702_free.end(); ++it) {
        if (it->second < sz) continue;
        uint32_t p = it->first, rest = it->second - sz;
        s_s6702_free.erase(it); if (rest) s_s6702_free[p + sz] = rest;
        s_s6702_live[p] = sz; s_s6702_live_bytes += sz; ++s_s6702_reused; s6893_ev(1, req, p);
        s_s7326_tag[p] = g_s6127_flags; s_s7326_released.erase(p);
        if ((s_s6702_reused & 255u) == 1) std::fprintf(stderr, "[spill] reuse#%lu req=0x%X -> %08X live=0x%X bump=0x%X freeblk=%zu\n", s_s6702_reused, req, p, s_s6702_live_bytes, s_s6569_bump, s_s6702_free.size());
        return p;
    }
    if (s_s6569_bump + sz > rs64_s7326_spill_cap()) { std::fprintf(stderr, "[spill] req=0x%X arena full live=0x%X freeblk=%zu\n", req, s_s6702_live_bytes, s_s6702_free.size()); return 0; }
    uint32_t p = rs64_s6587_spill_base() + s_s6569_bump; s_s6569_bump += sz;
    s_s6702_live[p] = sz; s_s6702_live_bytes += sz; s6893_ev(0, req, p);
    s_s7326_tag[p] = g_s6127_flags; s_s7326_released.erase(p);
    /* s7446 class DC: the per-request bump line (752 lines / ~41 KB in one second at mission load, owner recipe) is latched on
       ROGUESQ_SPILL_LOG=1 (or ROGUESQ_G1E_TRIM=0 = old). Placement stays recorded in the s6893 ring and ROGUESQ_S7317_ALLOCMAP;
       the arena-full crash breadcrumb and the 1-in-256 reuse/free summaries stay unconditional. */
    static const bool s7446_log = [] { const char* e = std::getenv("ROGUESQ_SPILL_LOG"), *g = std::getenv("ROGUESQ_G1E_TRIM");
        return (e && e[0] == '1') || (g && g[0] == '0'); }();
    if (s7446_log) std::fprintf(stderr, "[spill] req=0x%X -> %08X (used 0x%X live 0x%X)\n", req, p, s_s6569_bump, s_s6702_live_bytes);
    return p;
}
extern "C" void rs64_s6570_svcnull(char k, uint32_t a, uint32_t ra, uint32_t b) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_SVCNULL"); return e && e[0] && e[0] != '0'; }();
    static int n = 0; if (!on || n >= 60) return; ++n;
    std::fprintf(stderr, "[svcnull] %c a=%08X ra=%08X b=%08X\n", k, a, ra, b);
}
static bool g_s6571_last_null = false;
extern "C" void rs64_s6571_svc(char k, uint32_t a, uint32_t b, uint32_t c, uint32_t d) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_SVCNULL"); return e && e[0] && e[0] != '0'; }();
    static int nr = 0, nt = 0, nrall = 0;
    if (!on) return;
    if (k == 'T') { if (nt++ >= 60) return; std::fprintf(stderr, "[svcstop] T svc=%08X ra=%08X flag=%02X queue=%08X\n", a, b, c, d); return; }
    if (k == 'q') { static int nq = 0; if (c != 0 || d != 0 || nq >= 40) { /* only print when the preceding 'r' printed a null slot */ } 
        if (g_s6571_last_null && nq++ < 40) std::fprintf(stderr, "[svcq] svc=%08X first|msgCount<<16=%08X msgbuf=%08X buf[0]=%08X\n", a, b, c, d);
        g_s6571_last_null = false; return; }
    /* 'r': after osRecvMesg: a=svc b=osRecvMesg retval c=slot d=validCount; log all for svc 0x80954F60 (first 12) + every empty slot (first 40) */
    if (c == 0) { if (nr++ >= 40) return; } else if (a == 0x80954F60u) { if (nrall++ >= 12) return; } else return;
    if (c == 0) g_s6571_last_null = true;
    std::fprintf(stderr, "[svcrecv] r svc=%08X ret=%08X slot=%08X validCount=%u\n", a, b, c, d);
}
/* s6702 release of a live spill block into the coalescing free list; caller holds s_s6702_mu. */
static void s6702_release_locked(std::map<uint32_t, uint32_t>::iterator lv) {
    const uint32_t b = rs64_s6587_spill_base(), p = lv->first, sz = lv->second;
    s_s6702_live.erase(lv); s_s6702_live_bytes -= sz; ++s_s6702_freed; s6893_ev(2, sz, p); s_s7326_tag.erase(p);
    s7317_free(p);
    auto it = s_s6702_free.emplace(p, sz).first;  /* coalesce with neighbours */
    if (it != s_s6702_free.begin()) { auto pv = std::prev(it); if (pv->first + pv->second == it->first) { pv->second += it->second; s_s6702_free.erase(it); it = pv; } }
    auto nx = std::next(it); if (nx != s_s6702_free.end() && it->first + it->second == nx->first) { it->second += nx->second; s_s6702_free.erase(nx); }
    if (it->first + it->second == b + s_s6569_bump) { s_s6569_bump = it->first - b; s_s6702_free.erase(it); }  /* top block returns to the bump */
}
/* s7326: retail scene reset for spill blocks. coalesceFreeHeapBlocks (0x800022F8) frees EVERY used persistent-heap block whose header
   tag lacks 0x80 (rs_malloc a1 & 0x88 -> tag), whatever its a0. Spill blocks are outside the guest chain, so before s7326 they survived:
   s7326 run a, dd8 21:9 hangar route, loadLevelAssets' 0x2DFF00 (a1 tag 0) outlived the reset that precedes the mission load, the
   game's next 0x1E000C / 0x2DFF00 requests found the 4 MB arena full, rs_malloc returned NULL and emitGridCellTileStrip faulted.
   Called from the coalesce wrapper (before the ALLOCMAP-gated re-sync): releases every live spill block whose recorded a1 has neither
   0x80 (persistent) nor 0x04 (temp pool, which retail drops at its own rebuild). ROGUESQ_SPILL_RESET=0 = old (blocks survive). */
static std::vector<std::pair<uint32_t, uint32_t>> s7331_q; static uint64_t s7331_sync = 0;  /* s7331: spill blocks released at this reset */
extern "C" void rs64_s7326_spill_reset(uint32_t a0) {
    static const bool off = [] { const char* e = std::getenv("ROGUESQ_SPILL_RESET"); return e && e[0] == '0'; }();
    if (off) return;
    std::lock_guard<std::mutex> lk(s_s6702_mu);
    if (s_s6702_live.empty()) return;
    unsigned long n = 0; uint64_t bytes = 0; uint32_t big = 0, bigp = 0;
    for (auto it = s_s6702_live.begin(); it != s_s6702_live.end();) {
        auto tg = s_s7326_tag.find(it->first); const uint32_t fl = tg != s_s7326_tag.end() ? tg->second : 0x80u;  /* unknown tag: keep */
        if (fl & 0x84u) { ++it; continue; }
        auto nx = std::next(it); const uint32_t p = it->first, sz = it->second;
        ++n; bytes += sz; if (sz > big) { big = sz; bigp = p; }
        if (rs64_s7331_on) s7331_q.push_back({p, sz});  /* s7331: tracked after the lock drops */
        s6702_release_locked(it); s_s7326_released[p] = sz; it = nx; }
    s_s7326_rel_n += n; s_s7326_rel_bytes += bytes;
    if (n) { static int nl = 0; if (nl++ < 400) std::fprintf(stderr, "[s7326] spill reset a0=%X released %lu blocks 0x%llX bytes (largest 0x%X at %08X) | live now 0x%X bump=0x%X | total %lu blocks 0x%llX, post-reset rs_free %lu\n",
        a0, n, (unsigned long long)bytes, big, bigp, s_s6702_live_bytes, s_s6569_bump, s_s7326_rel_n, (unsigned long long)s_s7326_rel_bytes, s_s7326_rel_post); }
}
/* Called only from the rs_free hook (apply_s6569_spill.py F_NEW): a spill pointer is released here, then rs_free returns. */
extern "C" int rs64_s6569_isspill(uint32_t p) {
    uint32_t b = rs64_s6587_spill_base(); if (!(p >= b && p < b + rs64_s7326_spill_cap())) return 0;
    static const bool legacy = [] { const char* e = std::getenv("ROGUESQ_SPILL_LEAK"); return e && e[0] && e[0] != '0'; }();  /* =1: s6569 leak behaviour */
    if (legacy) return 1;
    std::lock_guard<std::mutex> lk(s_s6702_mu);
    auto lv = s_s6702_live.find(p);
    if (lv == s_s6702_live.end()) { static int nb = 0;
        if (s_s7326_released.count(p)) { ++s_s7326_rel_post; static int np = 0; if (np++ < 40) std::fprintf(stderr, "[s7326] rs_free of %08X after the scene reset released it (ignored, not reallocated)\n", p); return 1; }
        if (nb++ < 20) std::fprintf(stderr, "[spill] free of unknown/double-freed %08X ignored\n", p); return 1; }
    uint32_t sz = lv->second; s6702_release_locked(lv);
    if ((s_s6702_freed & 255u) == 1) std::fprintf(stderr, "[spill] free#%lu %08X sz=0x%X live=0x%X bump=0x%X freeblk=%zu\n", s_s6702_freed, p, sz, s_s6702_live_bytes, s_s6569_bump, s_s6702_free.size());
    return 1;
}
/* s6893: full evidence on the first guard fire: RDRAM to 20 MB, spill event ring, live map. Runs once, from build/. */
/* s6893 G5a root cause: see tools/apply_s6893_tilepool.py. K = ceil(dd)^2, x2 for wide; ROGUESQ_TILEPOOL_K overrides, ROGUESQ_TILEPOOL=0 = old. */
static uint32_t s6893_base = 0, s6893_cap = 0, s6893_max = 0; static unsigned s6893_lines = 0;
static bool s6893_pool_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_TILEPOOL"); return !(e && *e == '0'); }(); return on; }
extern "C" uint32_t rs64_s6893_tilepool_size(uint32_t req) {
    if (!s6893_pool_on()) return req;
    static const uint32_t k = [] {
        if (const char* e = std::getenv("ROGUESQ_TILEPOOL_K")) { int v = std::atoi(e); if (v >= 1) return (uint32_t)v; }
        const char* d = std::getenv("ROGUESQ_DRAW_DISTANCE"); double dd = (d && *d) ? std::atof(d) : 1.0; uint32_t px = dd > 1.0 ? (uint32_t)std::ceil(dd) : 1u; if (!(px <= 8u)) px = 8u; /* s7358: terrain clamps dd at 8 (apply_s6036_dd); k=ceil(dd)^2*2 past it overflowed the spill arena */
        const char* w = std::getenv("ROGUESQ_FB_WIDTH");
        return px * px * ((w && std::atoi(w) > 640) ? 2u : 1u); }();
    s6893_base = req / 25u; s6893_cap = s6893_base * k; s6893_max = 0;
    std::fprintf(stderr, "[s6893] tile pool entries %u -> %u (k=%u)\n", s6893_base, s6893_cap, k);
    return req * k;
}
extern "C" uint32_t rs64_s6893_tileslot(uint32_t count) {
    static const uint32_t add = [] { const char* e = std::getenv("ROGUESQ_TILEPOOL_TESTADD"); return e ? (uint32_t)std::atoi(e) : 0u; }();  /* test lever: forces the overflow on demand */
    count += add;
    if (!s6893_cap) return count;
    if (count > s6893_max) { s6893_max = count; if (count >= s6893_base / 2u && s6893_lines++ < 200) std::fprintf(stderr, "[s6893] tile count %u of retail %u (cap %u)\n", count + 1, s6893_base, s6893_cap); }
    return count < s6893_cap ? count : s6893_cap - 1;
}
/* s6911 G5h: see tools/apply_s6911_varclamp.py. idx = x + z * w as the game computed it; clamps x,z to the map at dd>1. ROGUESQ_DD_VARCLAMP=0 old, =tog odd seconds. */
extern "C" int32_t rs64_s6911_mapidx(int32_t idx, int32_t x, int32_t z, uint32_t w, uint32_t h) {
    extern volatile int g_rs64_dd_scene;
    static const int mode = [] { const char* e = std::getenv("ROGUESQ_DD_VARCLAMP"); const char* d = std::getenv("ROGUESQ_DRAW_DISTANCE");
        if (!(d && std::atof(d) > 1.0)) return 0; return !(e && *e) ? 1 : *e == '0' ? 0 : *e == 't' ? 2 : 1; }();
    static const int lg = [] { const char* e = std::getenv("ROGUESQ_DD_VARCLAMP_LOG"); return e && *e != '0'; }();
    if (x >= 0 && z >= 0 && x < (int32_t)w && z < (int32_t)h) return idx;
    static uint64_t seen = 0, fixed = 0; seen++;
    const bool on = mode == 2 ? ((mach_absolute_time() / 24000000ull) & 1) != 0 : mode != 0;
    const bool act = on && g_rs64_dd_scene && w && h;
    if (act) fixed++;
    static uint32_t lw = 0, lh = 0; /* one line per map change: the 40 line budget hid every level after the first (s6913) */
    if (lg && (w != lw || h != lh)) { lw = w; lh = h; std::fprintf(stderr, "[s6911map] map %ux%u first off-map x=%d z=%d seen %llu\n", w, h, x, z, (unsigned long long)seen); }
    if (lg && (seen <= 40 || (seen & 0xFFF) == 0)) std::fprintf(stderr, "[s6911] off-map variant x=%d z=%d map %ux%u raw idx %d on=%d seen %llu fixed %llu\n", x, z, w, h, idx, act ? 1 : 0, (unsigned long long)seen, (unsigned long long)fixed);
    if (!act) return idx;
    const int32_t cx = x < 0 ? 0 : x >= (int32_t)w ? (int32_t)w - 1 : x, cz = z < 0 ? 0 : z >= (int32_t)h ? (int32_t)h - 1 : z;
    return cx + cz * (int32_t)w;
}
extern "C" void rs64_s6893_dump(const uint8_t* rdram) {
    static bool done = false; if (done) return; done = true;
    if (const char* e = std::getenv("ROGUESQ_S6892_DUMP")) if (*e == '0') return;
    if (FILE* f = fopen("rs64_s6893_rdram.bin", "wb")) { fwrite(rdram, 1, 0x1400000u, f); fclose(f); }
    std::lock_guard<std::mutex> lk(s_s6702_mu);
    if (FILE* f = fopen("rs64_s6893_spill.txt", "w")) {
        uint32_t n = s6893_n, c = n < 65536u ? n : 65536u;
        for (uint32_t i = n - c; i != n; ++i) { const S6893Ev& e = s6893_ring[i & 0xFFFFu]; fprintf(f, "ev %u op=%u req=%X p=%08X ra=%08X\n", i, e.op, e.req, e.p, e.ra); }
        for (auto& kv : s_s6702_live) fprintf(f, "live %08X %X\n", kv.first, kv.second);
        for (auto& kv : s_s6702_free) fprintf(f, "free %08X %X\n", kv.first, kv.second);
        fclose(f);
    }
}
extern "C" void rs64_s5041_malloc(uint32_t ptr) {
    if (!s5041_on() || ptr == 0) return;
    s_s5041_freed.erase(ptr);
}

static inline uint32_t s5042_rd(const uint8_t* rd, uint32_t off) { return ((uint32_t)rd[off ^ 3u] << 24) | ((uint32_t)rd[(off + 1) ^ 3u] << 16) | ((uint32_t)rd[(off + 2) ^ 3u] << 8) | rd[(off + 3) ^ 3u]; }

static uint8_t* g_s6127_rd_fwd();
static void s6127_walk(uint32_t req, bool ok) {  /* s6127: walk both guest heaps (heads 0x8010FEFC, 0x80110018); hdr: u16 flags(1=free,2=used,8=end) u16 tag u32 size, 16B hdr */
    static int n = 0, nok = 0; if (ok) { if (nok++ >= 40) return; } else if (n++ >= 3) return;
    uint8_t* rd = g_s6127_rd_fwd(); if (!rd) { std::fprintf(stderr, "[heapwalk] no rdram yet\n"); return; }
    for (int h = 0; h < 2; ++h) {
        uint32_t head = s5042_rd(rd, (h ? 0x8010FF18u : 0x8010FF00u) - 0x80000000u);
        uint64_t freeb = 0, usedb = 0; uint32_t nfree = 0, nused = 0, big[5] = {0,0,0,0,0}; uint32_t a = head, first = head, last = 0; int guard = 0; struct UB { uint32_t sz, addr, tag; } ub[10] = {}; /* s6128: top used blocks */
        if (!ok) std::fprintf(stderr, "[heapwalk] heap%d ptr-slot=%08X (0x8010FEFC=%08X 0x80110018=%08X)\n", h, head, s5042_rd(rd, 0x10FF00u), s5042_rd(rd, 0x10FF18u));
        if (head < 0x80000000u || head >= rs64_ram_top) { std::fprintf(stderr, "[heapwalk] heap%d head=%08X (out of range)\n", h, head); continue; }
        while (a >= 0x80000000u && a < rs64_ram_top && guard++ < 200000) {
            uint32_t w0 = s5042_rd(rd, a - 0x80000000u), sz = s5042_rd(rd, a - 0x80000000u + 4); uint16_t fl = w0 >> 16;
            last = a; if (guard <= 12 && !ok) std::fprintf(stderr, "[heapwalk]   h%d blk@%08X w0=%08X size=%08X\n", h, a, w0, sz);
            if (fl & 1) { ++nfree; freeb += sz; for (int i = 0; i < 5; ++i) if (sz > big[i]) { for (int j = 4; j > i; --j) big[j] = big[j-1]; big[i] = sz; break; } } else { ++nused; usedb += sz; for (int i = 0; i < 10; ++i) if (sz > ub[i].sz) { for (int j = 9; j > i; --j) ub[j] = ub[j-1]; ub[i] = { sz, a, (uint32_t)(w0 & 0xFFFFu) }; break; } }
            if (fl & 8) break;
            if (sz == 0 || sz > (rs64_ram_top - 0x80000000u)) { std::fprintf(stderr, "[heapwalk] heap%d BAD size %08X at %08X fl=%04X\n", h, sz, a, fl); break; }
            a = a + 0x10 + sz;
        }
        if (h == 1) { std::fprintf(stderr, "[heapwalk-top]%s used>=:", ok ? "(1000ok)" : ""); for (int i = 0; i < 10; ++i) if (ub[i].sz) std::fprintf(stderr, " %X@%08X/t%X", ub[i].sz, ub[i].addr, ub[i].tag); std::fprintf(stderr, "\n"); }
        if (!(ok && h == 0)) std::fprintf(stderr, "[heapwalk]%s req#%d heap%d start=%08X lastblk=%08X end~%08X nfree=%u free=0x%llX nused=%u used=0x%llX top5free=%X,%X,%X,%X,%X\n", ok ? "(1000ok)" : "", n, h, first, last, a, nfree, (unsigned long long)freeb, nused, (unsigned long long)usedb, big[0], big[1], big[2], big[3], big[4]);
    }
}
static uint8_t* g_s6127_rd_fwd() { return g_s6127_rd; }
static void s6129_dump(const char* why, uint32_t from) {  /* s6129: list every main-heap block at/after `from` (hdr: u16 flags,u16 tag,u32 size,16B hdr) */
    uint8_t* rd = g_s6127_rd; if (!rd) return;
    uint32_t a = s5042_rd(rd, 0x10FF00u); int g = 0, shown = 0; uint32_t endsent = s5042_rd(rd, 0x10FF00u);
    std::fprintf(stderr, "[s6129] %s head=%08X slotE8=%08X top-ptrs 63D8=%08X 63DC=%08X 63E0=%08X 63E4=%08X 63F8=%08X\n", why, endsent, s5042_rd(rd, 0x10FF18u), s5042_rd(rd, 0x1163D8u), s5042_rd(rd, 0x1163DCu), s5042_rd(rd, 0x1163E0u), s5042_rd(rd, 0x1163E4u), s5042_rd(rd, 0x1163F8u));
    while (a >= 0x80000000u && a < rs64_ram_top && g++ < 200000) {
        uint32_t w0 = s5042_rd(rd, a - 0x80000000u), sz = s5042_rd(rd, a - 0x80000000u + 4); uint16_t fl = w0 >> 16;
        if (a >= from && shown < 48) { ++shown; std::fprintf(stderr, "[s6129]   blk@%08X fl=%04X tag=%04X size=%X\n", a, fl, w0 & 0xFFFF, sz); }
        if ((fl & 8) || sz == 0 || sz > (rs64_ram_top - 0x80000000u)) { std::fprintf(stderr, "[s6129]   END blk@%08X fl=%04X size=%X (nblk walked=%d)\n", a, fl, sz, g); break; }
        a += 0x10 + sz;
    }
}
extern "C" void rs64_s5042_poison(uint8_t* rdram, uint32_t ptr, uint32_t ra) {
    g_s6127_rd = rdram; /* s6127: stash rdram for the NULL-path freelist walk */
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_FREE_POISON"); return e && e[0] && e[0] != '0'; }();
    if (!on || ptr < 0x80000010u || ptr >= rs64_ram_top || (ptr & 3u)) return;
    static unsigned long npoison = 0, nskip = 0, nverify_bad = 0; static int shown = 0;
    uint32_t off = ptr - 0x80000000u;
    uint32_t sz = s5042_rd(rdram, off - 0x10 + 4);
    if (sz < 0x20 || sz > 0x700000u || off + 16 > (rs64_ram_top - 0x80000000u)) { ++nskip; if (shown < 8) { ++shown; std::fprintf(stderr, "[s5042-poison] SKIP ptr=%08X sz=%08X ra=%08X\n", ptr, sz, ra); } return; }
    for (uint32_t i = 0; i < 16; i += 4) { uint32_t v = 0xDEADBEEFu; for (int k = 0; k < 4; k++) rdram[(off + i + k) ^ 3u] = (uint8_t)(v >> (24 - 8 * k)); }
    bool ok = s5042_rd(rdram, off) == 0xDEADBEEFu && s5042_rd(rdram, off + 12) == 0xDEADBEEFu;
    if (!ok) ++nverify_bad;
    ++npoison;
    if ((npoison & (npoison - 1)) == 0) std::fprintf(stderr, "[s5042-poison] total poisoned=%lu skipped=%lu verify_bad=%lu last ptr=%08X sz=%08X ra=%08X\n", npoison, nskip, nverify_bad, ptr, sz, ra);
}
extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,
                                                 uint32_t voice_index,
                                                 uint32_t a1, uint32_t a2,
                                                 uint32_t a3, uint32_t scaled,
                                                 uint32_t voice_base) {
    if (!rdram || !rs64_m5_voice_modulation_enabled()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static uint32_t rows[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 128u) return;
    std::fprintf(stderr,
        "[m5-voice-mod-call] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "voice=%u a1=0x%08X a2=0x%08X a3=0x%08X scaled=0x%08X base=0x%08X\n",
        rows[slot]++, rs64_phase_ord(), width, origin, pc, voice_index, a1,
        a2, a3, scaled, voice_base);
    std::fflush(stderr);
}

extern "C" void rs64_m5_voice_modulation_state(uint8_t* rdram, uint32_t pc,
                                                  uint32_t voice_ptr,
                                                  uint32_t coeff_ptr,
                                                  uint32_t coeff_value,
                                                  uint32_t voice_base) {
    if (!rdram || !rs64_m5_voice_modulation_enabled()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static uint32_t rows[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 128u) return;
    const auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint8_t* p = rdram + (guest - 0x80000000u);
        return (static_cast<uint32_t>(p[3]) << 24) |  /* s7601 BS: was p[0]<<24.. = byte-reversed word */
               (static_cast<uint32_t>(p[2]) << 16) |
               (static_cast<uint32_t>(p[1]) << 8) | p[0];
    };
    const uint32_t voice_record = voice_ptr >= 0x80000046u
        ? voice_ptr - 0x46u : 0xFFFFFFFFu;
    std::fprintf(stderr,
        "[m5-voice-mod-state] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "record=0x%08X base=0x%08X coeff_ptr=0x%08X coeff=0x%08X "
        "w44=0x%08X w48=0x%08X w4c=0x%08X\n",
        rows[slot]++, rs64_phase_ord(), width, origin, pc, voice_record,
        voice_base, coeff_ptr, coeff_value, word(voice_record + 0x44u),
        word(voice_record + 0x48u), word(voice_record + 0x4Cu));
    std::fflush(stderr);
}

extern "C" void rs64_m5_voice_modulation_callee(uint8_t* rdram, uint32_t stage,
                                                   uint32_t pc, uint32_t ra,
                                                   uint32_t a0, uint32_t a1,
                                                   uint32_t v0) {
    if (!rdram || !rs64_m5_voice_modulation_enabled()) return;
    if (stage == 0u && pc == 0x8008D5FCu) {
        rs64_m5_voice_callee_detail_pending = true;
    } else if (stage == 1u && rs64_m5_voice_callee_detail_pending &&
               pc == 0x80084860u) {
        rs64_m5_voice_callee_detail_active = true;
        rs64_m5_voice_callee_detail_pending = false;
    } else if (stage == 2u && rs64_m5_voice_callee_detail_active &&
               pc == 0x80084860u) {
        rs64_m5_voice_callee_detail_active = false;
    }
    uint32_t width = 0, origin = 0;
    width = rs64_vi_committed_width();
    origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static uint32_t controls = 0;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) {
        if (controls < 8u) {
            std::fprintf(stderr,
                "[m5-voice-callee-control] n=%u stage=%u pc=0x%08X width=%u origin=0x%06X\n",
                controls++, stage, pc, width, origin);
            std::fflush(stderr);
        }
        return;
    }
    static uint32_t rows[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 256u) return;
    const char* label = stage == 0u ? "call" : (stage == 1u ? "entry" : "return");
    std::fprintf(stderr,
        "[m5-voice-callee] row=%u stage=%s phase=%u width=%u origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X v0=0x%08X\n",
        rows[slot]++, label, rs64_phase_ord(), width, origin, pc, ra, a0, a1, v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_voice_modulation_callee_detail(
    uint8_t* rdram, uint32_t pc, uint32_t ra, uint32_t kind,
    uint32_t ptr, uint32_t value, uint32_t aux) {
    if (!rdram || !rs64_m5_voice_modulation_enabled()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static uint32_t rows[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] >= 256u) return;
    std::fprintf(stderr,
        "[m5-voice-callee-detail] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X ra=0x%08X kind=%u ptr=0x%08X value=0x%08X aux=0x%08X\n",
        rows[slot]++, rs64_phase_ord(), width, origin, pc, ra, kind, ptr,
        value, aux);
    std::fflush(stderr);
}

extern "C" void rs64_m5_pre_dma_writer_store(char width, uint32_t pc,
                                                uint32_t addr,
                                                uint32_t value);

// s6198: rs64_m5_writer_parity passes value as literal 0 and runs before the
// store, so the stored word is read back from RDRAM on the next hook entry.
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;

namespace {

struct Rs64FillRun { uint32_t lo, hi; };
struct Rs64FillAgg {
    uint64_t count = 0;
    uint32_t first = 0, last = 0, lo = 0, hi = 0;
    uint64_t ord0 = 0, ord1 = 0;
    Rs64FillRun runs[24]{};
    uint8_t nruns = 0;
    uint8_t overflow = 0;
};
struct Rs64FillSig { uint32_t pc, value; uint64_t ord; };
struct Rs64FillTls {
    uint32_t pc = 0, value = 0, lo = 0, hi = 0, first = 0, last = 0;
    uint64_t count = 0, ord0 = 0, ord1 = 0;
    bool live = false;
    int dir = 0;
    int stride = 4;
};

struct Rs64FillState {
    std::mutex mu;
    std::map<uint64_t, Rs64FillAgg> by;
    std::map<uint32_t, Rs64FillSig> sig;
    std::atomic<uint64_t> order{0};
    std::atomic<uint64_t> words{0};
    std::atomic<uint64_t> resolved{0};
    std::atomic<uint64_t> nonzero{0};
    std::atomic<uint64_t> interesting{0};
    uint32_t gen = 0;
    uint32_t exact = 0;
    uint32_t sig_drop = 0;
    int pcs_overflow = 0;
    std::chrono::steady_clock::time_point flushed{};
    bool ever = false;
};

Rs64FillState& rs64_fill_state() {
    static Rs64FillState s;
    return s;
}

void rs64_fill_add_run(Rs64FillAgg* agg, uint32_t lo, uint32_t hi) {
    const uint32_t span = hi >= lo ? hi - lo : 0u;
    if (agg->nruns >= 24) {
        agg->overflow = 1;
        if (span < 0x20u) return;
        uint8_t victim = 0;
        uint32_t shortest = 0xFFFFFFFFu;
        for (uint8_t i = 0; i < agg->nruns; ++i) {
            const uint32_t w = agg->runs[i].hi - agg->runs[i].lo;
            if (w < shortest) { shortest = w; victim = i; }
        }
        if (shortest >= span) return;
        agg->runs[victim] = agg->runs[agg->nruns - 1];
        agg->nruns--;
    }
    if (agg->nruns < 24) {
        agg->runs[agg->nruns++] = Rs64FillRun{lo, hi};
    } else {
        agg->overflow = 1;
    }
    bool merged = true;
    while (merged) {
        merged = false;
        for (uint8_t i = 0; i < agg->nruns && !merged; ++i) {
            for (uint8_t j = static_cast<uint8_t>(i + 1); j < agg->nruns; ++j) {
                Rs64FillRun* x = &agg->runs[i];
                Rs64FillRun* y = &agg->runs[j];
                if (x->hi + 4u < y->lo || y->hi + 4u < x->lo) continue;
                if (y->lo < x->lo) x->lo = y->lo;
                if (y->hi > x->hi) x->hi = y->hi;
                agg->runs[j] = agg->runs[agg->nruns - 1];
                agg->nruns--;
                merged = true;
                break;
            }
        }
    }
}

void rs64_fill_flush_summary_locked(Rs64FillState& st) {
    st.gen++;
    std::fprintf(stderr,
        "[g1d-fill-ctl] gen=%u word_stores=%llu resolved=%llu nonzero=%llu "
        "interesting=%llu pcs=%zu sig=%zu exact=%u pcs_overflow=%d sig_drop=%u rdram=%d\n",
        st.gen,
        (unsigned long long)st.words.load(std::memory_order_relaxed),
        (unsigned long long)st.resolved.load(std::memory_order_relaxed),
        (unsigned long long)st.nonzero.load(std::memory_order_relaxed),
        (unsigned long long)st.interesting.load(std::memory_order_relaxed),
        st.by.size(), st.sig.size(), st.exact, st.pcs_overflow, st.sig_drop,
        g_recomp_rdram_for_wp_raw != nullptr);
    for (const auto& kv : st.by) {
        const uint32_t pc = static_cast<uint32_t>(kv.first >> 32);
        const uint32_t value = static_cast<uint32_t>(kv.first);
        const Rs64FillAgg& agg = kv.second;
        char spans[512];
        size_t used = 0;
        spans[0] = 0;
        for (uint8_t i = 0; i < agg.nruns && used + 20 < sizeof(spans); ++i) {
            used += static_cast<size_t>(std::snprintf(
                spans + used, sizeof(spans) - used, "%s%06X-%06X",
                i ? "," : "", agg.runs[i].lo, agg.runs[i].hi));
        }
        if (agg.overflow && used + 2 < sizeof(spans)) spans[used++] = '+';
        spans[used] = 0;
        std::fprintf(stderr,
            "[g1d-fill] gen=%u pc=0x%08X value=%08X count=%llu first=0x%06X last=0x%06X "
            "min=0x%06X max=0x%06X ord=%llu-%llu runs=%u spans=%s\n",
            st.gen, pc, value, (unsigned long long)agg.count, agg.first, agg.last,
            agg.lo, agg.hi, (unsigned long long)agg.ord0, (unsigned long long)agg.ord1,
            agg.nruns, spans[0] ? spans : "-");
    }
    std::fflush(stderr);
    st.flushed = std::chrono::steady_clock::now();
    st.ever = true;
}

void rs64_fill_commit_tls(Rs64FillTls* tls) {
    if (!tls->live || tls->count == 0) return;
    Rs64FillState& st = rs64_fill_state();
    std::lock_guard<std::mutex> lock(st.mu);
    const uint64_t key = (uint64_t)tls->pc << 32 | tls->value;
    auto it = st.by.find(key);
    if (it == st.by.end()) {
        const bool common = tls->value == 0x00010001u || tls->value == 0x0001u;
        if (st.by.size() >= 1024u && common) {
            st.pcs_overflow = 1;
            tls->live = false;
            tls->count = 0;
            return;
        }
        it = st.by.emplace(key, Rs64FillAgg{}).first;
        it->second.first = tls->first;
        it->second.lo = tls->lo;
        it->second.hi = tls->hi;
        it->second.ord0 = tls->ord0;
    }
    Rs64FillAgg& agg = it->second;
    agg.count += tls->count;
    agg.last = tls->last;
    agg.ord1 = tls->ord1;
    if (tls->lo < agg.lo) agg.lo = tls->lo;
    if (tls->hi > agg.hi) agg.hi = tls->hi;
    rs64_fill_add_run(&agg, tls->lo, tls->hi);
    const auto ord_at = [&](uint32_t addr) -> uint64_t {
        const uint32_t step = tls->stride > 0 ? (uint32_t)tls->stride : 4u;
        if (tls->dir < 0) return tls->ord0 + (uint64_t)(tls->hi - addr) / step;
        return tls->ord0 + (uint64_t)(addr - tls->lo) / step;
    };
    const bool rare = tls->value == 0x05200002u || tls->value == 0x0001FFFFu;
    if (rare) {
        if (tls->count <= 256u) {
            const uint32_t step = tls->stride > 0 ? (uint32_t)tls->stride : 4u;
            for (uint32_t addr = tls->lo; addr <= tls->hi; addr += step) {
                const uint64_t ord = ord_at(addr);
                if (st.exact < 4000u || tls->value == 0x05200002u) {
                    std::fprintf(stderr,
                        "[g1d-fill-exact] pc=0x%08X value=%08X addr=0x%06X ord=%llu\n",
                        tls->pc, tls->value, addr, (unsigned long long)ord);
                    if (tls->value == 0x05200002u) std::fflush(stderr);
                    st.exact++;
                }
                if (st.sig.size() < 16384u) {
                    st.sig[addr] = Rs64FillSig{tls->pc, tls->value, ord};
                } else {
                    st.sig_drop++;
                }
            }
        } else {
            st.sig_drop++;
        }
    } else {
        for (auto sig = st.sig.begin(); sig != st.sig.end(); ) {
            const uint32_t addr = sig->first;
            if (addr < tls->lo || addr > tls->hi) { ++sig; continue; }
            const uint64_t ord = ord_at(addr);
            std::fprintf(stderr,
                "[g1d-fill-clobber] addr=0x%06X prev_pc=0x%08X prev_value=%08X prev_ord=%llu "
                "pc=0x%08X ord=%llu\n",
                addr, sig->second.pc, sig->second.value,
                (unsigned long long)sig->second.ord, tls->pc, (unsigned long long)ord);
            sig = st.sig.erase(sig);
        }
    }
    tls->live = false;
    tls->count = 0;
}

void rs64_fill_note_hi(uint32_t pc, uint32_t phys, uint32_t word) {
    // Command nodes sit above the 8 MB line (s6197: 0xAEF620 / 0xB2D820).
    // The 24-run summary evicts later single-word stores, so this log is the
    // one that can still name a scattered 00010001 writer.
    if (phys < 0x800000u || phys >= 0x01000000u) return;
    static std::atomic<uint32_t> hi_n{0};
    const uint32_t n = hi_n.fetch_add(1, std::memory_order_relaxed);
    if (n >= 65536u) return;
    std::fprintf(stderr, "[g1d-fill-hi] pc=0x%08X value=%08X addr=0x%06X n=%u\n",
                 pc, word, phys, n);
    if (word == 0x05200002u || (n & 63u) == 0u) std::fflush(stderr);
}

void rs64_fill_note_word(Rs64FillTls* tls, uint32_t pc, uint32_t phys,
                         uint32_t word, int stride) {
    const bool interesting = stride == 4 &&
        (word == 0x00010001u || word == 0x0001FFFFu || word == 0x05200002u);
    if (!interesting) return;
    rs64_fill_note_hi(pc, phys, word);
    Rs64FillState& st = rs64_fill_state();
    const uint64_t ord = st.order.fetch_add(1, std::memory_order_relaxed) + 1u;
    st.interesting.fetch_add(1, std::memory_order_relaxed);
    if (tls->live && tls->count && tls->pc == pc && tls->value == word &&
        tls->stride == stride) {
        if (tls->dir >= 0 && phys == tls->hi + (uint32_t)stride) {
            tls->hi = phys;
            tls->last = phys;
            tls->count++;
            tls->ord1 = ord;
            tls->dir = 1;
            return;
        }
        if (tls->dir <= 0 && phys + (uint32_t)stride == tls->lo) {
            tls->lo = phys;
            tls->last = phys;
            tls->count++;
            tls->ord1 = ord;
            tls->dir = -1;
            return;
        }
    }
    rs64_fill_commit_tls(tls);
    *tls = Rs64FillTls{pc, word, phys, phys, phys, phys, 1u, ord, ord, true, 0, stride};
}

}  // namespace

namespace {

std::atomic<uint64_t> g_rs64_blk_n{0};
std::atomic<uint64_t> g_rs64_blk_drop{0};
std::atomic<int> g_rs64_blk_armed{0};
thread_local uint32_t g_rs64_blk_ustore_pc = 0;

bool rs64_g1d_blk_enabled() {
    static const bool on = [] {
        const char* e = std::getenv("ROGUESQ_LOG_G1D_BLK");
        return e && *e && *e != '0';
    }();
    return on;
}

void rs64_g1d_blk_arm() {
    if (g_rs64_blk_armed.exchange(1, std::memory_order_relaxed) == 0) {
        std::fprintf(stderr, "[g1d-blk-ctl] armed=1\n");
        std::fflush(stderr);
    }
}

}  // namespace

extern "C" void rs64_g1d_blk_set_ustore_pc(uint32_t pc) {
    if (!rs64_g1d_blk_enabled()) return;
    g_rs64_blk_ustore_pc = pc;
}

extern "C" void rs64_g1d_tb2(const char* tag) {
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw;
    if (r == nullptr) return;
    static const uint32_t k[3] = {0x00A6AA10u, 0x00AE5F20u, 0x00AE6B20u};
    for (int i = 0; i < 3; ++i) {
        uint32_t wv[8];
        for (uint32_t q = 0; q < 8u; ++q) {
            uint32_t v = 0;
            for (uint32_t b = 0; b < 4u; ++b) v = (v << 8) | r[(k[i] + q * 4u + b) ^ 3u];
            wv[q] = v;
        }
        std::fprintf(stderr, "[g1d-tb2] %s addr=0x%06X %08X %08X %08X %08X %08X %08X %08X %08X\n",
                     tag, k[i], wv[0], wv[1], wv[2], wv[3], wv[4], wv[5], wv[6], wv[7]);
    }
    std::fflush(stderr);
}

// s6998 G5a: is the guest heap block under an RT64 copyNativeToRAM writeback
// live? ROGUESQ_G5A_WBLIVE=1. Walks the three rs_malloc arena heads
// (0x8010FEFC / FF00 / FF18; header hw+0: 1 free, 2 allocated, 8 terminator;
// +2 tag; +4 size; next = h + 0x10 + size, from rs_malloc 0x80001BB4-0x80001C50)
// and classifies each written range against the block holding the colour image
// address F the writeback belongs to:
//   own      F's block allocated, every other overlapped block free/none
//   stale    F's block is free (image address returned to the heap)
//   nonheap  F is in no heap block, and no allocated block is overlapped
//   foreign  an allocated block other than F's is overlapped (live corruption)
// hdr counts ranges that cover any block header. Reads only; racy vs the guest.
namespace {
struct G5aBlk { uint32_t h, fl, tag, sz; };
static uint32_t g5a_rd(volatile uint8_t* r, uint32_t va) {
    return *(volatile uint32_t*)(r + (va & 0x00FFFFFCu));
}
static int g5a_walk(volatile uint8_t* r, std::vector<G5aBlk>& out) {
    out.clear();
    static const uint32_t heads[3] = {0x8010FEFCu, 0x8010FF00u, 0x8010FF18u};
    uint32_t seen[3] = {0, 0, 0}; int narena = 0;
    for (int i = 0; i < 3; ++i) {
        uint32_t a = g5a_rd(r, heads[i]);
        if (a < 0x80000000u || a >= 0x81000000u) continue;
        bool dup = false; for (int j = 0; j < narena; ++j) if (seen[j] == a) dup = true;
        if (dup) continue; seen[narena++] = a;
        for (int g = 0; g < 200000; ++g) {
            uint32_t w0 = g5a_rd(r, a), sz = g5a_rd(r, a + 4u), fl = w0 >> 16;
            if (fl & 8u) break;
            if ((fl & 3u) == 0u || sz > 0x1000000u) break;
            out.push_back({a, fl, w0 & 0xFFFFu, sz});
            uint32_t nx = a + 0x10u + sz;
            if (nx <= a || nx >= 0x81000000u) break;
            a = nx;
        }
    }
    return narena;
}
/* s7334 item 24(b): class 5 "guest non-heap tail". coalesceFreeHeapBlocks (0x800022F8) re-terminates the persistent arena at
   a3 - 0x10 (fl=8 sz=0 store at pc 800024A4/A8/B0, store watch s7334), a3 being the frame-buffer layout bound from 0x80000DD4
   (caller 0x80001430) or the global 0x801163E4; the memory above holds the scene's framebuffers and the gfx RDP FIFO and is never
   heap. True when x sits in no walked guest block and the highest walked block end below x is such a sentinel.
   ROGUESQ_S7334_CLASS5=0 restores the old 3/4 classes. */
static bool s7334_nonheap(uint32_t x) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7334_CLASS5"); return !(e && *e == '0'); }();
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!on || !r) return false;
    std::vector<G5aBlk> b; g5a_walk(r, b); uint32_t top = 0;
    for (const auto& k : b) { const uint32_t e = k.h + 0x10u + k.sz; if (e <= x && e > top) top = e; }
    return top && ((g5a_rd(r, top) >> 16) & 8u) && g5a_rd(r, top + 4u) == 0u; }
/* s7325: guest-side heap walk (independent of the host alloc map): 0 x in no block, 1 in block header, 2 in data. */
static int s7325_guest(uint32_t x, uint32_t* fl, uint32_t* h, uint32_t* sz) {
    *fl = *h = *sz = 0; volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return 0;
    std::vector<G5aBlk> b; g5a_walk(r, b);
    for (const auto& k : b) if (x >= k.h && x < k.h + 0x10u + k.sz) { *fl = k.fl; *h = k.h; *sz = k.sz; return x < k.h + 0x10u ? 1 : 2; }
    return 0; }
}  // namespace
/* s7333 item 24(b): for an address the guest walk does not place (FIFO above the arena top), report the highest walked block end
   below x, the 4 words at x-0x10 and at that end (sentinel header?), plus the s7333 keep/drop counters. */
extern "C" void rs64_s7333_above(uint32_t x, uint32_t* top, uint32_t* w, uint32_t* tw, uint64_t* kept, uint64_t* dropped, uint64_t* nev) {
    *top = 0; for (int i = 0; i < 4; ++i) w[i] = tw[i] = 0; *kept = s_s7333_kept; *dropped = s_s7333_dropped; *nev = s_s7333_nev;
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    std::vector<G5aBlk> b; g5a_walk(r, b);
    for (const auto& k : b) { const uint32_t e = k.h + 0x10u + k.sz; if (e <= x && e > *top) *top = e; }
    for (int i = 0; i < 4; ++i) { w[i] = g5a_rd(r, x - 0x10u + 4u * i); if (*top) tw[i] = g5a_rd(r, *top + 4u * i); } }
/* s7333: before heapsync #1 (boot) register the guest fl&6 carves from one guest walk, retried every 512 lookups. Caller holds s_s7317_mu. */
namespace {
void s7333_boot_register() {
    static uint32_t miss = 0; if ((miss++ & 511u) != 0) return;
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    std::vector<G5aBlk> b; g5a_walk(r, b); static int nlog = 0;
    for (const auto& k : b) { if ((k.fl & 6u) != 6u) continue; const uint32_t p0 = k.h + 0x10u; if (s_s7332_carve.count(p0)) continue;
        s_s7332_carve[p0] = k.sz; s_s7333_keys.emplace(p0, 0);
        if (nlog++ < 16) std::fprintf(stderr, "[s7333] boot carve %08X+%X (guest fl=%X) registered before heapsync #1\n", p0, k.sz, k.fl); } }
}  // namespace
struct S7325Out { uint32_t lo, loend, hi, lreq, hreq; void* lopc[3]; void* hipc[3]; uint32_t fptr, freq; double fage; void* fpc[4]; void* apc[3];
                  int gk; uint32_t gfl, gh, gsz; };
/* s7325 gap class of KSEG0 x: 0 inside a live block, 1 outside the heap extent ever allocated (static), 2 header gap (x in
   [end of a live block, next live block) with that gap <= 0x20), 3 inside a freed block (most recent free wins), 4 untracked, 5 (guest=1 only, s7334) above an arena end sentinel in no guest block.
   With guest=1 the guest heap walk result is filled (gk 0 none / 1 header / 2 data, gfl flags 1 free 2 allocated). */
extern "C" int rs64_s7325_gap(uint32_t x, S7325Out* o, int guest) {
    std::memset(o, 0, sizeof *o); int k;
    { std::lock_guard<std::mutex> lk(s_s7317_mu);
      const bool live = s7318_blk(x, nullptr) != 0;
      auto it = s_s7317_live.upper_bound(x);
      if (it != s_s7317_live.end() && !s7318_sp(it->first)) { o->hi = it->first; o->hreq = it->second.req; for (int j = 0; j < 3; ++j) o->hipc[j] = it->second.pc[j]; }
      if (it != s_s7317_live.begin()) { auto lv = std::prev(it); o->lo = lv->first; o->lreq = lv->second.req; o->loend = lv->first + lv->second.req;
          for (int j = 0; j < 3; ++j) o->lopc[j] = lv->second.pc[j]; }
      const S7325F* best = nullptr; auto fi = s_s7325_freed.upper_bound(x);
      for (int n = 0; n < 2048 && fi != s_s7325_freed.begin(); ++n) { --fi; const S7325F& f = fi->second;
          if (x - f.ptr < (f.req ? f.req : 1u) && (!best || f.seq > best->seq)) best = &f; }
      if (best) { o->fptr = best->ptr; o->freq = best->req; o->fage = s7325_now() - best->t; for (int j = 0; j < 4; ++j) o->fpc[j] = best->fpc[j]; for (int j = 0; j < 3; ++j) o->apc[j] = best->apc[j]; }
      if (live) k = 0;
      else if (x < s_s7325_hmin || x >= s_s7325_hmax) k = 1;
      else if (o->hi && o->lo && x >= o->loend && x < o->hi && o->hi - o->loend <= 0x20u) k = 2;
      else if (best) k = 3;
      else k = 4; }
    if (guest) o->gk = s7325_guest(x, &o->gfl, &o->gh, &o->gsz);
    if (guest && o->gk == 0 && (k == 3 || k == 4) && s7334_nonheap(x)) k = 5;   // s7334 class 5 (item 24(b))
    return k; }
/* positive controls: *fr = last freed ptr (0 if none), *hg = end of the last malloc'd block when its live successor sits <= 0x20 past it */
extern "C" void rs64_s7325_ctl(uint32_t* fr, uint32_t* hg) {
    std::lock_guard<std::mutex> lk(s_s7317_mu); *fr = s_s7325_lastfree; *hg = 0;
    static uint32_t rot = 0; rot = rot * 1103515245u + 12345u;
    auto it = s_s7317_live.lower_bound(0x80000000u | (rot & 0x003FFFF0u)); if (it == s_s7317_live.end()) it = s_s7317_live.begin();
    for (int n = 0; n < 4096 && it != s_s7317_live.end(); ++n, ++it) { auto nx = std::next(it); if (nx == s_s7317_live.end()) break;
        const uint32_t e = it->first + it->second.req;
        if (!s7318_sp(it->first) && !s7318_sp(nx->first) && nx->first > e && nx->first - e <= 0x20u) { *hg = e; return; } } }
/* s7325: buildHeapFreeList(head, 0, 0, lo, hi) entry (tools/apply_s7325_heaprebuild.py). The retail scene reset rebuilds an arena
   without rs_free, so every host-map block in [lo, hi) dies here: drop them (s7317 map -> freed history tagged reset, s6063 map).
   Under ALLOCMAP one stderr line per rebuild with the spill arena (s6702) live blocks/bytes at that moment (spill blocks are never
   in the rebuilt range, so anything the game allocated there before the reset and relied on the reset to discard stays live). */
extern "C" void rs64_s7325_heaprebuild(uint32_t head, uint32_t lo, uint32_t hi) {
    static uint64_t n = 0; ++n; uint64_t dropped = 0, dbytes = 0;
    std::vector<std::tuple<char, uint32_t, uint32_t, void*>> s7331_t;
    struct S7331Fl { std::vector<std::tuple<char, uint32_t, uint32_t, void*>>& v; ~S7331Fl() { for (auto& x : v) rs64_s7331_track(1000000u + s7331_sync, std::get<0>(x), std::get<1>(x), std::get<2>(x), std::get<3>(x)); } } s7331_fl{s7331_t};
    if (s7317_on()) { std::lock_guard<std::mutex> lk(s_s7317_mu); const double now = s7325_now();
        for (auto it = s_s7317_live.lower_bound(lo); it != s_s7317_live.end() && it->first < hi;) {
            if (s7318_sp(it->first)) { ++it; continue; }
            if (rs64_s7324_on) { S7325F f{it->first, it->second.req, ++s_s7325_seq, now, {nullptr, nullptr, nullptr, nullptr}, {it->second.pc[0], it->second.pc[1], it->second.pc[2]}};
                s_s7325_ord.push_back(s_s7325_freed.emplace(it->first, f)); if (s_s7325_ord.size() > 65536u) { s_s7325_freed.erase(s_s7325_ord.front()); s_s7325_ord.pop_front(); } }
            if (rs64_s7331_on) s7331_t.emplace_back('R', it->first, it->second.req, it->second.pc[1]);
            s7333_ev("rebuild", it->first, it->second.req, it->second.pc[0] == (void*)&s7332_carve_tag, 0);
            ++dropped; dbytes += it->second.req; it = s_s7317_live.erase(it); } }
    for (auto it = s_s6063_live.lower_bound(lo); it != s_s6063_live.end() && it->first < hi;) { s_s6063_bytes -= it->second; it = s_s6063_live.erase(it); }
    if (s7317_on() && head == 0x8010FEFCu) { std::lock_guard<std::mutex> lk(s_s7317_mu); const double now = s7325_now(); uint64_t nt = 0, nb = 0;
        for (auto it = s_s7317_live.lower_bound(0x81000000u); it != s_s7317_live.end() && s7318_sp(it->first); ++it) {
            if (!(it->second.fl & 4u)) continue; ++nt; nb += it->second.req;
            if (!s_s7326_surv.count(it->first)) { s_s7326_surv[it->first] = S7326S{s_s7326_resets, now, it->second.fl, it->second.req, it->second.pc[1], 'T', false}; ++s_s7326_nsurv; } }
        if (nt) std::fprintf(stderr, "[s7326] temp rebuild: %llu flags&4 spill blocks 0x%llX bytes outlive it\n", (unsigned long long)nt, (unsigned long long)nb); }
    if (s7317_on()) { uint32_t sb = 0; size_t sn = 0; { std::lock_guard<std::mutex> lk(s_s6702_mu); sn = s_s6702_live.size(); sb = s_s6702_live_bytes; }
        std::fprintf(stderr, "[s7325] heap rebuild #%llu head=%08X range=%08X..%08X dropped=%llu blocks 0x%llX bytes | spill live=%zu blocks 0x%X bytes bump=0x%X\n",
                     (unsigned long long)n, head, lo, hi, (unsigned long long)dropped, (unsigned long long)dbytes, sn, sb, s_s6569_bump); } }
/* s7325: after coalesceFreeHeapBlocks (0x800022F8, misnamed: scene-change bulk free of every persistent-heap block whose header tag
   lacks 0x80; wrapper from tools/apply_s7325_heaprebuild.py). Re-sync: host-map non-spill entries inside the walked arenas whose
   ptr-0x10 is no longer an allocated guest header are dropped (freed history, freer null). When anything was dropped, one stderr
   line: dropped count, spill-arena live blocks split by the rs_malloc a1 tag bit 0x80 recorded at allocation (a non-persistent spill
   block outlives the reset that retail would have applied to it), and the tag control (recorded a1 & 0x80 vs guest header tag & 0x80
   on matched heap blocks: must agree). */
static void rs64_s7326_scan(uint32_t a0, uint64_t ncall, uint64_t npk, uint64_t npk_b, uint32_t ctl);
static bool s7332_carve_on() { static const int v = [] { const char* e = std::getenv("ROGUESQ_S7332_CARVE"); return (e && *e == '0') ? 0 : 1; }(); return v != 0; }
extern "C" void rs64_s7325_heapsync(uint32_t a0);
extern "C" void rs64_s7325_heapsync(uint32_t a0) {
    ++s7331_sync; s7331_q.clear();
    rs64_s7326_spill_reset(a0);  /* s7326: retail bulk free applied to spill blocks (always, not ALLOCMAP-gated) */
    std::vector<std::tuple<char, uint32_t, uint32_t, void*>> s7331_t;  /* s7331 dropped blocks (kind, ptr, req, allocator) */
    if (rs64_s7331_on && s7317_on()) { std::lock_guard<std::mutex> lk(s_s7317_mu);
        for (auto& q : s7331_q) { auto it = s_s7317_live.find(q.first); s7331_t.emplace_back('S', q.first, it != s_s7317_live.end() ? it->second.req : q.second, it != s_s7317_live.end() ? it->second.pc[1] : nullptr); } }
    struct S7331Fl { std::vector<std::tuple<char, uint32_t, uint32_t, void*>>& v; ~S7331Fl() { for (auto& x : v) rs64_s7331_track(s7331_sync, std::get<0>(x), std::get<1>(x), std::get<2>(x), std::get<3>(x)); } } s7331_fl{s7331_t};
    if (!s7317_on()) return;
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    static uint64_t ncall = 0, nlog = 0; ++ncall;
    uint32_t ctl = 0; uint64_t npk = 0, npk_b = 0;  /* s7326 */
    if (s7326_ctl_on()) { ctl = rs64_s6569_spill(0x40u);
        if (ctl) { std::lock_guard<std::mutex> lk(s_s7317_mu); s_s7317_live[ctl] = S7317B{0x40u, {nullptr, nullptr, nullptr}, s7325_now(), 0u}; ++s_s7317_sprec; ++s_s7326_ctl_n; } }
    std::vector<G5aBlk> b; g5a_walk(r, b); if (b.empty()) return;
    std::map<uint32_t, uint32_t> alloc; uint32_t lo = 0xFFFFFFFFu, hi = 0;
    for (const auto& k : b) { lo = std::min(lo, k.h); hi = std::max(hi, k.h + 0x10u + k.sz); if ((k.fl & 3u) == 2u) alloc[k.h + 0x10u] = k.tag; }
    uint64_t dropped = 0, dbytes = 0, agree = 0, disagree = 0, sp_n = 0, sp_np = 0, sp_npb = 0; std::map<std::string, uint64_t> npown;
    { std::lock_guard<std::mutex> lk(s_s7317_mu); const double now = s7325_now();
      for (auto it = s_s7317_live.lower_bound(lo); it != s_s7317_live.end() && it->first < hi;) {
          if (s7318_sp(it->first)) { ++it; continue; }
          auto g = alloc.find(it->first);
          if (g != alloc.end()) { (((g->second ^ it->second.fl) & 0x80u) ? disagree : agree)++; if (!(it->second.fl & 0x84u)) { ++npk; npk_b += it->second.req; } ++it; continue; }
          if (rs64_s7324_on) { S7325F f{it->first, it->second.req, ++s_s7325_seq, now, {nullptr, nullptr, nullptr, nullptr}, {it->second.pc[0], it->second.pc[1], it->second.pc[2]}};
              s_s7325_ord.push_back(s_s7325_freed.emplace(it->first, f)); if (s_s7325_ord.size() > 65536u) { s_s7325_freed.erase(s_s7325_ord.front()); s_s7325_ord.pop_front(); } }
          if (rs64_s7331_on && it->second.pc[0] != (void*)&s7332_carve_tag) s7331_t.emplace_back('H', it->first, it->second.req, it->second.pc[1]);
          s7333_ev("sync", it->first, it->second.req, it->second.pc[0] == (void*)&s7332_carve_tag, 0);
          ++dropped; dbytes += it->second.req; it = s_s7317_live.erase(it); }
      /* s7332 item 24: coalesceFreeHeapBlocks (0x80002510/18/5C, 0x800023AC/D8: store watch s7332) writes the per-scene flags&4 carve
         block header by hand: no rs_malloc call, so rs64_s6063_malloc never saw it. It holds the framebuffers, the temp arena and the
         gfx RDP FIFO (OSTask output_buff). Register every guest-allocated fl&4 block the map lacks so ALLOCMAP consumers class it live. */
      if (s7332_carve_on()) for (const auto& k : b) { if ((k.fl & 6u) != 6u) continue; const uint32_t p0 = k.h + 0x10u;
          auto ex = s_s7317_live.find(p0); if (ex != s_s7317_live.end()) { if (ex->second.pc[0] == (void*)&s7332_carve_tag) ex->second.req = k.sz; if (k.sz > ex->second.req || ex->second.pc[0] == (void*)&s7332_carve_tag) { s_s7332_carve[p0] = k.sz; s_s7333_keys.emplace(p0, 0); } continue; }
          s_s7317_live[p0] = S7317B{k.sz, {(void*)&s7332_carve_tag, (void*)&rs64_s7325_heapsync, nullptr}, now, 0x04u}; s_s7332_carve[p0] = k.sz; s_s7333_keys.emplace(p0, 0); ++s_s7332_ncarve;
          if (s_s7332_ncarve <= 64) std::fprintf(stderr, "[s7332] carve #%llu registered %08X+%X (guest fl=%X) at heapsync #%llu\n",
                                                  (unsigned long long)s_s7332_ncarve, p0, k.sz, k.fl, (unsigned long long)(ncall)); }
      if (dropped) for (auto it = s_s7317_live.lower_bound(0x81000000u); it != s_s7317_live.end() && s7318_sp(it->first); ++it) {
          ++sp_n; if (!(it->second.fl & 0x80u)) { ++sp_np; sp_npb += it->second.req; Dl_info di; void* pc = it->second.pc[1];
              npown[(pc && dladdr(pc, &di) && di.dli_sname) ? di.dli_sname : "?"]++; } } }
    for (auto it = s_s6063_live.lower_bound(lo); it != s_s6063_live.end() && it->first < hi;) { if (!alloc.count(it->first)) { s_s6063_bytes -= it->second; it = s_s6063_live.erase(it); } else ++it; }
    if (dropped && nlog++ < 400) {
        std::fprintf(stderr, "[s7325] heapsync #%llu a0=%08X arena=%08X..%08X guest_alloc=%zu dropped=%llu 0x%llX bytes tagctl agree=%llu disagree=%llu | spill live=%llu nonpersist=%llu 0x%llX bytes owners:",
                     (unsigned long long)ncall, a0, lo, hi, alloc.size(), (unsigned long long)dropped, (unsigned long long)dbytes, (unsigned long long)agree,
                     (unsigned long long)disagree, (unsigned long long)sp_n, (unsigned long long)sp_np, (unsigned long long)sp_npb);
        int k = 0; for (auto& kv : npown) { if (k++ >= 8) break; std::fprintf(stderr, " %s=%llu", kv.first.c_str(), (unsigned long long)kv.second); }
        std::fprintf(stderr, "\n"); }
    rs64_s7326_scan(a0, ncall, npk, npk_b, ctl); }
/* s7326 survivor scan after each coalesce reset (see S7326S). One [s7326] line per reset: heap np_kept (non-spill a1&0x84==0 blocks the
   guest still holds after the reset: retail-semantics control, must be 0 if the bulk free releases every such block), new 'C'
   survivors, current survivor set (count, bytes, by kind), cumulative survived / late-freed, spill arena live bytes and bump, ctl. */
static void rs64_s7326_scan(uint32_t a0, uint64_t ncall, uint64_t npk, uint64_t npk_b, uint32_t ctl) {
    uint64_t nnew = 0, nnew_b = 0, cur = 0, cur_b = 0, curT = 0, splive = 0; bool ctl_in = false; std::map<std::string, uint64_t> own;
    { std::lock_guard<std::mutex> lk(s_s7317_mu); const double now = s7325_now(); ++s_s7326_resets;
      for (auto it = s_s7317_live.lower_bound(0x81000000u); it != s_s7317_live.end() && s7318_sp(it->first); ++it) {
          ++splive; if (it->second.fl & 0x84u) continue;
          if (!s_s7326_surv.count(it->first)) { const bool c = (it->first == ctl);
              s_s7326_surv[it->first] = S7326S{s_s7326_resets, now, it->second.fl, it->second.req, it->second.pc[1], 'C', c};
              if (c) { ctl_in = true; ++s_s7326_ctl_seen; } else { ++s_s7326_nsurv; ++nnew; nnew_b += it->second.req; } } }
      for (auto& kv : s_s7326_surv) { if (kv.second.ctl) continue; ++cur; cur_b += kv.second.req; if (kv.second.kind == 'T') ++curT;
          Dl_info di; void* pc = kv.second.pc; own[(pc && dladdr(pc, &di) && di.dli_sname) ? di.dli_sname : "?"]++; } }
    uint32_t lb = 0, bump = 0; size_t nfree = 0; { std::lock_guard<std::mutex> lk(s_s6702_mu); lb = s_s6702_live_bytes; bump = s_s6569_bump; nfree = s_s6702_free.size(); }
    std::fprintf(stderr, "[s7326] reset#%llu sync#%llu a0=%X heap_np_kept=%llu 0x%llX | new_surv=%llu 0x%llX cur_surv=%llu 0x%llX (T %llu) tot_surv=%llu late_freed=%llu 0x%llX dtmax=%.1f | spill blocks=%llu live=0x%X bump=0x%X freeblk=%zu | ctl in=%d seen=%llu/%llu late=%llu owners:",
                 (unsigned long long)s_s7326_resets, (unsigned long long)ncall, a0, (unsigned long long)npk, (unsigned long long)npk_b, (unsigned long long)nnew,
                 (unsigned long long)nnew_b, (unsigned long long)cur, (unsigned long long)cur_b, (unsigned long long)curT, (unsigned long long)s_s7326_nsurv,
                 (unsigned long long)s_s7326_nlate, (unsigned long long)s_s7326_late_bytes, s_s7326_late_dtmax, (unsigned long long)splive, lb, bump, nfree,
                 (int)ctl_in, (unsigned long long)s_s7326_ctl_seen, (unsigned long long)s_s7326_ctl_n, (unsigned long long)s_s7326_ctl_late);
    int k = 0; for (auto& kv : own) { if (k++ >= 10) break; std::fprintf(stderr, " %s=%llu", kv.first.c_str(), (unsigned long long)kv.second); }
    std::fprintf(stderr, "\n");
    if (ctl) rs64_s6569_isspill(ctl);  /* ctl: free it now -> must count as a late free */ }
/* s7325 reconciliation: host live map (non-spill) vs the guest heap walk. Guest block h (flags, size) is "matched" when the
   map holds ptr h+0x10. Map entries with no guest allocated block at ptr-0x10 are stale: nested (inside a guest allocated block),
   in_free (inside a guest free block), or nowhere (outside every walked arena). Guest allocated blocks with no map entry are
   unmapped. Top owners (allocator frame 1) and alloc ages of the stale classes; sizes/addresses of unmapped. */
extern "C" void rs64_s7325_reconcile(FILE* o) {
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return;
    std::vector<G5aBlk> b; const int na = g5a_walk(r, b);
    std::lock_guard<std::mutex> lk(s_s7317_mu);
    const double now = s7325_now();
    uint64_t galloc = 0, gfree = 0, matched = 0, unmapped = 0, ub = 0, st[3] = {0, 0, 0}, nmap = 0;
    std::map<std::string, uint64_t> own[3]; double amin[3] = {1e30, 1e30, 1e30}, amax[3] = {0, 0, 0};
    std::map<uint32_t, const G5aBlk*> byh; for (const auto& k : b) { byh[k.h] = &k; if ((k.fl & 3u) == 2u) ++galloc; else ++gfree; }
    std::vector<std::pair<uint32_t, uint32_t>> um;
    for (const auto& k : b) if ((k.fl & 3u) == 2u) { if (s_s7317_live.count(k.h + 0x10u)) ++matched; else { ++unmapped; ub += k.sz; if (um.size() < 12) um.push_back({k.h + 0x10u, k.sz}); } }
    for (auto& kv : s_s7317_live) { if (s7318_sp(kv.first)) continue; ++nmap;
        auto g = byh.find(kv.first - 0x10u); if (g != byh.end() && (g->second->fl & 3u) == 2u) continue;
        int c = 2; auto c2 = byh.upper_bound(kv.first);
        if (c2 != byh.begin()) { --c2; const G5aBlk* k = c2->second; if (kv.first < k->h + 0x10u + k->sz) c = (k->fl & 3u) == 2u ? 0 : 1; }
        ++st[c]; char nm[160]; Dl_info di; void* pc = kv.second.pc[1];
        if (pc && dladdr(pc, &di) && di.dli_sname) snprintf(nm, sizeof nm, "%s", di.dli_sname); else snprintf(nm, sizeof nm, "?");
        own[c][nm]++; const double a = kv.second.t > 0 ? now - kv.second.t : -1; if (a >= 0) { amin[c] = std::min(amin[c], a); amax[c] = std::max(amax[c], a); } }
    fprintf(o, "REC arenas=%d guest_alloc=%llu guest_free=%llu map_nonspill=%llu matched=%llu unmapped=%llu unmapped_bytes=%llX stale_nested=%llu stale_in_free=%llu stale_nowhere=%llu\n",
            na, (unsigned long long)galloc, (unsigned long long)gfree, (unsigned long long)nmap, (unsigned long long)matched, (unsigned long long)unmapped,
            (unsigned long long)ub, (unsigned long long)st[0], (unsigned long long)st[1], (unsigned long long)st[2]);
    static const char* cn[3] = {"nested", "in_free", "nowhere"};
    for (int c = 0; c < 3; ++c) { if (!st[c]) continue; std::vector<std::pair<uint64_t, std::string>> v; for (auto& kv : own[c]) v.push_back({kv.second, kv.first});
        std::sort(v.rbegin(), v.rend()); fprintf(o, "REC stale_%s age %.1f..%.1f s owners:", cn[c], amin[c] < 1e29 ? amin[c] : -1.0, amax[c]);
        for (size_t i = 0; i < v.size() && i < 8; ++i) fprintf(o, " %s=%llu", v[i].second.c_str(), (unsigned long long)v[i].first); fprintf(o, "\n"); }
    fprintf(o, "REC unmapped_ex:"); for (auto& u : um) fprintf(o, " %08X+%X", u.first, u.second); fprintf(o, "\n"); }
namespace {
// returns class 0 own,1 stale,2 nonheap,3 foreign; fills fb/foreign block info
static int g5a_classify(const std::vector<G5aBlk>& b, uint32_t F, uint32_t lo, uint32_t hi,
                        const G5aBlk** fbb, const G5aBlk** fgn, int* hdr) {
    *fbb = nullptr; *fgn = nullptr; *hdr = 0;
    for (const auto& k : b) if (k.h <= F && F < k.h + 0x10u + k.sz) { *fbb = &k; break; }
    for (const auto& k : b) {
        uint32_t s = k.h, e = k.h + 0x10u + k.sz;
        if (e <= lo || s >= hi) continue;
        if (s >= lo && s < hi) ++*hdr;
        if (&k != *fbb && (k.fl & 2u) && !*fgn) *fgn = &k;
    }
    if (*fgn) return 3;
    if (!*fbb) return 2;
    return ((*fbb)->fl & 2u) ? 0 : 1;
}
static void rs64_g5a_wblive(uint32_t src, uint32_t dest, uint32_t len) {
    static int en = -1;
    if (en < 0) { const char* e = std::getenv("ROGUESQ_G5A_WBLIVE"); en = (e && *e && *e != '0') ? 1 : 0; }
    if (!en) return;
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw;
    if (!r || len < 4u) return;
    static std::mutex mu; std::lock_guard<std::mutex> lk(mu);
    static std::vector<G5aBlk> b; static uint64_t ncls[4], nhdr, ncall; static int nlog[4], nxl;
    static bool ctl = false;
    static const char* nm[4] = {"own", "stale", "nonheap", "foreign"};
    const int narena = g5a_walk(r, b);
    uint32_t nfree = 0, nalloc = 0; for (auto& k : b) { if (k.fl & 2u) ++nalloc; else ++nfree; }
    if (!ctl && nalloc >= 2u) {
        // positive control: synthetic ranges whose answers are known
        ctl = true; const G5aBlk *A = nullptr, *B = nullptr, *Fr = nullptr;
        for (size_t i = 0; i + 1 < b.size(); ++i)
            if ((b[i].fl & 2u) && (b[i + 1].fl & 2u)) { A = &b[i]; B = &b[i + 1]; break; }
        for (auto& k : b) if (!(k.fl & 2u)) { Fr = &k; break; }
        const G5aBlk *x, *y; int h; int c1 = -1, c2 = -1, c3 = -1;
        if (A) { c1 = g5a_classify(b, A->h + 0x10u, A->h + 0x10u, A->h + 0x10u + A->sz, &x, &y, &h);
                 c2 = g5a_classify(b, A->h + 0x10u, A->h + 0x10u, B->h + 0x20u, &x, &y, &h); }
        if (Fr) c3 = g5a_classify(b, Fr->h + 0x10u, Fr->h + 0x10u, Fr->h + 0x10u + 4u, &x, &y, &h);
        std::fprintf(stderr, "[g5a-wbl-ctl] narena=%d nblk=%zu alloc=%u free=%u own_in_A=%s(want own) A_into_B=%s(want foreign) in_free=%s(want stale or foreign)\n",
                     narena, b.size(), nalloc, nfree, c1 < 0 ? "na" : nm[c1], c2 < 0 ? "na" : nm[c2], c3 < 0 ? "na" : nm[c3]);
    }
    const uint32_t F = (src & 0x00FFFFFFu) | 0x80000000u;
    const uint32_t lo = (dest & 0x00FFFFFFu) | 0x80000000u, hi = lo + len;
    const G5aBlk *fb, *fg; int hdr;
    const int c = g5a_classify(b, F, lo, hi, &fb, &fg, &hdr);
    ++ncall; ++ncls[c]; if (hdr) ++nhdr;
    const uint32_t ph = rs64_phase_ord();
    bool lg = false;
    if (c == 3 || hdr) { if (nxl < 300) { ++nxl; lg = true; } }
    else if (nlog[c] < 6) { ++nlog[c]; lg = true; }
    if ((ncall & (ncall - 1)) == 0) lg = true;
    {   // distinct-range census: every new (F, lo, hi, class, block) once, cap 600
        static std::set<std::string> seen; static int nd;
        char key[96]; std::snprintf(key, sizeof key, "%08X:%08X:%08X:%d:%08X:%08X", F, lo, hi, c, fb ? fb->h : 0u, fg ? fg->h : 0u);
        if (nd < 600 && seen.insert(key).second) { ++nd;
            std::fprintf(stderr, "[g5a-wbl-d] n=%llu ph=%u cls=%s F=0x%08X lo=0x%08X hi=0x%08X fbblk=0x%08X fl=%X sz=0x%X fgn=0x%08X off=0x%X\n",
                (unsigned long long)ncall, ph, nm[c], F, lo, hi, fb ? fb->h : 0u, fb ? fb->fl : 0u, fb ? fb->sz : 0u, fg ? fg->h : 0u,
                fb ? F - fb->h : 0u); }
    }
    if (lg) {
        std::fprintf(stderr, "[g5a-wbl] n=%llu ph=%u cls=%s F=0x%08X lo=0x%08X hi=0x%08X len=0x%X hdr=%d fbblk=0x%08X fl=%X tag=%04X sz=0x%X fgn=0x%08X fl=%X tag=%04X sz=0x%X nblk=%zu tot own=%llu stale=%llu nonheap=%llu foreign=%llu hdrhit=%llu\n",
            (unsigned long long)ncall, ph, nm[c], F, lo, hi, len, hdr,
            fb ? fb->h : 0u, fb ? fb->fl : 0u, fb ? fb->tag : 0u, fb ? fb->sz : 0u,
            fg ? fg->h : 0u, fg ? fg->fl : 0u, fg ? fg->tag : 0u, fg ? fg->sz : 0u, b.size(),
            (unsigned long long)ncls[0], (unsigned long long)ncls[1], (unsigned long long)ncls[2],
            (unsigned long long)ncls[3], (unsigned long long)nhdr);
        std::fflush(stderr);
    }
}
}  // namespace

extern "C" void rs64_g1d_blk_dma(const char* kind, uint32_t src, uint32_t dest,
                                 uint32_t len, uint32_t pc) {
    if (kind != nullptr && std::strcmp(kind, "rt64wb") == 0) rs64_g5a_wblive(src, dest, len);
    // s6206: count copyNativeToRAM spans that overlap the early images
    // [0xA6A000, 0xB00000). Independent of the command-node block log.
    if (kind != nullptr && len >= 4u && std::strcmp(kind, "rt64wb") == 0) {
        static int s_wb = -1;
        if (s_wb < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_G1D_TASK");
            s_wb = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_wb) {
            const uint32_t phys = dest & 0x00FFFFFFu;
            const uint64_t end64 = (uint64_t)phys + (uint64_t)len;
            if (phys < 0x00B00000u && end64 > 0x00A6A000u) {
                static uint32_t n = 0;
                static uint32_t n4 = 0;
                ++n;
                const uint32_t phase = rs64_phase_ord();
                if (phase == 4u) ++n4;
                {
                    static bool s_first = false;
                    static bool s_cov[3] = {false, false, false};
                    static const uint32_t ka[3] = {0x00A6AA10u, 0x00AE5F20u, 0x00AE6B20u};
                    if (!s_first) { s_first = true; rs64_g1d_tb2("wb-first"); }
                    for (int ti = 0; ti < 3; ++ti) {
                        if (!s_cov[ti] && ka[ti] >= phys && ka[ti] + 32u <= end64) {
                            s_cov[ti] = true;
                            std::fprintf(stderr, "[g1d-tb2] wb-covers addr=0x%06X phase=%u n=%u\n", ka[ti], phase, n);
                            rs64_g1d_tb2("wb-cover");
                        }
                    }
                }
                const bool edge = n <= 8u || (n & (n - 1u)) == 0u;
                if (edge) {
                    std::fprintf(stderr,
                        "[g1d-wb] n=%u n4=%u phase=%u src=0x%06X dest=0x%06X end=0x%06X len=0x%X\n",
                        n, n4, phase, src & 0x00FFFFFFu, phys,
                        (uint32_t)std::min<uint64_t>(end64, 0x00FFFFFFu), len);
                    std::fflush(stderr);
                }
            }
        }
    }
    if (!rs64_g1d_blk_enabled() || len < 4u || kind == nullptr) return;
    rs64_g1d_blk_arm();
    const uint32_t phys = dest & 0x1FFFFFFFu;
    if (phys >= 0x01000000u) return;
    const uint64_t end64 = (uint64_t)phys + (uint64_t)len;
    if (end64 <= 0x800000ull) return;
    // s6199: a >=0x80 transfer that misses the wide node is not the fill.
    // Shorter transfers are logged only when they actually plant a
    // command-node word, so the wide 00010001 fill cannot hide under the
    // length filter.
    uint32_t hit_off = 0;
    uint32_t hit_word = 0;
    if (len < 0x80u) {
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (rd == nullptr) return;
        const uint32_t start = phys & ~3u;
        const uint32_t end = (uint32_t)std::min<uint64_t>(end64, 0x00FFFFFCu);
        bool hit = false;
        for (uint32_t a = start; a + 4u <= end; a += 4u) {
            uint32_t word = 0;
            for (uint32_t b = 0; b < 4u; ++b)
                word = (word << 8) | rd[(a + b) ^ 3u];
            if (word == 0x05200002u || word == 0x00010001u || word == 0x0001FFFFu) {
                hit = true;
                hit_off = a - phys;
                hit_word = word;
                break;
            }
        }
        if (!hit) return;
    }
    const uint64_t n = g_rs64_blk_n.fetch_add(1, std::memory_order_relaxed);
    if (n >= 200000u) {
        const uint64_t drop = g_rs64_blk_drop.fetch_add(1, std::memory_order_relaxed);
        if (drop == 0u) {
            std::fprintf(stderr, "[g1d-blk-ctl] cap=200000\n");
            std::fflush(stderr);
        }
        return;
    }
    const uint32_t end = (uint32_t)std::min<uint64_t>(end64, 0x00FFFFFFu);
    std::fprintf(stderr,
        "[g1d-blk] kind=%s src=0x%08X dest=0x%06X end=0x%06X len=0x%X pc=0x%08X "
        "before=%08X after=%08X phase=%u n=%llu\n",
        kind, src, phys, end, len, pc, hit_off, hit_word, rs64_phase_ord(),
        (unsigned long long)n);
    if ((n & 31u) == 0u || len < 0x80u) std::fflush(stderr);
}

extern "C" void rs64_g1d_blk_unaligned(char kind, uint32_t addr, uint32_t before,
                                       uint32_t after) {
    if (!rs64_g1d_blk_enabled()) return;
    if (after == before) return;
    if (after != 0x05200002u && after != 0x00010001u && after != 0x0001FFFFu) return;
    rs64_g1d_blk_arm();
    const uint32_t phys = addr & 0x1FFFFFFFu;
    if (phys >= 0x01000000u) return;
    static std::atomic<uint32_t> low_fill{0};
    if (after == 0x00010001u && phys < 0x800000u) {
        if (low_fill.fetch_add(1, std::memory_order_relaxed) >= 64u) return;
    }
    const char* name = "una";
    if (kind == 'L') name = "swl";
    else if (kind == 'R') name = "swr";
    else if (kind == 'l') name = "sdl";
    else if (kind == 'r') name = "sdr";
    const uint32_t pc = g_rs64_blk_ustore_pc ? g_rs64_blk_ustore_pc
                                             : (uint32_t)g_rs64_last_guest_pc;
    const uint64_t n = g_rs64_blk_n.fetch_add(1, std::memory_order_relaxed);
    if (n >= 200000u) {
        g_rs64_blk_drop.fetch_add(1, std::memory_order_relaxed);
        return;
    }
    std::fprintf(stderr,
        "[g1d-blk] kind=%s src=0x00000000 dest=0x%06X end=0x%06X len=0x4 pc=0x%08X "
        "before=%08X after=%08X phase=%u n=%llu\n",
        name, phys, phys + 4u, pc, before, after, rs64_phase_ord(),
        (unsigned long long)n);
    std::fflush(stderr);
}

extern "C" void rs64_g1d_fillpc_note(char width, uint32_t pc, uint32_t addr) {
    static std::atomic<int> armed{0};
    if (armed.exchange(1, std::memory_order_relaxed) == 0) {
        std::fprintf(stderr, "[g1d-fill-ctl] armed=1\n");
        std::fflush(stderr);
    }
    // before/before2 are the aligned word(s) before this store. rs_memset's
    // sb loop otherwise gets credit for a 00010001 word it did not change.
    struct Pend { uint32_t pc, phys, before, before2; char width; bool live; };
    static thread_local Pend pend{};
    static thread_local Rs64FillTls tls{};
    static thread_local uint32_t ticks = 0;
    Rs64FillState& st = rs64_fill_state();
    auto target_word = [](uint32_t word) {
        return word == 0x05200002u || word == 0x00010001u || word == 0x0001FFFFu;
    };
    if (pend.live) {
        const Pend done = pend;
        pend.live = false;
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (rd != nullptr && done.phys < 0x00FFFFF8u) {
            if (done.width == 'H' || done.width == 'B') {
                const uint32_t aligned = done.phys & ~3u;
                const uint32_t word = rs64_rdram_u32(rd, aligned);
                st.resolved.fetch_add(1, std::memory_order_relaxed);
                if (word) st.nonzero.fetch_add(1, std::memory_order_relaxed);
                if (word != done.before && target_word(word))
                    rs64_fill_note_word(&tls, done.pc, aligned, word, 4);
            } else {
                const uint32_t nwords = done.width == 'D' ? 2u : 1u;
                for (uint32_t i = 0; i < nwords; ++i) {
                    const uint32_t phys = done.phys + 4u * i;
                    const uint32_t word = rs64_rdram_u32(rd, phys);
                    const uint32_t prior = i == 0u ? done.before : done.before2;
                    st.resolved.fetch_add(1, std::memory_order_relaxed);
                    if (word) st.nonzero.fetch_add(1, std::memory_order_relaxed);
                    if (word != prior && target_word(word))
                        rs64_fill_note_word(&tls, done.pc, phys, word, 4);
                }
            }
        }
    }
    volatile uint8_t* rd_now = g_recomp_rdram_for_wp_raw;
    if (width == 'H') {
        const uint32_t phys = addr & 0x1FFFFFFFu;
        st.words.fetch_add(1, std::memory_order_relaxed);
        if ((phys & 1u) == 0u && phys < 0x00FFFFFEu && rd_now != nullptr) {
            const uint32_t aligned = phys & ~3u;
            pend = Pend{pc, phys, rs64_rdram_u32(rd_now, aligned), 0u, width, true};
        }
    } else if (width == 'B') {
        const uint32_t phys = addr & 0x1FFFFFFFu;
        st.words.fetch_add(1, std::memory_order_relaxed);
        if (phys < 0x00FFFFFCu && rd_now != nullptr) {
            const uint32_t aligned = phys & ~3u;
            pend = Pend{pc, phys, rs64_rdram_u32(rd_now, aligned), 0u, width, true};
        }
    } else if (width == 'W' || width == 'D') {
        const uint32_t phys = (addr & 0x1FFFFFFFu) & ~3u;
        st.words.fetch_add(1, std::memory_order_relaxed);
        if (phys < 0x01000000u && rd_now != nullptr) {
            const uint32_t before2 = width == 'D' && phys + 4u < 0x01000000u
                ? rs64_rdram_u32(rd_now, phys + 4u) : 0u;
            pend = Pend{pc, phys, rs64_rdram_u32(rd_now, phys), before2, width, true};
        }
    }
    if ((++ticks & 8191u) == 0u) {
        rs64_fill_commit_tls(&tls);
        std::lock_guard<std::mutex> lock(st.mu);
        const auto now = std::chrono::steady_clock::now();
        if (!st.ever || now - st.flushed >= std::chrono::milliseconds(500))
            rs64_fill_flush_summary_locked(st);
    }
}


extern "C" void rs64FloorWriterRecord(const char*, uint32_t, uint32_t, uint32_t,
                                        uint32_t, uint32_t, uint32_t, const char*, const char*);
namespace {
constexpr uint32_t kFloorWriterTarget = 0x00BB0020u;
constexpr uint32_t kFloorWriterOther[] = {0x00BB6020u, 0x00BB5FDEu, 0x00BB67DEu};
constexpr uint32_t kFloorWriterControl = 0x01FF0020u;
bool floorWriterOn() {
    static const bool on = std::getenv("ROGUESQ_FLOOR_DEPTH_DIR") != nullptr;
    return on;
}
uint32_t floorWriterWord(uint32_t p) {
    uint32_t w = 0;
    volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
    if (rd) for (uint32_t i = 0; i < 4; ++i) w = (w << 8) | rd[(p + i) ^ 3u];
    return w;
}
// s6689: ROGUESQ_FLOOR_WATCH=hex,hex,... adds physical watch words (max 8).
struct FloorWriterExtra { uint32_t t[8]; int n; };
const FloorWriterExtra& floorWriterExtra() {
    static const FloorWriterExtra extra = [] {
        FloorWriterExtra x{{}, 0};
        const char* e = std::getenv("ROGUESQ_FLOOR_WATCH");
        while (e && *e && x.n < 8) {
            char* end = nullptr;
            unsigned long v = std::strtoul(e, &end, 16);
            if (end == e) break;
            x.t[x.n++] = uint32_t(v) & 0x1FFFFFFCu;
            e = *end == ',' ? end + 1 : end;
        }
        return x;
    }();
    return extra;
}
uint32_t floorWriterHit(uint32_t p, uint32_t len) {
    for (uint32_t t : {kFloorWriterTarget, kFloorWriterControl, kFloorWriterOther[0], kFloorWriterOther[1], kFloorWriterOther[2]})
        if (p < t + 4u && uint64_t(p) + len > t) return t;
    const FloorWriterExtra& x = floorWriterExtra();
    for (int i = 0; i < x.n; ++i)
        if (p < x.t[i] + 4u && uint64_t(p) + len > x.t[i]) return x.t[i];
    return 0;
}
struct FloorWriterPending {
    uint32_t pc = 0, p = 0, len = 0, target = 0, before = 0, src = 0;
    const char* api = nullptr;
    std::string caller;
};
thread_local FloorWriterPending floorGuest, floorHost;
void floorWriterFinish(FloorWriterPending& pending, const char* cls) {
    if (!pending.target) return;
    FloorWriterPending old = pending;
    pending = {};
    rs64FloorWriterRecord(cls, old.pc, old.p, old.len, old.target, old.before,
        floorWriterWord(old.target), old.api, old.caller.c_str());
}
void floorWriterGuest(char width, uint32_t pc, uint32_t addr) {
    if (!floorWriterOn()) return;
    floorWriterFinish(floorGuest, "guest-delayed");
    uint32_t len = width == 'B' ? 1 : width == 'H' ? 2 : width == 'D' ? 8 : 4;
    uint32_t p = addr & 0x1FFFFFFFu;
    uint32_t target = floorWriterHit(p, len);
    if (target) floorGuest = {pc, p, len, target, floorWriterWord(target), 0, "scalar", {}};
}
}
extern "C" void rs64_floor_ownership(const char* kind, uint32_t ptr, uint32_t len, uint32_t pc) {
    if (!floorWriterOn() || kind == nullptr) return;
    const bool alloc = std::strcmp(kind, "malloc") == 0 || std::strcmp(kind, "free") == 0 ||
        std::strcmp(kind, "free-entry") == 0;
    if (alloc && (ptr < 0x80800000u || ptr >= 0x81000000u)) return;
    const uint32_t phys = ptr & 0x1FFFFFFFu;
    const bool image = std::strcmp(kind, "setzimg") == 0 || std::strcmp(kind, "setcimg") == 0;
    if (image) {
        if (phys < 0x100000u || phys >= 0x1000000u) return;
        static std::atomic<uint64_t> prev{0};
        const uint64_t key = (uint64_t(kind[3]) << 32) | phys;
        if (prev.exchange(key) == key) return;
    }
    auto rd = [](uint32_t a) { return floorWriterWord(a & 0x1FFFFFFFu); };
    std::string detail;
    char buf[512];
    for (uint32_t a = 0x801163D8u; a <= 0x801163F8u; a += 4) {
        std::snprintf(buf, sizeof buf, "%08X=%08X;", a, rd(a)); detail += buf;
    }
    for (uint32_t a : {0x8011A838u, 0x8011A83Cu, 0x8010FEFCu}) {
        std::snprintf(buf, sizeof buf, "%08X=%08X;", a, rd(a)); detail += buf;
    }
    const bool bytes = alloc || std::strcmp(kind, "clear") == 0 || std::strncmp(kind, "depth-read", 10) == 0;
    if (bytes) {
        const uint64_t end = uint64_t(phys) + len;
        for (uint32_t w : {0x00BB0020u, 0x00BB5FDEu, 0x00BB6020u, 0x00BB67DEu}) {
            std::snprintf(buf, sizeof buf, "cover%08X=%d;", w, phys <= w && end > w); detail += buf;
        }
    }
    const bool heavy = alloc || std::strcmp(kind, "clear") == 0 || std::strcmp(kind, "metadata") == 0;
    if (heavy) {
        if (ptr >= 0x80000010u && ptr < 0x81000000u) {
            std::snprintf(buf, sizeof buf, "ptr-header=%08X/%08X/%08X/%08X;", rd(ptr-16), rd(ptr-12), rd(ptr-8), rd(ptr-4)); detail += buf;
        }
        uint32_t desc = rd(0x8010FCB0u);
        if (desc >= 0x80000000u && desc < 0x81000000u - 0x48u) {
            for (uint32_t off : {0x18u, 0x24u, 0x28u, 0x2Cu, 0x30u, 0x34u, 0x38u, 0x44u}) {
                std::snprintf(buf, sizeof buf, "desc+%02X=%08X;", off, rd(desc + off)); detail += buf;
            }
        }
        static const uint32_t kWatchGuest[] = {0x80BB0020u, 0x80BB5FDEu, 0x80BB6020u, 0x80BB67DEu};
        for (uint32_t slot : {0x8010FEFCu, 0x8010FF00u, 0x8010FF18u}) {
            uint32_t a = rd(slot), end = 0; unsigned count = 0;
            while (a >= 0x80000000u && a < 0x81000000u - 16u && count < 4096u) {
                ++count;
                uint32_t w = rd(a), size = rd(a + 4), fl = w >> 16;
                if (size > 0x1000000u || uint64_t(a) + 16 + size > 0x81000000u) break;
                end = a + 16 + size;
                bool hit = ptr >= a && ptr < end;
                if (!hit) for (uint32_t g : kWatchGuest) if (a <= g && end > g) hit = true;
                if (hit) {
                    std::snprintf(buf, sizeof buf, "heap%08X:block=%08X,size=%08X,flags=%04X,tag=%04X;", slot, a, size, fl, w & 0xFFFFu);
                    detail += buf;
                }
                if (fl & 8u || size == 0) break;
                a = end;
            }
            std::snprintf(buf, sizeof buf, "heap%08X:head=%08X,end=%08X,n=%u%s;", slot, rd(slot), end, count,
                count >= 4096u ? ",trunc=1" : ""); detail += buf;
        }
        if (alloc) {
            void* bt[10]; int n = backtrace(bt, 10);
            for (int i = 1; i < n; ++i) {
                Dl_info info{}; dladdr(bt[i], &info);
                const char* name = info.dli_sname ? info.dli_sname : "?";
                std::snprintf(buf, sizeof buf, "%s+%llu;", name,
                    (unsigned long long)((uintptr_t)bt[i] - (uintptr_t)info.dli_saddr));
                for (char* c = buf; *c; ++c) if (*c == '"' || *c == '\n' || *c == '\\') *c = '_';
                detail += buf;
            }
        }
    }
    rs64FloorWriterRecord("ownership", pc, phys, len, kFloorWriterTarget,
        rd(0x801163E4u), rd(0x801163DCu), kind, detail.c_str());
}
extern "C" void rs64_floor_writer_post(char, uint32_t pc, uint32_t addr) {
    if (!floorWriterOn()) return;
    const uint32_t p = addr & 0x1FFFFFFFu;
    if ((p >= 0x1163D8u && p <= 0x1163F8u) || p == 0x10FEFCu || p == 0x10FF00u || p == 0x10FF18u)
        rs64_floor_ownership("metadata", addr, 4, pc);
    if (floorGuest.target && floorGuest.pc == pc && floorGuest.p == (addr & 0x1FFFFFFFu))
        floorWriterFinish(floorGuest, "guest-exact");
}
extern "C" void rs64_floor_writer_context(uint32_t pc, uint32_t ra,
    uint32_t dst, uint32_t fill, uint32_t len, uint32_t callsite) {
    if (!floorWriterOn() || !floorGuest.target || floorGuest.pc != pc) return;
    char args[180];
    std::snprintf(args, sizeof args, "dst=%08X fill=%08X len=%08X ra=%08X callsite=%08X;",
        dst, fill, len, ra, callsite);
    floorGuest.caller = args;
    rs64_floor_ownership("clear", dst, len, pc);
    void* bt[10];
    const int n = backtrace(bt, 10);
    for (int i = 1; i < n; ++i) {
        Dl_info info{};
        dladdr(bt[i], &info);
        char frame[256];
        std::snprintf(frame, sizeof frame, "%s+%llu;", info.dli_sname ? info.dli_sname : "?",
            (unsigned long long)((uintptr_t)bt[i] - (uintptr_t)info.dli_saddr));
        floorGuest.caller += frame;
    }
}
extern "C" void rs64_floor_writer_flush() {
    if (floorWriterOn()) floorWriterFinish(floorGuest, "guest-delayed");
}
extern "C" void rs64_floor_writer_unaligned(char kind, uint32_t addr,
                                             uint32_t before, uint32_t after) {
    if (!floorWriterOn()) return;
    const uint32_t p = addr & 0x1FFFFFFFu;
    const uint32_t target = floorWriterHit(p, 4);
    if (!target) return;
    const char* api = kind == 'L' ? "swl" : kind == 'R' ? "swr" : kind == 'l' ? "sdl" : "sdr";
    rs64FloorWriterRecord("guest-exact", g_rs64_blk_ustore_pc, p, 4, target, before, after, api, "helper");
}
extern "C" void rs64_floor_writer_begin(const uint8_t* rd, uint32_t p,
                                          uint32_t len, const char* api) {
    if (!floorWriterOn() || rd != g_recomp_rdram_for_wp_raw) return;
    floorWriterFinish(floorGuest, "guest-delayed");
    const uint32_t target = floorWriterHit(p, len);
    if (!target) return;
    void* bt[10];
    int n = backtrace(bt, 10);
    std::string caller;
    for (int i = 1; i < n; ++i) {
        Dl_info info{};
        char frame[256];
        dladdr(bt[i], &info);
        std::snprintf(frame, sizeof frame, "%s+%llu;", info.dli_sname ? info.dli_sname : "?",
            (unsigned long long)((uintptr_t)bt[i] - (uintptr_t)info.dli_saddr));
        caller += frame;
    }
    floorHost = {0, p, len, target, floorWriterWord(target), 0, api, caller};
}
extern "C" void rs64_floor_writer_after(const uint8_t* rd, uint32_t p,
                                          uint32_t len, const char* api) {
    if (!floorWriterOn() || rd != g_recomp_rdram_for_wp_raw) return;
    if (floorHost.target && floorHost.p == p && floorHost.len == len &&
        std::strcmp(floorHost.api, api) == 0) floorWriterFinish(floorHost, "host");
}
extern "C" void bzero_recomp(uint8_t*, recomp_context*);
extern "C" void rs64_floor_writer_control() {
    static std::atomic<bool> done{false};
    if (!floorWriterOn() || !g_recomp_rdram_for_wp_raw || done.exchange(true)) return;
    uint8_t* rd = const_cast<uint8_t*>(g_recomp_rdram_for_wp_raw);
    const uint32_t marker = 0x12345678u;
    for (uint32_t i = 0; i < 4; ++i) rd[(kFloorWriterControl+i)^3u] = marker >> (24-8*i);
    recomp_context ctx{};
    ctx.r4 = (uint64_t)(int64_t)(int32_t)(0x80000000u + kFloorWriterControl);
    ctx.r5 = 4;
    bzero_recomp(rd, &ctx);
    rs64_floor_writer_flush();
    for (uint32_t i = 0; i < 4; ++i) rd[(kFloorWriterControl+i)^3u] = marker >> (24-8*i);
    rs64_floor_writer_begin(rd, kFloorWriterControl, 4, "control-memset");
    std::memset(rd + kFloorWriterControl, 0, 4);
    rs64_floor_writer_after(rd, kFloorWriterControl, 4, "control-memset");
}

extern "C" void rs64_m5_route_value_writer(char width, uint32_t pc,
                                              uint32_t addr,
                                              uint32_t value) {
    static const bool g1d_fillpc = [] {
        const char* e = std::getenv("ROGUESQ_LOG_G1D_FILLPC");
        return e && *e && *e != '0';
    }();
    floorWriterGuest(width, pc, addr);
    if (g1d_fillpc) rs64_g1d_fillpc_note(width, pc, addr);
    rs64_m5_pre_dma_writer_store(width, pc, addr, value);
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    static bool control = false;
    if (!control) {
        control = true;
        std::fprintf(stderr, "[m5-route-writer-control] scalar-store census is live\n");
        std::fflush(stderr);
    }
    const uint32_t width_n = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width_n == 1024u &&
                        (origin == 0x00790400u || origin == 0x00790800u)) ||
                       (width_n == 512u && origin == 0x006AB400u);
    if (!target) return;
    const uint32_t phys = (addr - 0x80000000u) & 0x1FFFFFFFu;
    if (phys < 0x128C80u || phys >= 0x128D20u) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width_n << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-route-writer] n=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X width=%c phys=0x%06X addr=0x%08X value=0x%08X\n",
        rows++, rs64_phase_ord(), width_n, origin, pc, width, phys, addr, value);
    std::fflush(stderr);
}

extern "C" void rs64_m5_exact_route_store(char width, unsigned pc,
                                             unsigned addr, unsigned value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_EXACT_ROUTE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    static std::atomic<bool> control{false};
    if (!control.exchange(true, std::memory_order_relaxed)) {
        std::fprintf(stderr, "[m5-exact-route-control] offset-class witness is live\n");
        std::fflush(stderr);
    }
    if (!enabled) return;
    const uint32_t phys = (addr - 0x80000000u) & 0x1FFFFFFFu;
    if (phys != 0x128C92u && phys != 0x128CD0u) return;
    const uint32_t width_n = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width_n == 1024u && origin == 0x00790400u) ||
                        (width_n == 512u && origin == 0x006AB400u);
    if (!target) return;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width_n << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr,
            "[m5-exact-route-phase-control] width=%u origin=0x%06X\n",
            width_n, origin);
    }
    if (rows++ >= 512u) return;
    std::fprintf(stderr,
        "[m5-exact-route] n=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "width=%c phys=0x%06X value=0x%08X\n",
        rows - 1u, rs64_phase_ord(), width_n, origin, pc, width, phys, value);
    std::fflush(stderr);
}

extern "C" void rs64_m5_route_prepare_inputs(
    uint8_t* rdram, uint32_t pc, uint32_t caller, uint32_t sp,
    uint32_t s0, uint32_t s1, uint32_t s2, uint32_t s3, uint32_t s4,
    uint32_t s5, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t v0,
    uint32_t message_type, uint32_t source_word, uint32_t source_byte,
    uint32_t branch_state) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_PREPARE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || rdram == nullptr) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 256u) return;
    const uint32_t route_target =
        ((width == 1024u && origin == 0x00790400u) ||
         (width == 512u && origin == 0x006AB400u)) ? 1u : 0u;
    const uint32_t branch = message_type == 2u ? 2u :
                            message_type >= 3u ? 3u :
                            message_type == 1u ? 1u : 0u;
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    std::fprintf(stderr,
        "[route-prep] n=%u phase=%u width=%u origin=0x%06X target=%u "
        "accepted=%u pc=0x%08X caller=0x%08X sp=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X s3=0x%08X s4=0x%08X s5=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X v0=0x%08X msg=0x%02X branch=%u "
        "source_word=0x%08X source_byte=0x%02X branch_state=0x%04X "
        "active=%u ordinal=%u row=%u exit=%d\n",
        rows, rs64_phase_ord(), width, origin, route_target, route_target,
        pc, caller, sp, s0, s1, s2, s3, s4, s5, a0, a1, a2, v0,
        message_type, branch, source_word, source_byte, branch_state,
        active ? 1u : 0u, ordinal, route_row, exit_reason);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_producer_mark_handoff(uint8_t* rdram, uint32_t edge,
                                                 uint32_t caller, uint32_t s0,
                                                 uint32_t s1, uint32_t a0,
                                                 uint32_t a1, uint32_t a2,
                                                 uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_HANDOFF");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !rdram) return;
    static std::mutex mutex;
    static uint32_t key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t next_key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != next_key) { key = next_key; rows = 0; }
    if (rows++ >= 512u) return;
    const auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    const auto word = [&byte](uint32_t guest) -> uint32_t {
        return (byte(guest) << 24) | (byte(guest + 1u) << 16) |
               (byte(guest + 2u) << 8) | byte(guest + 3u);
    };
    const uint32_t target = ((width == 1024u && origin == 0x00790400u) ||
                             (width == 512u && origin == 0x006AB400u)) ? 1u : 0u;
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    uint64_t task_generation = 0;
    uint64_t source_event = 0;
    uint32_t latest_route_seq = 0xFFFFFFFFu;
    uint32_t latest_route_ordinal = 0xFFFFFFFFu;
    uint32_t latest_route_row = 0xFFFFFFFFu;
    rs64_m5_audio_dma_identity(&source_event, &task_generation,
                               &latest_route_seq, &latest_route_ordinal,
                               &latest_route_row);
    if (task_generation == 0) {
        task_generation = rs64_m5_latest_audio_generation();
    }
    const uint64_t event = target ? rs64_m5_route_handoff_event(
        edge == 0u ? "handoff-entry" : (edge == 1u ? "handoff-exit" : "handoff-call"),
        caller, active ? 1u : 0u, arm, phase, width, origin, ordinal, route_row,
        edge, a0, a2) : 0u;
    std::fprintf(stderr,
        "[m5-route-handoff] edge=%s n=%u phase=%u width=%u origin=0x%06X "
        "target=%u caller=0x%08X s0=0x%08X s1=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X v0=0x%08X count=%u states=%u,%u,%u,%u,%u,%u "
        "pending=0x%08X/0x%08X sel=%02X/%02X/%02X event=%llu "
        "route_ordinal=%u route_row=%u active=%u exit=%d "
        "task_generation=%llu source_event=%llu\n",
        edge == 0u ? "entry" : (edge == 1u ? "exit" : "call"), rows - 1u,
        phase, width, origin, target,
        caller, s0, s1, a0, a1, a2, v0, byte(0x80128EADu),
        byte(0x80128EAAu), byte(0x80128EABu), byte(0x80128EACu),
        byte(0x80128EADu), byte(0x80128EAEu), byte(0x80128EAFu),
        word(0x80128E94u), word(0x80128E90u), byte(0x8012A865u),
        byte(0x8012A864u), byte(0x8012A862u),
        static_cast<unsigned long long>(event), ordinal, route_row,
        active ? 1u : 0u, exit_reason,
        static_cast<unsigned long long>(task_generation),
        static_cast<unsigned long long>(source_event));
    std::fflush(stderr);
}

extern "C" void rs64_m5_b40_read(uint8_t* /*rdram*/, uint32_t read_pc,
                                  uint32_t value, uint32_t branch_pc,
                                  uint32_t branch_taken) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_B40_READ");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;

    static std::atomic<uint32_t> phase_key{0xFFFFFFFFu};
    static std::atomic<uint32_t> phase_row{0};
    const uint32_t key = (width << 24) ^ origin;
    uint32_t prior = phase_key.load(std::memory_order_relaxed);
    if (prior != key && phase_key.compare_exchange_strong(
            prior, key, std::memory_order_relaxed)) {
        phase_row.store(0, std::memory_order_relaxed);
    }
    const uint32_t row = phase_row.fetch_add(1, std::memory_order_relaxed);
    if (row >= 4096u) return;

    const char* b40 = std::getenv("ROGUESQ_M5_B40_VALUE");
    const char* c88 = std::getenv("ROGUESQ_M5_C88_VALUE");
    std::fprintf(stderr,
        "[m5-b40-read] arm=%s b40=%u c88=%u row=%u phase=%u width=%u "
        "origin=0x%06X pc=0x%08X value=0x%02X branch_pc=0x%08X "
        "branch_dir=%u route_ordinal=%u\n",
        (b40 && b40[0] && b40[0] != '0') ? "treatment" : "control",
        (b40 && b40[0] && b40[0] != '0') ? 1u : 0u,
        rs64_s7715_c88_label(c88), row,
        rs64_phase_ord(), width, origin & 0x00FFFFFFu, read_pc,
        value & 0xFFu, branch_pc, branch_taken,
        g_rs64_m5_b40_route_ordinal.load(std::memory_order_relaxed));
    std::fflush(stderr);
}

extern "C" void rs64_m5_b40_route_title_transition(void) {
    static std::atomic<bool> seen{false};
    bool expected = false;
    if (!seen.compare_exchange_strong(expected, true, std::memory_order_relaxed)) return;
    rs64_m5_b40_route_event("title-transition", 0u, 0xFFFFFFFFu,
                            0xFFFFFFFFu, 0xFFFFFFFFu);
}

extern "C" int rs64_is_hangar_vi(void) {
    ultramodern::renderer::ViRegs *vi = ultramodern::renderer::get_vi_regs();
    if (vi->VI_WIDTH_REG != 512u) return 0;
    const uint32_t o = vi->VI_ORIGIN_REG & 0x00FFFFFFu;
    return (o == 0x006ab400u || o == 0x006ab800u) ? 1 : 0;
}

extern "C" void osViSetXScale_recomp(uint8_t* rdram, recomp_context* ctx) {
    static int s_count = 0;
    int n = ++s_count;
    if (n <= 4) {
        fprintf(stderr, "[osViSetXScale #%d] scale=%f\n", n, (double)ctx->f12.fl);
        fflush(stderr);
    }
    extern void osViSetXScale(float scale);
    osViSetXScale(ctx->f12.fl);
}

extern "C" void osViSetYScale_recomp(uint8_t* rdram, recomp_context* ctx) {
    static int s_count = 0;
    int n = ++s_count;
    if (n <= 4) {
        fprintf(stderr, "[osViSetYScale #%d] scale=%f\n", n, (double)ctx->f12.fl);
        fflush(stderr);
    }
    extern void osViSetYScale(float scale);
    osViSetYScale(ctx->f12.fl);
}

// osGetMemSize override — defaults to 8MB (Expansion Pak present, hi-res
// mode available). ROGUESQ_MEM_SIZE_MB=4 forces 4MB to test base-N64 lo-res
// path. 2026-05-13 test confirmed 4MB alone crashes boot in mainBootstrapWorker
// (game still goes hi-res because the mode flag is gated on more than memsize),
// so the env var is a knob, not a recommended setting.
extern "C" void osGetMemSize_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    static int s_mb = -1;
    if (s_mb < 0) {
        const char* v = std::getenv("ROGUESQ_MEM_SIZE_MB");
        s_mb = (v && *v) ? std::atoi(v) : 8;
        if (s_mb != 8) {
            fprintf(stderr, "[osGetMemSize] reporting %d MB (env override)\n", s_mb);
            fflush(stderr);
        }
    }
    ctx->r2 = (gpr)(s_mb * 1024 * 1024);
}

// zmemcpy is stubbed in rogue_squadron.toml because the original MIPS code
// at 0x80018F4C contains a `cache 0x0D` instruction unsupported by N64Recomp.
// The toml comment claims "the runtime provides memcpy" but no such
// implementation existed — leaving zmemcpy as an empty body. That made
// zlib's inflate_flush a no-op (it calls zmemcpy to copy from the sliding
// window to the user's next_out buffer), so every decompressed asset stayed
// all-zero. This is the actual implementation: byte-by-byte copy honoring
// the recompile's XOR-3 byte swizzle on each access.
//
// Signature: void zmemcpy(Bytef *dest, const Bytef *source, uInt len);
//   a0/r4 = dest (MIPS virtual address)
//   a1/r5 = source (MIPS virtual address)
//   a2/r6 = len (byte count)
/* s7490 class EO: the LIVE zmemcpy is this host body (RECOMP_FUNC is weak on clang, so the generated, hooked 0x80018EF4 body is
   dead code; 72 guest call sites). Its byte stores and loads bypassed RS64_S5798_ST / RS64_S7484_LD, so the s7475 slack canary (EB),
   s7480 UAF-store (EH) and s7484 UAF-load (EI) watches never saw a guest memcpy. Each marked byte now goes through the same host entry
   points (fn=zmemcpy_host, pc = the generated sb 0x80018F30 / lbu 0x80018F28). ROGUESQ_S7490_ZHOOK=0 = old (unhooked). Control:
   ROGUESQ_S7490_ZPLANT=<s> (needs S7480_UAF; replaces S7480_PLANT): <s> s after arming, the first zmemcpy whose dest lies inside a
   live canary block (req >= 0x40) records that block as freed (s7480 plant 1, guest memory untouched) BEFORE the copy, so the copy's
   own first byte MUST log `[s7480] plant DETECTED ... fn=zmemcpy_host`. `[s7490] sum` = calls/bytes/marked bytes. Measurement only. */
extern "C" int rs64_s7475_store(uint32_t pc, uint32_t a, int w, const char* fn);
static uint64_t s_s7490_calls = 0, s_s7490_bytes = 0, s_s7490_wmark = 0, s_s7490_rmark = 0, s_s7490_heap = 0;
static int s_s7490_plant = 0;
static bool s7490_zhook() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7490_ZHOOK"); return !(e && e[0] == '0'); }(); return on; }
static inline bool s7490_marked(uint32_t a) {
    const uint32_t o = a - 0x80000000u; return o < 0x1800000u && ((g_rs64_s7475_bm[o >> 3] >> (o & 7u)) & 1u); }
static void s7490_pre(uint32_t dst, uint32_t len) {
    ++s_s7490_calls; s_s7490_bytes += len;
    static const double zp = [] { const char* e = std::getenv("ROGUESQ_S7490_ZPLANT"); if (!e || !*e || *e == '0') return -1.0; return std::atof(e); }();
    std::lock_guard<std::mutex> lk(s_s7475_mu);
    auto it = s_s7475_live.upper_bound(dst); bool inheap = false;
    if (it != s_s7475_live.begin()) { --it; inheap = dst < it->first + it->second.sz; }
    if (inheap) ++s_s7490_heap;
    if (zp < 0 || s_s7490_plant || !inheap || !s7480_on() || s_s7480_plant != 0 || it->second.req < 0x40u || dst >= it->first + it->second.req) return;
    const double now = s7325_now(); if (now - s_s7475_t0 < zp) return;
    s_s7490_plant = 1; ++s_s7480_ptries; s7480_add(it->first, it->second.req, now, 1); s_s7480_plant = 1; s_s7480_ptime = now;
    std::fprintf(stderr, "[s7490] zplant SET blk=%08X req=%X dst=%08X len=%X t=%.1f\n", it->first, it->second.req, dst, len, now - s_s7475_t0); }
extern "C" void rs64_s7490_sum(double now) {
    std::fprintf(stderr, "[s7490] sum t=%.1f zhook=%d calls=%llu bytes=%llu heap_calls=%llu wmark=%llu rmark=%llu zplant=%d\n", now - s_s7475_t0, (int)s7490_zhook(),
                 (unsigned long long)s_s7490_calls, (unsigned long long)s_s7490_bytes, (unsigned long long)s_s7490_heap,
                 (unsigned long long)s_s7490_wmark, (unsigned long long)s_s7490_rmark, s_s7490_plant); }
/* s7491 class EP: host stores through guest pointers made by OS-call bodies (ultramodern mesgqueue do_send/do_recv/osCreateMesgQueue,
   osCreateThread; librecomp cont.cpp osContInit/GetQuery/GetReadData, pi.cpp save_read + OSIoMesg fill; osDpGetCounters here). Each
   site calls RS64_S7491(a, w, kind) after its store (weak decl in lib/, resolved here). Marked bytes go through rs64_s7475_store with
   pc = 0xE0000000 + kind index and fn = the kind, so the s7475 slack canary and s7480 UAF-store watch see them (rows fn=os_*).
   Every call is classed by destination: H = inside a live canary-recorded rs_malloc block, B = static image (< 0x80140000, .data/.bss),
   O = other (stack / arena / framebuffer region). Control ROGUESQ_S7491_MPLANT=<s> (needs S7480_UAF, no other s7480 plant):
   <s> s after arming, the first EP store into a live canary block (req >= 0x40) records that block as freed (guest memory
   untouched) before routing, so the same store MUST log `[s7480] plant DETECTED ... fn=os_*`; if no heap destination appears within
   <s>+30 s, the next EP destination of any class is planted instead (route control for static destinations). Measurement only. */
static const char* const k_s7491_kind[] = {"os_createmq", "os_send", "os_jam", "os_recv", "os_recv_out", "os_createthread", "os_continit",
    "os_contquery", "os_contread", "os_saveread", "os_iomesg", "os_dpcounters", "os_tq_link", "os_tq_head", "os_rt64fb"};
enum { S7491_NK = 15 };  /* s7492 class EQ: +os_tq_link/os_tq_head (threadqueue.cpp), +os_rt64fb (RT64 copyNativeToRAM, main.cpp) */
static uint64_t s_s7491_calls[S7491_NK] = {0}, s_s7491_cls[S7491_NK][3] = {{0}}, s_s7491_mark[S7491_NK] = {0};
static uint32_t s_s7491_lo[S7491_NK] = {0}, s_s7491_hi[S7491_NK] = {0};
static int s_s7491_plant = 0;
extern "C" int rs64_s7475_store(uint32_t pc, uint32_t a, int w, const char* fn);
extern "C" void rs64_s7491_hst(uint32_t a, uint32_t w, const char* kind) {
    if (s7545_on()) { if (kind && !std::strcmp(kind, "os_createthread")) rs64_s7545_create(a); if (kind && !std::strcmp(kind, "os_destroythread")) rs64_s7545_destroy(a); if (kind && w) s7545_host(a, w, kind); return; }  /* s7545 class GE */
    if (!g_rs64_s7475_bm || !kind || w == 0 || w > 0x200000u || a < 0x80000000u || a >= 0x81800000u) return;
    int k = 0; while (k < S7491_NK && std::strcmp(kind, k_s7491_kind[k])) ++k; if (k == S7491_NK) return;
    if (w > 0x10000u && k != 14) return;  /* only the RT64 framebuffer writeback is allowed whole-image widths */
    static const double mp = [] { const char* e = std::getenv("ROGUESQ_S7491_MPLANT"); if (!e || !*e || *e == '0') return -1.0; return std::atof(e); }();
    /* s7492: ROGUESQ_S7491_MPLANT_KIND=<kind> restricts the plant to one kind (per-site positive control for the EQ hooks) */
    static const char* const mpk = [] { const char* e = std::getenv("ROGUESQ_S7491_MPLANT_KIND"); return (e && *e) ? e : (const char*)nullptr; }();
    {   std::lock_guard<std::mutex> lk(s_s7475_mu);
        ++s_s7491_calls[k]; if (!s_s7491_lo[k] || a < s_s7491_lo[k]) s_s7491_lo[k] = a; if (a + w > s_s7491_hi[k]) s_s7491_hi[k] = a + w;
        auto it = s_s7475_live.upper_bound(a); bool inheap = false;
        if (it != s_s7475_live.begin()) { --it; inheap = a < it->first + it->second.sz; }
        const int c = inheap ? 0 : a < 0x80140000u ? 1 : 2; ++s_s7491_cls[k][c];
        if (mp >= 0 && !s_s7491_plant && s7480_on() && s_s7480_plant == 0 && (!mpk || !std::strcmp(mpk, kind))) {
            const double now = s7325_now(), age = now - s_s7475_t0;
            const bool heap_ok = inheap && it->second.req >= 0x40u && a + w <= it->first + it->second.req;
            if (age >= mp && (heap_ok || age >= mp + 30.0)) {
                const uint32_t pb = heap_ok ? it->first : (a & ~0xFu), pn = heap_ok ? it->second.req : ((a + w + 0xFu) & ~0xFu) - (a & ~0xFu);
                s_s7491_plant = heap_ok ? 1 : 2; ++s_s7480_ptries; s7480_add(pb, pn, now, 1); s_s7480_plant = 1; s_s7480_ptime = now;
                std::fprintf(stderr, "[s7491] mplant SET kind=%s class=%c blk=%08X n=%X a=%08X w=%u t=%.1f\n", kind, heap_ok ? 'H' : "HBO"[c], pb, pn, a, w, age); } } }
    if (k == 14 && rs64_s7501_on) return;  /* s7501 EZ: fb bytes are marked; the writeback itself is already a ring event (main.cpp s7501_wb) */
    for (uint32_t i = 0; i < w && a + i < 0x81800000u; ++i) {  /* s7560 AO: a < 0x81800000 and w <= 0x200000 still let a + w run past the 0x300000-byte bitmap */
        const uint32_t b = a + i, o = b - 0x80000000u;
        if ((g_rs64_s7475_bm[o >> 3] >> (o & 7u)) & 1u) { ++s_s7491_mark[k]; rs64_s7475_store(0xE0000000u + (uint32_t)k, b, 1, kind); } } }
extern "C" void rs64_s7491_sum(double now) {
    std::string b; char t[160];
    for (int k = 0; k < S7491_NK; ++k) { if (!s_s7491_calls[k]) continue;
        snprintf(t, sizeof t, " %s=%llu:H%llu,B%llu,O%llu,m%llu[%08X-%08X]", k_s7491_kind[k], (unsigned long long)s_s7491_calls[k], (unsigned long long)s_s7491_cls[k][0],
                 (unsigned long long)s_s7491_cls[k][1], (unsigned long long)s_s7491_cls[k][2], (unsigned long long)s_s7491_mark[k], s_s7491_lo[k], s_s7491_hi[k]); b += t; }
    std::fprintf(stderr, "[s7491] sum t=%.1f mplant=%d kinds(calls:heap,static,other,marked[range])%s\n", now - s_s7475_t0, s_s7491_plant, b.c_str()); }
extern "C" void zmemcpy(uint8_t* rdram, recomp_context* ctx) {
    // Use the full 64-bit register values for the bounds check. The MEM_BU
    // macro does (reg + offset) ^ 3 - 0xFFFFFFFF80000000 in 64-bit, so
    // truncating to uint32_t can mask sign-extension issues.
    uint64_t dest_full = (uint64_t)ctx->r4;
    uint64_t src_full  = (uint64_t)ctx->r5;
    uint64_t len_full  = (uint64_t)ctx->r6;
    constexpr uint64_t KSEG0_BASE = 0xFFFFFFFF80000000ull;
    const uint64_t KSEG0_END  = 0xFFFFFFFF00000000ull + rs64_ram_top;
    constexpr uint32_t KSEG0_BASE_LO = 0x80000000u;
    const uint32_t KSEG0_END_LO  = rs64_ram_top;
    auto in_range = [&](uint64_t addr_full, uint64_t n) {
        // Accept either sign-extended (0xFFFFFFFF80...) or zero-extended (0x80...)
        // as long as it lands within the 8MB rdram region.
        if (addr_full >= KSEG0_BASE && addr_full + n <= KSEG0_END) return true;
        uint32_t lo = (uint32_t)addr_full;
        if (lo >= KSEG0_BASE_LO && (uint64_t)lo + n <= KSEG0_END_LO &&
            (addr_full >> 32) == 0) return true;
        return false;
    };
    if (len_full > 0 && (!in_range(dest_full, len_full) || !in_range(src_full, len_full))) {
        static int s_warned = 0;
        if (s_warned++ < 8) {
            fprintf(stderr, "[zmemcpy] OOB skip dst=0x%016llX src=0x%016llX len=%llu\n",
                    (unsigned long long)dest_full,
                    (unsigned long long)src_full,
                    (unsigned long long)len_full);
            fflush(stderr);
        }
        ctx->r2 = ctx->r4;  // zlib's zmemcpy returns nothing meaningful
        return;
    }
    // Use full gpr (uint64_t) values for MEM_BU/MEM_B. Truncating to uint32_t
    // breaks the macro's `- 0xFFFFFFFF80000000` arithmetic under C integer
    // promotion (uint32 + int64 = the uint32 gets zero-extended, so subtracting
    // a sign-extended int64 produces a 4GB-offset host pointer → AV).
    /* s7810: canonicalise to the sign-extended KSEG0 form, as retail's `addu t5, a0, zero` (ADD32) does. in_range() accepts a
       zero-extended 0x00000000_80xxxxxx pointer, and MEM_BU/MEM_B on that form index rdram + 4 GB (outside even the 4 GB
       reservation) -> host fault where the recompiled retail body copies correctly (tools/s7810_host_override_diff.py). */
    gpr dest_reg = (gpr)(int64_t)(int32_t)(uint32_t)ctx->r4;
    gpr src_reg  = (gpr)(int64_t)(int32_t)(uint32_t)ctx->r5;
    uint32_t len = (uint32_t)len_full;
    rs64_f5_host_write_begin(rdram, (uint32_t)dest_reg & 0x1FFFFFFFu, len, "zmemcpy");
    if (g_rs64_s7475_bm && s7490_zhook()) {  /* s7490 class EO: route marked bytes through the guest store/load watches */
        const uint32_t d0 = (uint32_t)dest_reg, s0 = (uint32_t)src_reg; s7490_pre(d0, len);
        for (uint32_t i = 0; i < len; ++i) {
            if (g_rs64_s7484_on && s7490_marked(s0 + i)) { ++s_s7490_rmark; rs64_s7484_load(0x80018F28u, s0 + i, 1, "zmemcpy_host"); }
            ctx->r2 = MEM_BU(i, src_reg);
            MEM_B(i, dest_reg) = ctx->r2;
            if (s7490_marked(d0 + i)) { ++s_s7490_wmark; rs64_s7475_store(0x80018F30u, d0 + i, 1, "zmemcpy_host"); }
        }
    } else
    for (uint32_t i = 0; i < len; ++i) {
        ctx->r2 = MEM_BU(i, src_reg);
        MEM_B(i, dest_reg) = ctx->r2;
    }
    rs64_m5_host_write_census(rdram, (uint32_t)dest_reg & 0x1FFFFFFFu,
                              len, "zmemcpy");
    {
        uint32_t pc = (uint32_t)ctx->r31;
        if (pc < 0x80000000u) pc = (uint32_t)g_rs64_last_guest_pc;
        rs64_g1d_blk_dma("zmemcpy", (uint32_t)src_reg, (uint32_t)dest_reg, len, pc);
    }
    ctx->r2 = ctx->r4;  // zlib's zmemcpy returns nothing meaningful
}

// heapWalker cycle-detection state. Updated by hooks in funcs_3.c (entry +
// loop-top). When the walk revisits its starting pointer, the hook breaks
// out of the loop instead of spinning forever.
extern "C" unsigned g_heapwalker_initial = 0;
extern "C" unsigned g_heapwalker_iter = 0;

// tickTextureMaterialExpiry cycle-detection state. Inner walk over the
// material list can loop forever when a node's next ptr points back into
// the visited set. KSEG0 guards prevent AVs but not cycles. Reset at
// function entry; capped iter count + first-node-revisit triggers bailout.
extern "C" unsigned g_tick_walker_first = 0;
extern "C" unsigned g_tick_walker_iter  = 0;

// Watchdog for the cinematic inner loop. cinematicLoopBody iterates many
// times per cutscene playback; if it stops iterating for more than 2 seconds
// while the rest of the runtime keeps ticking, the game thread is hung in
// some callee. We capture the game thread's stack to find which one.
#ifdef _WIN32
static std::atomic<DWORD> g_cine_tid{0};
static std::atomic<uint64_t> g_cine_iter{0};
static std::atomic<uint64_t> g_cine_last_ms{0};

extern "C" void rs64_cine_dump_if_stuck(void);
extern "C" void rs64_cine_progress_log(void);
extern "C" void rs64_cine_start_watchdog_thread(void);

extern "C" void rs64_cine_iter_tick(unsigned iter) {
    g_cine_tid.store(GetCurrentThreadId(), std::memory_order_relaxed);
    g_cine_iter.store(iter, std::memory_order_relaxed);
    g_cine_last_ms.store(GetTickCount64(), std::memory_order_relaxed);
    // First tick spawns the dedicated watchdog thread.
    rs64_cine_start_watchdog_thread();
}

// Spawn a dedicated watchdog thread the first time iter_tick fires. The
// gfx_thread's update_screen path could itself be deadlocked behind the
// same mutex chain that's hanging the game thread (events_context.message_mutex
// in ultramodern, in particular), so polling from gfx_thread isn't reliable.
// A standalone thread that only uses Sleep + atomics is immune.
extern "C" void rs64_cine_start_watchdog_thread(void) {
    static std::atomic<bool> s_started{false};
    bool was = s_started.exchange(true, std::memory_order_relaxed);
    if (was) return;
    std::thread([]() {
        for (;;) {
            ::Sleep(500);
            rs64_cine_progress_log();
            rs64_cine_dump_if_stuck();
        }
    }).detach();
}

// Periodic progress log so we can see whether the inner loop is iterating
// at all and at what rate. Called from update_screen on a coarse schedule.
extern "C" void rs64_cine_progress_log(void) {
    static uint64_t s_last_log_ms = 0;
    static uint64_t s_last_log_iter = 0;
    uint64_t now = GetTickCount64();
    if (now - s_last_log_ms < 2000) return;  // 2s cadence
    uint64_t cur = g_cine_iter.load(std::memory_order_relaxed);
    uint64_t delta = cur - s_last_log_iter;
    uint64_t age_ms = (g_cine_last_ms.load() ? now - g_cine_last_ms.load() : 0);
    fprintf(stderr, "[cine-progress] iter=%llu delta=%llu in %llums (idle=%llums)\n",
            (unsigned long long)cur, (unsigned long long)delta,
            (unsigned long long)(now - s_last_log_ms),
            (unsigned long long)age_ms);
    fflush(stderr);
    s_last_log_ms = now;
    s_last_log_iter = cur;
}

extern void print_stack_with_symbols(void** frames, USHORT count);

extern "C" void rs64_cine_dump_if_stuck(void) {
    static std::atomic<bool> s_dumped{false};
    if (s_dumped.load(std::memory_order_relaxed)) return;

    uint64_t last = g_cine_last_ms.load(std::memory_order_relaxed);
    if (last == 0) return;  // never started iterating

    uint64_t now = GetTickCount64();
    if (now - last < 2000) return;  // not stuck yet

    DWORD tid = g_cine_tid.load(std::memory_order_relaxed);
    if (tid == 0) return;

    bool expected = false;
    if (!s_dumped.compare_exchange_strong(expected, true)) return;  // single shot

    fprintf(stderr, "[cine-watchdog] freeze detected: tid=%lu iter=%llu idle=%llums — opening thread\n",
            tid, (unsigned long long)g_cine_iter.load(), (unsigned long long)(now - last));
    fflush(stderr);

    // Try several access masks — some Win10 builds reject the wide masks.
    DWORD masks[] = {
        THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT,
        THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT | THREAD_QUERY_LIMITED_INFORMATION,
        0x1F03FF,  // pre-Vista THREAD_ALL_ACCESS
        0x1FFFFF,  // Vista+ THREAD_ALL_ACCESS
    };
    HANDLE hThread = NULL;
    DWORD last_err = 0;
    for (DWORD m : masks) {
        hThread = OpenThread(m, FALSE, tid);
        if (hThread) {
            fprintf(stderr, "[cine-watchdog] OpenThread succeeded with mask=0x%lX\n", m);
            break;
        }
        last_err = GetLastError();
    }
    if (hThread == NULL) {
        fprintf(stderr, "[cine-watchdog] OpenThread failed for tid=%lu last_err=%lu (cur tid=%lu)\n",
                tid, last_err, GetCurrentThreadId());
        fflush(stderr);
        s_dumped.store(false, std::memory_order_relaxed);
        return;
    }
    fprintf(stderr, "[cine-watchdog] opened, suspending\n"); fflush(stderr);
    DWORD susp = SuspendThread(hThread);
    if (susp == (DWORD)-1) {
        fprintf(stderr, "[cine-watchdog] SuspendThread failed err=%lu\n", GetLastError());
        fflush(stderr);
        CloseHandle(hThread);
        return;
    }
    fprintf(stderr, "[cine-watchdog] suspended (prev count=%lu), getting context\n", susp); fflush(stderr);
    CONTEXT ctx{};
    ctx.ContextFlags = CONTEXT_ALL;
    if (!GetThreadContext(hThread, &ctx)) {
        fprintf(stderr, "[cine-watchdog] GetThreadContext failed err=%lu\n", GetLastError());
        fflush(stderr);
        ResumeThread(hThread);
        CloseHandle(hThread);
        return;
    }
    fprintf(stderr,
        "[cine-watchdog] game thread tid=%lu hung at RIP=0x%llX RSP=0x%llX RBP=0x%llX\n",
        tid, (unsigned long long)ctx.Rip, (unsigned long long)ctx.Rsp, (unsigned long long)ctx.Rbp);
    fflush(stderr);

    // Stack walk.
    STACKFRAME64 frame{};
    frame.AddrPC.Offset    = ctx.Rip; frame.AddrPC.Mode    = AddrModeFlat;
    frame.AddrFrame.Offset = ctx.Rbp; frame.AddrFrame.Mode = AddrModeFlat;
    frame.AddrStack.Offset = ctx.Rsp; frame.AddrStack.Mode = AddrModeFlat;
    void* frames[48];
    USHORT count = 0;
    HANDLE hProcess = GetCurrentProcess();
    SymInitialize(hProcess, NULL, TRUE);
    fprintf(stderr, "[cine-watchdog] walking stack\n"); fflush(stderr);
    while (count < 48) {
        if (!StackWalk64(IMAGE_FILE_MACHINE_AMD64, hProcess, hThread, &frame, &ctx,
                         NULL, SymFunctionTableAccess64, SymGetModuleBase64, NULL))
            break;
        if (frame.AddrPC.Offset == 0) break;
        frames[count++] = (void*)(uintptr_t)frame.AddrPC.Offset;
    }
    fprintf(stderr, "[cine-watchdog] walked %u frames, resuming + symbolizing\n", count); fflush(stderr);
    ResumeThread(hThread);
    CloseHandle(hThread);
    print_stack_with_symbols(frames, count);
    fflush(stderr);
}
#else
extern "C" void rs64_cine_iter_tick(unsigned) {}
extern "C" void rs64_cine_dump_if_stuck(void) {}
#endif

// Yield the cinematic CPU thread every N iterations to break the iter-810
// OS-level thread starvation stall. Empirically a kernel I/O call (stderr
// flush) unsticks it; Win32 Sleep alone does not. SwitchToThread yields to
// any ready thread on the same CPU.
extern "C" void rs64_cine_yield(void) {
    static int s_count = 0;
    ++s_count;
    // ~Every 16 iters: yield + flush stderr. Cheap enough to do hot.
    if ((s_count & 0xF) == 0) {
#ifdef _WIN32
        ::SwitchToThread();
#else
        std::this_thread::yield();
#endif
        std::fflush(stderr);
    }
}

// Pace the 32-iteration attribution-display loop inside
// runIdleFramesAndLoadSaveData (each iter renders one attribution frame).
// On real N64, each iter waits for the previous frame to complete via
// waitForPrevFrameDone → waitForPostSwapAck → which we patched to NOBLOCK
// (boot deadlock workaround). Without the wait, all 32 frames flash by in
// <1ms and the attribution screen is never visible.
// Sleep here so attribution displays for ~5 seconds (configurable).
//
// ROGUESQ_ATTRIBUTION_SLEEP_MS=N (default 150ms × 32 iters ≈ 4.8 sec).
// Set to 0 to disable.
extern "C" void rs64_idle_pace(void) {
#ifdef _WIN32
    static int s_sleep_ms = -1;
    if (s_sleep_ms < 0) {
        const char* e = std::getenv("ROGUESQ_ATTRIBUTION_SLEEP_MS");
        s_sleep_ms = (e && *e) ? std::atoi(e) : 150;
        if (s_sleep_ms < 0) s_sleep_ms = 0;
        if (s_sleep_ms > 5000) s_sleep_ms = 5000;
        fprintf(stderr, "[idle-pace] attribution sleep_ms=%d (32 iters ≈ %ds total)\n",
                s_sleep_ms, (s_sleep_ms * 32) / 1000);
        fflush(stderr);
    }
    if (s_sleep_ms == 0) return;
    ::Sleep((DWORD)s_sleep_ms);
#endif
}

// Pace cinematicLoopBody to a target frame rate. Without this, the loop
// runs at >1000 Hz on the host (no pacing from NOBLOCK-patched osRecvMesg
// waits), racing through the cinematic in <2 seconds and skipping past
// the attribution screen, fade, and N64-logo segments before they're
// visible. Default 30 Hz to match N64 native cinematic rate.
// Configure via ROGUESQ_CINE_TARGET_FPS env var: 0 = disabled, positive
// int = target FPS.
extern "C" void rs64_cine_pace(void) {
#ifdef _WIN32
    static int s_target_fps = -1;
    if (s_target_fps < 0) {
        const char* e = std::getenv("ROGUESQ_CINE_TARGET_FPS");
        s_target_fps = (e && *e) ? std::atoi(e) : 30;
        if (s_target_fps < 0) s_target_fps = 0;
        if (s_target_fps > 240) s_target_fps = 240;
        fprintf(stderr, "[cine-pace] init target_fps=%d (env='%s')\n",
                s_target_fps, e ? e : "(null)");
        fflush(stderr);
        // Bump Windows timer resolution to 1ms so Sleep(33) actually sleeps
        // ~33ms instead of the default ~15.6ms quantum.
        timeBeginPeriod(1);
    }
    if (s_target_fps == 0) return;  // disabled
    uint32_t target_interval_ms = 1000u / (uint32_t)s_target_fps;
    static uint64_t s_last_ms = 0;
    static uint32_t s_calls = 0;
    static uint32_t s_sleeps = 0;
    uint64_t now = GetTickCount64();
    if (s_last_ms == 0) {
        s_last_ms = now;
        return;
    }
    uint64_t elapsed = now - s_last_ms;
    if (elapsed < (uint64_t)target_interval_ms) {
        ::Sleep((DWORD)(target_interval_ms - elapsed));
        ++s_sleeps;
    }
    s_last_ms = GetTickCount64();
    ++s_calls;
    if (s_calls <= 5 || (s_calls & 0x3F) == 0) {
        fprintf(stderr, "[cine-pace] call=%u sleeps=%u elapsed=%llums interval=%ums\n",
                s_calls, s_sleeps, (unsigned long long)elapsed, target_interval_ms);
        fflush(stderr);
    }
#endif
}

// Diagnostic helper for [[patches.hook]] entries that need to log to
// stderr — the hook code lives in funcs_*.c which doesn't include stdio.
// Format args: 4 unsigned 32-bit values + a tag string.
extern "C" void rs64_dbg_log4(const char* tag, unsigned a, unsigned b, unsigned c, unsigned d) {
    static int s_log = -1;
    if (s_log < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_HOOKS");
        s_log = (e && *e && *e != '0') ? 1 : 0;
    }
    if (!s_log) return;
    fprintf(stderr, "[hook] %s a=0x%08X b=0x%08X c=0x%08X d=0x%08X\n",
            tag ? tag : "?", a, b, c, d);
    fflush(stderr);
}

// Optional task-submission diagnostic. Gated by ROGUESQ_LOG_TASKSUBMIT.
// When enabled, logs task type + data_ptr/size + first 32 bytes of the DL
// buffer for the first 4 tasks + every 64th. Originally added 2026-05-09
// to investigate why GFX tasks were submitted with data_size=0; finding:
// Factor 5's task protocol uses data_ptr but ignores data_size (the DL
// chains via G_DL jumps to static setup code in .text). data_size=0 is
// normal for Factor 5 cinematic tasks.
extern void print_stack_with_symbols(void** frames, USHORT count);
extern "C" void rs64_set_pending_task_guest_ptr(uint32_t guest_ptr);
extern "C" void rs64_m5_descriptor_start(uint8_t* rdram, uint32_t task_ptr);
extern "C" void rs64_sp_reset_yield_request();
extern "C" void rs64_s7330_aud_submit(uint32_t data_ptr);
extern "C" void rs64_m5_raw_task_boundary(const char* edge,
                                             uint8_t* rdram,
                                             uint32_t raw_task_ptr);

/* s7337: the OSTask range check hard-coded 8 MB. At dd>1 the game is told 12 MB (s6858), so a task struct in
   0x80800000..guest top would be dropped with no SP/DP completion (a freeze). Bound = rs64_ram_top (guest top, widened
   to the host arena end by s7336). ROGUESQ_S7337=0 restores 8 MB. [s7337] line: tasks seen, highest task address,
   and how many the old bound would have rejected. */
extern "C" uint32_t rs64_ram_top;
static bool rs64_s7337_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7337"); return !(e && e[0] == '0'); }(); return on; }
static bool rs64_guest_range_valid_top(uint64_t addr, uint64_t size, uint32_t top) {
    const uint64_t kseg0_base = 0xFFFFFFFF80000000ull;
    const uint64_t kseg0_end = 0xFFFFFFFF00000000ull | top;
    /* s7337: the pre-s7337 form `size <= kseg0_end - addr` wrapped for addr above the end, so it never rejected a
       sign-extended task pointer past 8 MB (selftest old=1 at 0x80900000). Require addr < end first. */
    if (addr >= kseg0_base) return addr < kseg0_end && size <= kseg0_end - addr;

    const uint32_t low = static_cast<uint32_t>(addr);
    return (addr >> 32) == 0 && low >= 0x80000000u && low < top &&
           size <= static_cast<uint64_t>(top - 0x80000000u) - (low - 0x80000000u);
}
static bool rs64_guest_range_valid(uint64_t addr, uint64_t size) {
    static std::atomic<uint32_t> n{0}, hi{0}, widened{0};
    const uint32_t top = rs64_s7337_on() && rs64_ram_top > 0x80800000u ? rs64_ram_top : 0x80800000u;
    const bool ok = rs64_guest_range_valid_top(addr, size, top);
    const bool old_ok = rs64_guest_range_valid_top(addr, size, 0x80800000u);
    const uint32_t lo = static_cast<uint32_t>(addr);
    uint32_t h = hi.load(std::memory_order_relaxed);
    while (ok && lo > h && !hi.compare_exchange_weak(h, lo, std::memory_order_relaxed)) {}
    const uint32_t w = (ok && !old_ok) ? widened.fetch_add(1, std::memory_order_relaxed) + 1 : widened.load(std::memory_order_relaxed);
    const uint32_t k = n.fetch_add(1, std::memory_order_relaxed) + 1;
    if (k == 1)  /* positive control: a synthetic task at 0x80900000 (9 MB) under each bound */
        std::fprintf(stderr, "[s7337] selftest 0x80900000: old=%d new=%d top=0x%08X\n",
                     (int)rs64_guest_range_valid_top(0xFFFFFFFF80900000ull, 64, 0x80800000u),
                     (int)rs64_guest_range_valid_top(0xFFFFFFFF80900000ull, 64, top), top);
    if (k == 1 || (k & (k - 1)) == 0 && k >= 1024 || (ok && !old_ok && w <= 4))
        std::fprintf(stderr, "[s7337] task range: n=%u hi=0x%08X top=0x%08X widened=%u%s\n", k, hi.load(std::memory_order_relaxed),
                     top, w, rs64_s7337_on() ? "" : " (S7337=0: 8 MB bound)");
    return ok;
}

extern "C" int rs64_s7518_cache_on(void);  // s7518 class FO (librecomp ultra_translation.cpp)
extern "C" void osSpTaskStartGo_recomp(uint8_t* rdram, recomp_context* ctx) {
    rs64_m5_raw_task_boundary("start", rdram, static_cast<uint32_t>(ctx->r4));
    if (!rs64_guest_range_valid(static_cast<uint64_t>(ctx->r4), sizeof(OSTask))) {
        // s7197: this return posts no SP/DP completion. Never seen, but make it visible if it ever explains a freeze.
        static int shown = 0;
        if (shown++ < 8) fprintf(stderr, "[s7197-sp-drop] invalid OSTask 0x%08X ra=0x%08X: no completion posted\n",
                                 (uint32_t)ctx->r4, (uint32_t)ctx->r31);
        ctx->r2 = 0;
        return;
    }
    rs64_sp_reset_yield_request();
    { /* s7518 class FO: task ranges the RSP reads, in [cache] call order */
      if (rs64_s7518_cache_on()) { OSTask* t18 = TO_PTR(OSTask, ctx->r4);
        std::fprintf(stderr, "[cache] op=sp%u a=%08X n=%X ra=%08X uc=%08X ucn=%X ud=%08X udn=%X out=%08X stk=%08X yld=%08X\n",
            (uint32_t)t18->t.type, (uint32_t)t18->t.data_ptr, (uint32_t)t18->t.data_size, (uint32_t)ctx->r31, (uint32_t)t18->t.ucode,
            (uint32_t)t18->t.ucode_size, (uint32_t)t18->t.ucode_data, (uint32_t)t18->t.ucode_data_size, (uint32_t)t18->t.output_buff,
            (uint32_t)t18->t.dram_stack, (uint32_t)t18->t.yield_data_ptr); } }
    { if (rs64_s7324_on) { OSTask* t30 = TO_PTR(OSTask, ctx->r4); if (t30->t.type == 2u) rs64_s7330_aud_submit((uint32_t)t30->t.data_ptr); } }  /* s7330 */
    { if (rs64_s7331_on) { OSTask* t32 = TO_PTR(OSTask, ctx->r4); const uint32_t f[9] = { (uint32_t)t32->t.type, (uint32_t)t32->t.ucode, (uint32_t)t32->t.dram_stack,
        (uint32_t)t32->t.output_buff, (uint32_t)t32->t.output_buff_size, (uint32_t)t32->t.data_ptr, (uint32_t)t32->t.data_size, (uint32_t)t32->t.yield_data_ptr,
        (uint32_t)t32->t.yield_data_size }; rs64_s7331_task(f); } }  /* s7332 */
    rs64_m5_descriptor_start(rdram, (uint32_t)ctx->r4);
    rs64_set_pending_task_guest_ptr((uint32_t)ctx->r4);
    static int s_log = -1;
    if (s_log < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_TASKSUBMIT");
        s_log = (e && *e && *e != '0') ? 1 : 0;
    }
    // Separate gate: print host-side stack on first GFX submit so we can
    // identify which game thread / function chain is driving submission.
    // One-shot per task type — once we know who submits GFX vs audio, the
    // log is noise.
    {
        static int s_log_stk = -1;
        if (s_log_stk < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_TASKSUBMIT_STACK");
            s_log_stk = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_log_stk) {
            OSTask* task = TO_PTR(OSTask, ctx->r4);
            static bool s_logged_gfx = false;
            static bool s_logged_audio = false;
            const bool is_gfx = (task->t.type == 1u);
            const bool is_audio = (task->t.type == 2u);
            if ((is_gfx && !s_logged_gfx) || (is_audio && !s_logged_audio)) {
                if (is_gfx) s_logged_gfx = true;
                if (is_audio) s_logged_audio = true;
                fprintf(stderr,
                    "[task-submit-stack] tid=%lu type=0x%X data_ptr=0x%08X ucode=0x%08X\n",
                    GetCurrentThreadId(),
                    (unsigned)task->t.type,
                    (unsigned)task->t.data_ptr,
                    (unsigned)task->t.ucode);
                void* frames[24];
                USHORT count = RtlCaptureStackBackTrace(0, 24, frames, nullptr);
                print_stack_with_symbols(frames, count);
                fflush(stderr);
            }
        }
    }
    if (s_log) {
        OSTask* task = TO_PTR(OSTask, ctx->r4);
        static int n = 0;
        ++n;
        // Log first 4, every 64th, AND every GFX task regardless of count
        // (audio tasks fire at high rate and would mask GFX in normal sampling).
        const bool is_gfx = (task->t.type == 1u);
        if (n <= 4 || (n & 63) == 0 || is_gfx) {
            fprintf(stderr,
                "[task-submit #%d] type=0x%X flags=0x%X data_ptr=0x%08X data_size=%u ucode=0x%08X ucode_size=%u\n",
                n,
                (unsigned)task->t.type,
                (unsigned)task->t.flags,
                (unsigned)task->t.data_ptr,
                (unsigned)task->t.data_size,
                (unsigned)task->t.ucode,
                (unsigned)task->t.ucode_size);
            uint32_t dp = (uint32_t)task->t.data_ptr;
            if (task->t.type == M_GFXTASK && dp >= 0x80000000u && dp < rs64_ram_top) {
                uint32_t off = dp - 0x80000000u;
                fprintf(stderr, "  data_ptr[0..32]:");
                for (int i = 0; i < 32; ++i) {
                    fprintf(stderr, " %02X", (unsigned)rdram[(off + i) ^ 3]);
                }
                fprintf(stderr, "\n");
            }
            fflush(stderr);
        }
    }
    {
        // s4508: raw DL bytes at data_ptr, first 3 GFX tasks per VI width.
        static const char* dir = std::getenv("RS64_GFX_DL_DUMP_DIR");
        OSTask* task = TO_PTR(OSTask, ctx->r4);
        uint32_t dp = (uint32_t)task->t.data_ptr;
        if (dir && *dir && task->t.type == M_GFXTASK && dp >= 0x80000000u &&
            dp + 0x4000u <= rs64_ram_top) {
            static uint32_t seen_w[8];
            static int seen_n[8];
            static int nw = 0;
            const uint32_t width = ultramodern::renderer::get_vi_regs()->VI_WIDTH_REG;
            int idx = -1;
            for (int k = 0; k < nw; k++) if (seen_w[k] == width) idx = k;
            if (idx < 0 && nw < 8) { idx = nw++; seen_w[idx] = width; }
            if (idx >= 0 && seen_n[idx] < 3) {
                char path[512];
                std::snprintf(path, sizeof path, "%s/port_w%u_%d.bin", dir, width, seen_n[idx]++);
                if (FILE* f = std::fopen(path, "wb")) {
                    uint32_t off = dp - 0x80000000u;
                    for (uint32_t i = 0; i < 0x4000u; ++i) std::fputc(rdram[(off + i) ^ 3], f);
                    std::fclose(f);
                    // s4510: child DLs (op 06 targets in first 0x100 B of root)
                    int c = 0;
                    for (uint32_t o = 0; o < 0x100u; o += 8) {
                        uint32_t w0 = 0, w1 = 0;
                        for (int j = 0; j < 4; ++j) { w0 = (w0 << 8) | rdram[(off + o + j) ^ 3]; w1 = (w1 << 8) | rdram[(off + o + 4 + j) ^ 3]; }
                        if ((w0 >> 24) == 6 && (w1 >> 24) == 0x80 && (w1 & 0x1FFFFFFFu) + 0x1000u <= (rs64_ram_top - 0x80000000u)) {
                            uint32_t co = w1 & 0x1FFFFFFFu;
                            char cp[512];
                            std::snprintf(cp, sizeof cp, "%s/port_w%u_%d_c%02d.bin", dir, width, seen_n[idx] - 1, c++);
                            if (FILE* cf = std::fopen(cp, "wb")) {
                                for (uint32_t i = 0; i < 0x1000u; ++i) std::fputc(rdram[(co + i) ^ 3], cf);
                                std::fclose(cf);
                            }
                            {   // s4511: data blobs (ops 01/02/04/fd) referenced by this child
                                auto rd32 = [&](uint32_t a) { uint32_t v = 0; for (int j = 0; j < 4; ++j) v = (v << 8) | rdram[(a + j) ^ 3]; return v; };
                                uint32_t q = 0, dn = 0;
                                while (q + 8u <= 0x1000u) {
                                    uint32_t v0 = rd32(co + q), v1 = rd32(co + q + 4);
                                    uint32_t op = v0 >> 24, db = v1 & 0x1FFFFFFFu;
                                    q += 8;
                                    if ((op == 1 || op == 2 || op == 4 || op == 0xFD) && (v1 >> 24) == 0x80 && db + 0x400u <= (rs64_ram_top - 0x80000000u)) {
                                        char dp2[512];
                                        std::snprintf(dp2, sizeof dp2, "%s/port_w%u_%d_c%02d_d%02u_op%02x.bin", dir, width, seen_n[idx] - 1, c - 1, dn++, op);
                                        if (FILE* df = std::fopen(dp2, "wb")) {
                                            for (uint32_t z = 0; z < 0x400u; ++z) std::fputc(rdram[(db + z) ^ 3], df);
                                            std::fclose(df);
                                        }
                                    }
                                    if (op == 3) q += 16; else if (op == 5) q += 32; else if (op == 0xBD) q += 16; else if (op == 0xBE || op == 0xB3) q += 8;
                                    else if (op == 0xB4 || op == 0xBF) { if (v0 & 2) q += 16; q += 8; }
                                    if (op == 0xB8 || op == 7 || op == 0xB5) break;
                                }
                            }
                        }
                    }
                }
                std::fprintf(stderr, "[dl-dump] %s data_ptr=0x%08X\n", path, dp);
            }
        }
    }
    ultramodern::submit_rsp_task(rdram, ctx->r4);
}

// Optional sender-trace for osSendMesg. Captures host stack on the first
// send to each unique queue address — quickly maps which game functions
// drive which queues. Gated by ROGUESQ_LOG_SENDMESG_STACK=1.
//
// We override the librecomp default (link warning re: duplicate symbol is
// expected; lld-link picks our version). The behavior is identical otherwise.
extern "C" int32_t osSendMesg(uint8_t* rdram, int32_t mq_, OSMesg mesg, s32 flag);
extern "C" int32_t osRecvMesg(uint8_t* rdram, int32_t mq_, PTR(OSMesg) mesg, s32 flag);
extern "C" uint32_t rs64_phase_ord(void);

static void log_m5_frame_sync_edge(uint8_t* rdram, const char* edge,
                                   uint32_t mq_addr, uint32_t msg,
                                   int32_t flag) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FRAME_SYNC");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (!enabled || (mq_addr != 0x80138D10u && mq_addr != 0x80128CF0u)) return;
    static std::atomic<uint32_t> rows{0};
    const uint32_t phase = rs64_phase_ord();
    const uint32_t row = rows.fetch_add(1, std::memory_order_relaxed);
    if (phase >= 4u && row >= 256u) return;
    std::fprintf(stderr,
        "[m5-frame-sync] row=%u phase=%u edge=%s guest_pc=0x%08X mq=0x%08X "
        "msg=0x%08X flag=%d valid=%d first=%d count=%d\n",
        row, phase, edge, (unsigned)g_rs64_last_guest_pc, mq_addr, msg,
        (int)flag, (int)TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq_addr)->validCount,
        (int)TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq_addr)->first,
        (int)TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq_addr)->msgCount);
    std::fflush(stderr);
    if (row == 0) {
        std::fprintf(stderr, "[m5-frame-sync-positive] wrapper edge is live\n");
        std::fflush(stderr);
    }
}

static void log_a1_queue_boundary(uint32_t mq_addr, PTR(OSMesg) msg, s32 flag,
                                  int32_t result, const OSMesgQueue& before,
                                  const OSMesgQueue& after) {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_A1_QUEUE");
        return e && *e && *e != '0';
    }();
    if (!enabled || mq_addr != 0x8010FEE0u) return;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase >= 4u && rows >= 256u) return;
    ++rows;
    std::fprintf(stderr,
        "[a1-queue] row=%u phase=%u guest_pc=0x%08X mq=0x%08X msg=0x%08X flag=%d "
        "pre_valid=%d pre_first=%d pre_count=%d pre_msg=0x%08X result=%d "
        "post_valid=%d post_first=%d post_count=%d post_msg=0x%08X\n",
        rows, phase, (unsigned)g_rs64_last_guest_pc, mq_addr, (uint32_t)msg, (int)flag,
        before.validCount, before.first, before.msgCount, (uint32_t)before.msg,
        (int)result, after.validCount, after.first, after.msgCount, (uint32_t)after.msg);
    std::fflush(stderr);
}

static bool submit_boundary_log_enabled() {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* specific = std::getenv("ROGUESQ_LOG_SUBMIT_BOUNDARY");
        return (all && *all && *all != '0') || (specific && *specific && *specific != '0');
    }();
    return enabled;
}

static void log_submit_boundary(uint8_t* rdram, const char* kind, uint32_t mq, uint32_t flag) {
    if (!submit_boundary_log_enabled()) return;
    static std::atomic<uint32_t> phase_seen{0xFFFFFFFFu};
    static std::atomic<uint32_t> phase_rows{0};
    const uint32_t phase = rs64_phase_ord();
    uint32_t prior = phase_seen.load(std::memory_order_relaxed);
    if (prior != phase && phase_seen.compare_exchange_strong(prior, phase, std::memory_order_relaxed)) {
        phase_rows.store(0, std::memory_order_relaxed);
    }
    const uint32_t row = phase_rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256) return;
    const uint32_t gate0 = rdram[0x11A89Fu ^ 3u];
    const uint32_t gate1 = rdram[0x11A8A0u ^ 3u];
    const uint32_t obj = mq == 0x8011A408u ? 0x11A408u : 0u;
    std::fprintf(stderr,
        "[submit-boundary] phase=%u row=%u kind=%s mq=0x%08X flag=%u guest_pc=0x%08X gate89f=%u gate8a0=%u obj_valid=%u obj_msg=0x%08X obj_count=%u\n",
        phase, row, kind, mq, flag, (unsigned)g_rs64_last_guest_pc,
        gate0, gate1, obj ? 1u : 0u,
        obj ? ((uint32_t)rdram[(obj + 0x0Cu) ^ 3u] << 24 |
               (uint32_t)rdram[(obj + 0x0Du) ^ 3u] << 16 |
               (uint32_t)rdram[(obj + 0x0Eu) ^ 3u] << 8 |
               (uint32_t)rdram[(obj + 0x0Fu) ^ 3u]) : 0u,
        obj ? ((uint32_t)rdram[(obj + 0x08u) ^ 3u] << 24 |
               (uint32_t)rdram[(obj + 0x09u) ^ 3u] << 16 |
               (uint32_t)rdram[(obj + 0x0Au) ^ 3u] << 8 |
               (uint32_t)rdram[(obj + 0x0Bu) ^ 3u]) : 0u);
    std::fflush(stderr);
}

static void log_m5_dp_event_boundary(const char* edge, uint32_t mq_addr,
                                     uint32_t msg, int32_t flag, int32_t result,
                                     const OSMesgQueue& before,
                                     const OSMesgQueue& after) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_DP_EVENT");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (!enabled || mq_addr != 0x8011A408u) return;
    static std::atomic<uint32_t> phase_seen{0xFFFFFFFFu};
    static std::atomic<uint32_t> phase_rows{0};
    const uint32_t phase = rs64_phase_ord();
    uint32_t prior = phase_seen.load(std::memory_order_relaxed);
    if (prior != phase && phase_seen.compare_exchange_strong(
            prior, phase, std::memory_order_relaxed)) {
        phase_rows.store(0, std::memory_order_relaxed);
    }
    const uint32_t row = phase_rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256u) return;
    std::fprintf(stderr,
        "[m5-dp-event] phase=%u row=%u edge=%s guest_pc=0x%08X mq=0x%08X "
        "msg=0x%08X flag=%d result=%d pre_valid=%d pre_first=%d pre_count=%d "
        "pre_msg=0x%08X post_valid=%d post_first=%d post_count=%d post_msg=0x%08X\n",
        phase, row, edge, (unsigned)g_rs64_last_guest_pc, mq_addr, msg, (int)flag,
        (int)result, before.validCount, before.first, before.msgCount,
        (uint32_t)before.msg, after.validCount, after.first, after.msgCount,
        (uint32_t)after.msg);
    std::fflush(stderr);
    if (row == 0) {
        std::fprintf(stderr, "[m5-dp-event-positive] DP queue wrapper is live\n");
        std::fflush(stderr);
    }
}

// VI-640 blocked-thread graph (temp, env-gated). Stable host tid, not guest pc.
static bool recv_trace_enabled() {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_RECV_TRACE");
        return e && *e && *e != '0';
    }();
    return enabled;
}

static bool sendmesg_stack_enabled() {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_SENDMESG_STACK");
        return e && *e && *e != '0';
    }();
    return enabled;
}

struct RecvMqStat {
    uint32_t mq = 0;
    uint64_t last_tid = 0;
    uint32_t guest_tid = 0;
    uint32_t rplus = 0;
    uint32_t rminus = 0;
    uint32_t sends = 0;
    uint32_t logged_rplus = 0;
    uint32_t logged_rminus = 0;
    uint32_t stack_logged = 0;
    uint32_t send_stack_logged = 0;
};

static constexpr uint32_t kRecvMqCap = 384;
static RecvMqStat g_recv_stats[kRecvMqCap];
static std::atomic<uint32_t> g_recv_n{0};
static std::recursive_mutex g_recv_mu;

static uint32_t rs64_guest_tid(uint8_t* rdram) {
    PTR(OSThread) t = ultramodern::this_thread();
    if (!t) return 0;
    return (uint32_t)TO_PTR(OSThread, t)->id;
}

static RecvMqStat* recv_stat_for(uint32_t mq) {
    std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
    const uint32_t n = g_recv_n.load(std::memory_order_relaxed);
    for (uint32_t i = 0; i < n && i < kRecvMqCap; i++) {
        if (g_recv_stats[i].mq == mq) return &g_recv_stats[i];
    }
    if (n >= kRecvMqCap) return nullptr;
    g_recv_stats[n].mq = mq;
    g_recv_n.store(n + 1, std::memory_order_relaxed);
    return &g_recv_stats[n];
}

static void recv_trace_dump() {
    RecvMqStat copy[kRecvMqCap];
    uint32_t n = 0;
    {
        std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
        n = g_recv_n.load(std::memory_order_relaxed);
        if (n > kRecvMqCap) n = kRecvMqCap;
        for (uint32_t i = 0; i < n; i++) copy[i] = g_recv_stats[i];
    }
    const uint64_t ms = GetTickCount64();
    uint32_t blocked = 0;
    for (uint32_t i = 0; i < n; i++) {
        const RecvMqStat& s = copy[i];
        const int32_t net = (int32_t)s.rplus - (int32_t)s.rminus;
        if (net > 0) blocked++;
        std::fprintf(stderr,
            "[recvsum] t_ms=%llu mq=0x%08X tid=%lu gid=%u R+=%u R-=%u net=%d S+=%u\n",
            (unsigned long long)ms, s.mq, (unsigned long)s.last_tid, s.guest_tid,
            s.rplus, s.rminus, (int)net, s.sends);
    }
    std::fprintf(stderr, "[recvsum] t_ms=%llu queues=%u blocked=%u\n",
        (unsigned long long)ms, n, blocked);
    std::fflush(stderr);
}

static void recv_trace_start_dumper() {
    static std::once_flag once;
    std::call_once(once, [] {
        std::fprintf(stderr, "[recvtrace] enabled=1 dumper=10s\n");
        std::fflush(stderr);
        std::thread([] {
            for (;;) {
                std::this_thread::sleep_for(std::chrono::seconds(10));
                recv_trace_dump();
            }
        }).detach();
    });
}

static void recv_trace_enter(uint8_t* rdram, uint32_t mq, int32_t flag, uint64_t tid) {
    if (!recv_trace_enabled() || flag != OS_MESG_BLOCK) return;
    recv_trace_start_dumper();
    RecvMqStat* s = recv_stat_for(mq);
    if (!s) return;
    const uint32_t gid = rs64_guest_tid(rdram);
    bool want_line = false;
    bool want_stack = false;
    {
        std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
        s->last_tid = tid;
        s->guest_tid = gid;
        s->rplus++;
        if (s->logged_rplus < 8) {
            s->logged_rplus++;
            want_line = true;
        }
        if (s->stack_logged == 0) {
            s->stack_logged = 1;
            want_stack = true;
        }
    }
    if (want_line) {
        std::fprintf(stderr, "[recvtrace] R+ mq=0x%08X flag=%d tid=%lu gid=%u\n",
            mq, (int)flag, (unsigned long)tid, gid);
        std::fflush(stderr);
    }
    if (mq == 0x8011A818u) {
        auto be_u8 = [&](uint32_t kseg) -> unsigned {
            const uint32_t phys = kseg - 0x80000000u;
            return (unsigned)rdram[phys ^ 3u];
        };
        std::fprintf(stderr,
            "[framesync-gate] mq=0x8011A818 89C=%u 89D=%u 89E=%u 89F=%u 8A0=%u 28D44=%u\n",
            be_u8(0x8011A89Cu), be_u8(0x8011A89Du), be_u8(0x8011A89Eu),
            be_u8(0x8011A89Fu), be_u8(0x8011A8A0u), be_u8(0x80128D44u));
        std::fflush(stderr);
    }
    if (want_stack) {
        std::fprintf(stderr, "[recvbt] mq=0x%08X tid=%lu gid=%u\n",
            mq, (unsigned long)tid, gid);
        void* frames[24];
        USHORT count = RtlCaptureStackBackTrace(0, 24, frames, nullptr);
        print_stack_with_symbols(frames, count);
        std::fflush(stderr);
    }
}

static void recv_trace_exit(uint32_t mq, int32_t flag, uint64_t tid, int32_t result) {
    if (!recv_trace_enabled() || flag != OS_MESG_BLOCK) return;
    RecvMqStat* s = recv_stat_for(mq);
    if (!s) return;
    bool want_line = false;
    {
        std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
        s->rminus++;
        if (s->logged_rminus < 8) {
            s->logged_rminus++;
            want_line = true;
        }
    }
    if (want_line) {
        std::fprintf(stderr, "[recvtrace] R- mq=0x%08X tid=%lu r=%d\n",
            mq, (unsigned long)tid, (int)result);
        std::fflush(stderr);
    }
}

static void recv_trace_scheduler_type(uint8_t* rdram, uint32_t msg_addr,
                                      int32_t result) {
    if (!recv_trace_enabled() || result != 0 || msg_addr < 0x80000000u ||
        msg_addr >= rs64_ram_top) return;
    static std::atomic<uint32_t> rows{0};
    const uint32_t row = rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256u) return;
    const uint32_t msg_phys = msg_addr - 0x80000000u;
    const unsigned type = (unsigned)rdram[msg_phys ^ 3u];
    auto be_u8 = [&](uint32_t kseg) -> unsigned {
        const uint32_t p = kseg - 0x80000000u;
        return (unsigned)rdram[p ^ 3u];
    };
    std::fprintf(stderr,
        "[recv-scheduler-type] phase=%u row=%u msg=0x%08X type=0x%02X "
        "89F=%u 28D44=%u\n",
        rs64_phase_ord(), row, msg_addr, type, be_u8(0x8011A89Fu),
        be_u8(0x80128D44u));
    std::fflush(stderr);
}

extern "C" void rs64_m5_scheduler_recv_identity(uint8_t* rdram, uint32_t pc,
                                                   uint32_t caller,
                                                   uint32_t output_slot,
                                                   uint32_t result) {
    if (!recv_trace_enabled() || result != 0 || rdram == nullptr) return;
    if (output_slot < 0x80000000u || output_slot >= rs64_ram_top) return;
    const uint32_t slot_phys = output_slot - 0x80000000u;
    const uint32_t msg_addr =
        (static_cast<uint32_t>(rdram[slot_phys ^ 3u]) << 24) |
        (static_cast<uint32_t>(rdram[(slot_phys + 1u) ^ 3u]) << 16) |
        (static_cast<uint32_t>(rdram[(slot_phys + 2u) ^ 3u]) << 8) |
        static_cast<uint32_t>(rdram[(slot_phys + 3u) ^ 3u]);
    unsigned type = 0xFFu;
    if (msg_addr >= 0x80000000u && msg_addr < rs64_ram_top) {
        type = rdram[(msg_addr - 0x80000000u) ^ 3u];
    }
    static std::atomic<uint32_t> bucket{0xFFFFFFFFu};
    static std::atomic<uint32_t> rows{0};
    const uint32_t phase = rs64_phase_ord();
    if (bucket.load(std::memory_order_relaxed) != phase &&
        bucket.exchange(phase, std::memory_order_relaxed) != phase) {
        rows.store(0, std::memory_order_relaxed);
    }
    const uint32_t row = rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256u) return;
    auto be_u8 = [rdram](uint32_t guest) -> unsigned {
        if (guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    std::fprintf(stderr,
        "[recv-scheduler-identity] phase=%u row=%u pc=0x%08X caller=0x%08X "
        "slot=0x%08X msg=0x%08X type=0x%02X 89F=%u 28D44=%u\n",
        phase, row, pc, caller, output_slot, msg_addr, type,
        be_u8(0x8011A89Fu), be_u8(0x80128D44u));
    std::fflush(stderr);
}

static void sendtgt_note(uint32_t mq, uint64_t tid, bool want_stack) {
    if (!recv_trace_enabled() && !want_stack) return;
    if (recv_trace_enabled()) recv_trace_start_dumper();
    RecvMqStat* s = recv_stat_for(mq);
    if (!s) return;
    bool first = false;
    bool do_stack = false;
    {
        std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
        s->sends++;
        if (s->sends == 1) first = true;
        if (want_stack && s->send_stack_logged == 0) {
            s->send_stack_logged = 1;
            do_stack = true;
        }
    }
    if (first && recv_trace_enabled()) {
        std::fprintf(stderr, "[sendtgt] mq=0x%08X tid=%lu\n", mq, (unsigned long)tid);
        std::fflush(stderr);
    }
    if (do_stack) {
        std::fprintf(stderr, "[sendmesg] tid=%lu mq=0x%08X\n", (unsigned long)tid, mq);
        void* frames[24];
        USHORT count = RtlCaptureStackBackTrace(0, 24, frames, nullptr);
        print_stack_with_symbols(frames, count);
        std::fflush(stderr);
    }
}

struct Rs64M5FrequencyPending {
    uint32_t queue;
    uint32_t msg;
    uint32_t callsite;
    uint32_t state;
    bool valid;
};

static thread_local Rs64M5FrequencyPending g_rs64_m5_frequency_pending{0, 0, 0, 0, false};

struct Rs64M5PointerCandidate {
    uint32_t pc;
    uint32_t addr;
    uint32_t value;
    uint32_t phase;
};

static thread_local Rs64M5PointerCandidate g_rs64_m5_pointer_latest[4]{};

struct Rs64M5ZcfreeEdge {
    uint32_t s1;
    uint32_t a0;
    uint32_t ra;
    uint32_t ordinal;
    bool valid;
};

static thread_local Rs64M5ZcfreeEdge g_rs64_m5_zcfree_edge{0, 0, 0, 0, false};

extern "C" void rs64_m5_state_pointer_entry(uint8_t* rdram,
                                               recomp_context* ctx) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool title_phase = width == 1024u &&
        (origin == 0x00790400u || origin == 0x00790800u);
    const bool hangar_phase = width == 512u &&
        (origin == 0x006AB400u || origin == 0x006AB800u);
    if (!title_phase && !hangar_phase) return;
    const uint32_t s1 = U32(ctx->r17);
    if (!((s1 >= 0x80194000u && s1 < 0x80196000u) ||
          (s1 >= 0x801B0000u && s1 < 0x801C0000u))) return;
    extern void rs64_m5_state_pointer_consumer(uint32_t s1);
    rs64_m5_state_pointer_consumer(s1);
    static uint32_t rows = 0;
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-state-pointer-entry] ordinal=%u phase=%u width=%u origin=0x%06X "
        "s1=0x%08X state_word=0x%08X a0=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, s1,
        U32(MEM_W(0, ctx->r17)), U32(ctx->r4), U32(ctx->r31));
    std::fflush(stderr);
}

static thread_local uint32_t g_rs64_m5_state_call_pc = 0;
static thread_local uint32_t g_rs64_m5_state_call_s0 = 0;

extern "C" void rs64_m5_state_pointer_callsite(recomp_context* ctx,
                                                 uint32_t call_pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 1024u) return;
    g_rs64_m5_state_call_pc = call_pc;
    g_rs64_m5_state_call_s0 = U32(ctx->r16);
    std::fprintf(stderr,
        "[m5-state-pointer-callsite] ordinal=%u phase=%u width=%u origin=0x%06X "
        "call_pc=0x%08X s0=0x%08X s1=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, call_pc, U32(ctx->r16),
        U32(ctx->r17), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_zcfree_edge(recomp_context* ctx) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    g_rs64_m5_zcfree_edge = {U32(ctx->r17), U32(ctx->r4), U32(ctx->r31), rows++, true};
    if (g_rs64_m5_zcfree_edge.ordinal >= 1024u) return;
    std::fprintf(stderr,
        "[m5-zcfree-edge] ordinal=%u phase=%u width=%u origin=0x%06X "
        "s1=0x%08X a0=0x%08X ra=0x%08X\n",
        g_rs64_m5_zcfree_edge.ordinal, rs64_phase_ord(), width, origin,
        g_rs64_m5_zcfree_edge.s1, g_rs64_m5_zcfree_edge.a0,
        g_rs64_m5_zcfree_edge.ra);
    std::fflush(stderr);
    if (g_rs64_m5_zcfree_edge.ordinal == 0) {
        std::fprintf(stderr, "[m5-zcfree-edge-positive] sole caller edge is live\n");
        std::fflush(stderr);
    }
}

struct Rs64M5DownstreamStore {
    uint32_t pc;
    uint32_t addr;
    uint32_t value;
    uint32_t edge_ordinal;
    uint32_t edge_s1;
    uint32_t ordinal;
};

static thread_local Rs64M5DownstreamStore g_rs64_m5_downstream_latest{0, 0, 0, 0, 0, 0};

extern "C" void rs64_m5_downstream_store(uint8_t* rdram, recomp_context* ctx,
                                           char width, uint32_t pc,
                                           uint32_t addr, uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_DOWNSTREAM");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    static const bool late_only = [] {
        const char* e = std::getenv("ROGUESQ_M5_DOWNSTREAM_LATE_ONLY");
        return e && e[0] && e[0] != '0';
    }();
    if (late_only && pc < 0x80001DFCu) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 2048u) return;
    g_rs64_m5_downstream_latest = {
        pc, addr, value, g_rs64_m5_zcfree_edge.ordinal,
        g_rs64_m5_zcfree_edge.s1, rows
    };
    if (rows == 0) {
        std::fprintf(stderr, "[m5-downstream-store-positive] downstream store census is live\n");
        std::fflush(stderr);
    }
    std::fprintf(stderr,
        "[m5-downstream-store] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "pc=0x%08X width=%c addr=0x%08X value=0x%08X edge_ord=%u edge_s1=0x%08X "
        "caller_s1=0x%08X caller_ra=0x%08X\n",
        rows++, rs64_phase_ord(), origin, pc, width, U32(addr), U32(value),
        g_rs64_m5_zcfree_edge.ordinal, g_rs64_m5_zcfree_edge.s1,
        U32(ctx->r17), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_producer_input(uint8_t* rdram,
                                         recomp_context* ctx,
                                         uint32_t producer_pc,
                                         uint32_t call_pc,
                                         uint32_t target_pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 1024u) return;
    const uint32_t source_ptr = U32(ctx->r4);
    const uint32_t source_word =
        (source_ptr >= 0x80000000u && source_ptr <= 0x807FFFFCu)
            ? rs64_rdram_u32(rdram, source_ptr - 0x80000000u)
            : 0xFFFFFFFFu;
    std::fprintf(stderr,
        "[m5-producer-input] ordinal=%u phase=%u width=%u origin=0x%06X "
        "producer_pc=0x%08X source_ptr=0x%08X source_word=0x%08X "
        "loaded_s0=0x%08X call_pc=0x%08X target_pc=0x%08X s1=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, producer_pc, source_ptr,
        source_word, U32(ctx->r16), call_pc, target_pc, U32(ctx->r17),
        U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_output_state_fields(uint8_t* rdram,
                                                recomp_context* ctx,
                                                uint32_t pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 2048u) return;
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return rs64_rdram_u32(rdram, p);
    };
    auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFFFFFFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    std::fprintf(stderr,
        "[m5-output-state-fields] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X s0=0x%08X s1=0x%08X source_word=0x%08X "
        "branch_selector=0x%08X source_byte=0x%02X branch_state=0x%04X "
        "output_v0=0x%08X output_v1=0x%08X state_word=0x%08X "
        "a0=0x%08X a1=0x%08X ra=0x%08X pre_call_pc=0x%08X "
        "pre_call_s0=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, s0, s1,
        word(s0 + 0x60u), U32(ctx->r2), byte(s0 + 0x22u),
        word(s1 + 0x22u) & 0xFFFFu, U32(ctx->r2), U32(ctx->r3),
        word(s1), U32(ctx->r4), U32(ctx->r5), U32(ctx->r31),
        g_rs64_m5_state_call_pc, g_rs64_m5_state_call_s0);
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-output-state-fields-positive] four-PC schema witness is live\n");
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_table_selection(uint8_t* rdram,
                                           recomp_context* ctx,
                                           uint32_t pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TABLE_SELECTION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 2048u) return;
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return rs64_rdram_u32(rdram, p);
    };
    const uint32_t entry = U32(ctx->r3);
    const uint32_t selected = U32(ctx->r16);
    std::fprintf(stderr,
        "[m5-table-selection] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X entry=0x%08X index=0x%08X table_base=0x%08X "
        "selected=0x%08X selected_word=0x%08X a0=0x%08X s1=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, entry, U32(ctx->r6),
        word(U32(ctx->r17)), selected, word(selected), U32(ctx->r4),
        U32(ctx->r17), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_state_pointer_checkpoint(uint8_t* rdram,
                                                    recomp_context* ctx,
                                                    const char* edge) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool title_phase = width == 1024u &&
        (origin == 0x00790400u || origin == 0x00790800u);
    const bool hangar_phase = width == 512u &&
        (origin == 0x006AB400u || origin == 0x006AB800u);
    if (!title_phase && !hangar_phase) return;
    static uint32_t rows = 0;
    if (rows >= 1024u) return;
    const uint32_t s1 = U32(ctx->r17);
    if (!((s1 >= 0x80194000u && s1 < 0x80196000u) ||
          (s1 >= 0x801B0000u && s1 < 0x801C0000u))) return;
    std::fprintf(stderr,
        "[m5-state-pointer-checkpoint] edge=%s ordinal=%u phase=%u width=%u "
        "origin=0x%06X s1=0x%08X state_word=0x%08X state=0x%08X "
        "output_v0=0x%08X output_v1=0x%08X a0=0x%08X a1=0x%08X ra=0x%08X\n",
        edge, rows++, rs64_phase_ord(), width, origin, s1,
        U32(MEM_W(0, ctx->r17)), U32(ctx->r16), U32(ctx->r2), U32(ctx->r3),
        U32(ctx->r4), U32(ctx->r5), U32(ctx->r31));
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-state-pointer-checkpoint-positive] ordered witness is live\n");
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_pointer_span_store(char width, uint32_t pc,
                                             uint32_t addr, uint32_t value) {
    static const bool source_span_enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SOURCE_SPAN");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    const uint32_t source_phys = addr & 0x1FFFFFFFu;
    const uint32_t source_size = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    const uint32_t source_origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool source_title = rs64_vi_committed_width() == 1024u &&
        (source_origin == 0x00790400u || source_origin == 0x00790800u);
    const bool source_hit = source_phys < 0x0018DD50u &&
        source_phys + source_size > 0x0018DD20u;
    const bool source_hit2 = source_phys < 0x0018FB90u &&
        source_phys + source_size > 0x0018FB60u;
    if (source_span_enabled && source_title && (source_hit || source_hit2)) {
        static uint32_t source_rows = 0;
        static bool source_control = false;
        if (!source_control) {
            std::fprintf(stderr,
                "[m5-source-span-control] phase=%u width=1024 origin=0x%06X "
                "spans=0x18DD20:0x18DD50,0x18FB60:0x18FB90\n",
                rs64_phase_ord(), source_origin);
            std::fflush(stderr);
            source_control = true;
        }
        if (source_rows < 4096u) {
            std::fprintf(stderr,
                "[m5-source-span] ordinal=%u phase=%u width=1024 origin=0x%06X "
                "pc=0x%08X width=%c phys=0x%06X span=%s offset=0x%X value=0x%08X\n",
                source_rows++, rs64_phase_ord(), source_origin, pc, width,
                source_phys, source_hit ? "dd" : "fb",
                source_phys - (source_hit ? 0x0018DD20u : 0x0018FB60u), value);
            std::fflush(stderr);
        }
    }
    static const bool task_writer_enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TASK_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    const uint32_t store_phys = addr & 0x1FFFFFFFu;
    const uint32_t store_span = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    const uint32_t title_origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool title_phase = rs64_vi_committed_width() == 1024u &&
        (title_origin == 0x00790400u || title_origin == 0x00790800u);
    if (task_writer_enabled && title_phase &&
        store_phys < 0x001494B0u && store_phys + store_span > 0x00149470u) {
        static uint32_t rows = 0;
        static bool control = false;
        if (!control) {
            std::fprintf(stderr,
                "[m5-task-writer-control] phase=%u width=1024 origin=0x%06X span=0x149470:0x1494B0\n",
                rs64_phase_ord(), title_origin);
            std::fflush(stderr);
            control = true;
        }
        if (rows < 2048u) {
            std::fprintf(stderr,
                "[m5-task-writer] ordinal=%u phase=%u width=1024 origin=0x%06X "
                "pc=0x%08X width=%c phys=0x%06X field=0x%X value=0x%08X\n",
                rows++, rs64_phase_ord(), title_origin, pc, width, store_phys,
                store_phys - 0x00149470u, value);
            std::fflush(stderr);
        }
    }
    if (task_writer_enabled && title_phase && store_phys == 0x00149750u &&
        store_span == 4u) {
        static uint32_t pointer_rows = 0;
        static bool pointer_control = false;
        if (!pointer_control) {
            std::fprintf(stderr,
                "[m5-selector-pointer-control] phase=%u width=1024 origin=0x%06X addr=0x80149750\n",
                rs64_phase_ord(), title_origin);
            std::fflush(stderr);
            pointer_control = true;
        }
        if (pointer_rows < 1024u) {
            std::fprintf(stderr,
                "[m5-selector-pointer-store] ordinal=%u phase=%u width=1024 origin=0x%06X "
                "pc=0x%08X value=0x%08X\n",
                pointer_rows++, rs64_phase_ord(), title_origin, pc, value);
            std::fflush(stderr);
        }
    }
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t phys = addr & 0x1FFFFFFFu;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u) ||
        phys < 0x00110000u || phys >= 0x00112000u) return;
    static uint32_t rows = 0;
    static bool control = false;
    if (!control) {
        std::fprintf(stderr,
            "[m5-state-pointer-writer-control] phase=%u width=1024 origin=0x%06X\n",
            rs64_phase_ord(), origin);
        std::fflush(stderr);
        control = true;
    }
    if (value < 0x80110000u || value >= 0x80112000u) return;
    static constexpr uint32_t candidate_pcs[4] = {
        0x800027C4u, 0x800027D0u, 0x800027DCu, 0x80003C28u
    };
    for (unsigned i = 0; i < 4; ++i) {
        if (pc == candidate_pcs[i]) {
            g_rs64_m5_pointer_latest[i] = {pc, addr, value, rs64_phase_ord()};
            break;
        }
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-state-pointer-store] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "pc=0x%08X width=%c addr=0x%08X phys=0x%06X value=0x%08X\n",
        rows++, rs64_phase_ord(), origin, pc, width, addr, phys, value);
    std::fflush(stderr);
}

extern "C" void rs64_m5_family_provenance(const char* edge,
                                             const char* family,
                                             uint32_t pc,
                                             uint32_t ra,
                                             uint32_t a0,
                                             uint32_t a1,
                                             uint32_t a2,
                                             uint32_t a3,
                                             uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FAMILY_PROVENANCE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows[2][2] = {};
    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (phase_key == 0xFFFFFFFFu) {
        std::fprintf(stderr,
            "[m5-family-provenance-control] edge=%s family=%s pc=0x%08X phase=%u\n",
            edge ? edge : "?", family ? family : "?", pc, phase);
        std::fflush(stderr);
    }
    if (key != phase_key) {
        phase_key = key;
        std::memset(rows, 0, sizeof(rows));
    }
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    const unsigned family_index =
        (family && std::strcmp(family, "initTextureLUTAndAllocBuffers") == 0) ? 1u : 0u;
    const unsigned edge_index =
        (edge && std::strcmp(edge, "entry") == 0) ? 1u : 0u;
    if (rows[family_index][edge_index] >= 128u) return;
    std::fprintf(stderr,
        "[m5-family-provenance] edge=%s family=%s row=%u phase=%u width=%u "
        "origin=0x%06X pc=0x%08X ra=0x%08X callsite=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X v0=0x%08X\n",
        edge ? edge : "?", family ? family : "?", rows[family_index][edge_index]++, phase, width,
        origin, pc, ra, ra >= 8u ? ra - 8u : 0u, a0, a1, a2, a3, v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_mix_entry(uint8_t* rdram, recomp_context* ctx, uint32_t pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_MIX_ENTRY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !rdram) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u &&
                         (origin == 0x00790400u || origin == 0x00790800u)) ||
                        (width == 512u && origin == 0x006AB400u);
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    static uint32_t control = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (!target || rows >= 256u) return;
    if (control == 0) {
        std::fprintf(stderr,
            "[m5-mix-entry-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
        control = 1;
    }
    std::fprintf(stderr,
        "[m5-mix-entry] ordinal=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X ra=0x%08X\n",
        rows++, phase, width, origin, pc, U32(ctx->r4), U32(ctx->r5),
        U32(ctx->r6), U32(ctx->r7), U32(ctx->r16), U32(ctx->r17),
        U32(ctx->r18), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_writer(uint32_t v0, uint32_t s0, uint32_t s1,
                                          uint32_t s2, uint32_t a0, uint32_t a1,
                                          uint32_t a2, uint32_t a3, uint32_t ra,
                                          uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TASK_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-writer-control] phase=%u width=1024 origin=0x%06X pc=0x80091074\n",
            rs64_phase_ord(), origin);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-writer] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "v0=0x%08X s0=0x%08X s1=0x%08X s2=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X ra=0x%08X value=0x%08X\n",
        rows++, rs64_phase_ord(), origin, v0, s0, s1, s2, a0, a1, a2, a3, ra, value);
    std::fflush(stderr);
}

extern "C" void rs64_m5_port_selector_writer(uint32_t pc, uint32_t addr,
                                                uint32_t selector, uint32_t source,
                                                uint32_t s0, uint32_t s1, uint32_t ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_PORT_SELECTOR_WRITERS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
        std::fprintf(stderr,
            "[m5-port-selector-writer-control] phase=%u width=%u origin=0x%06X\n",
            phase, width, origin);
        std::fflush(stderr);
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-port-selector-writer] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X addr=0x%08X selector=0x%08X source=0x%08X "
        "s0=0x%08X s1=0x%08X ra=0x%08X\n",
        rows++, phase, width, origin, pc, addr, selector, source, s0, s1, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_load(uint32_t index, uint32_t table_addr,
                                        uint32_t value, uint32_t s0, uint32_t s1,
                                        uint32_t s2, uint32_t a0, uint32_t a1,
                                        uint32_t a2, uint32_t ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TASK_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-load-control] phase=%u width=1024 origin=0x%06X pc=0x80091060\n",
            rs64_phase_ord(), origin);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-load] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "index=0x%08X table_addr=0x%08X value=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), origin, index, table_addr, value,
        s0, s1, s2, a0, a1, a2, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_producer(uint8_t* rdram, uint32_t pc,
                                             uint32_t a0, uint32_t a1,
                                             uint32_t a2, uint32_t a3,
                                             uint32_t index, uint32_t ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_PRODUCER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !rdram) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-producer-control] phase=%u width=1024 origin=0x%06X pc=0x%08X\n",
            rs64_phase_ord(), origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    const auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return rs64_rdram_u32(rdram, p);
    };
    const uint32_t table = 0x80149758u + ((index & 0xFFu) * 4u);
    std::fprintf(stderr,
        "[m5-selector-producer] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "pc=0x%08X index=0x%08X table=0x%08X table_word=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), origin, pc, index, table, word(table),
        a0, a1, a2, a3, ra);
    std::fflush(stderr);
}

extern "C" void rs64_s4429_heap_probe(const char* kind, uint32_t pc,
                                      uint32_t addr, uint32_t value);
extern "C" void rs64_m5_selector_table_store(uint32_t pc, uint32_t addr,
                                                 uint32_t value, uint32_t v0,
                                                 uint32_t s0, uint32_t s1,
                                                 uint32_t s2, uint32_t a0,
                                                 uint32_t a1, uint32_t a2,
                                                 uint32_t a3, uint32_t ra) {
    rs64_s4429_heap_probe("W", pc, addr, value);
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_TABLE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool selector_table_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!selector_table_phase) return;
    if (addr != 0x80149758u && addr != 0x8014975Cu) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-table-control] phase=%u width=%u origin=0x%06X\n",
            rs64_phase_ord(), width, origin);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-table-store] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X addr=0x%08X value=0x%08X v0=0x%08X s0=0x%08X "
        "s1=0x%08X s2=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X "
        "a3=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, addr, value, v0, s0, s1, s2,
        a0, a1, a2, a3, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_store_context(uint32_t pc, uint32_t v0,
                                                  uint32_t s0, uint32_t s1,
                                                  uint32_t s2, uint32_t a0,
                                                  uint32_t a1, uint32_t a2,
                                                  uint32_t a3, uint32_t ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-store-context-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-store-context] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X v0=0x%08X s0=0x%08X s1=0x%08X s2=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X ra=0x%08X\n",
        rows++, phase, width, origin, pc, v0, s0, s1, s2, a0, a1, a2, a3, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_alloc_edge(const char* stage, uint32_t pc,
                                               uint32_t a0, uint32_t a1,
                                               uint32_t a2, uint32_t a3,
                                               uint32_t v0, uint32_t s0,
                                               uint32_t s1, uint32_t s2) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_ALLOC");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-alloc-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-selector-alloc] ordinal=%u phase=%u width=%u origin=0x%06X stage=%s "
        "pc=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X v0=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X\n",
        rows++, phase, width, origin, stage ? stage : "?", pc, a0, a1, a2,
        a3, v0, s0, s1, s2);
    std::fflush(stderr);
}

namespace {
struct M5SelectorAiJoinState {
    uint32_t phase = 0xFFFFFFFFu;
    uint32_t input = 0;
    uint32_t input_source = 0;
    uint32_t callsite = 0;
    uint32_t call_a0 = 0;
    uint32_t call_a1 = 0;
    uint32_t call_a2 = 0;
    uint32_t call_s0 = 0;
    uint32_t call_s1 = 0;
    uint32_t call_v0 = 0;
    bool have_input = false;
    bool have_call = false;
};

M5SelectorAiJoinState g_m5_selector_ai_join;

struct M5SelectorAiCallLatch {
    uint32_t callsite = 0;
    uint32_t input = 0;
    uint32_t input_source = 0;
    uint32_t a0 = 0;
    uint32_t a1 = 0;
    uint32_t a2 = 0;
    uint32_t s0 = 0;
    uint32_t s1 = 0;
    uint32_t v0 = 0;
    uint32_t phase = 0;
    bool valid = false;
    bool consumed = false;
};

M5SelectorAiCallLatch g_m5_selector_ai_call_latch;
}

extern "C" void rs64_m5_selector_input_load(uint32_t pc, uint32_t value,
                                                uint32_t source, uint32_t s1,
                                                uint32_t a0, uint32_t a2,
                                                uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_INPUT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    g_m5_selector_ai_join.phase = rs64_phase_ord();
    g_m5_selector_ai_join.input = value;
    g_m5_selector_ai_join.input_source = source;
    g_m5_selector_ai_join.have_input = true;
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && (origin == 0x006AB400u || origin == 0x006AB800u));
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-input-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-input] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X value=0x%08X source=0x%08X s1=0x%08X "
        "a0=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, phase, width, origin, pc, value, source, s1, a0, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_source_write(uint32_t pc, uint32_t addr,
                                                uint32_t value, uint32_t a0,
                                                uint32_t a1, uint32_t a2,
                                                uint32_t a3, uint32_t s0,
                                                uint32_t s1, uint32_t s2) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_SOURCE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || ((addr & 0x00FFFFFFu) != 0x00165ED0u)) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && (origin == 0x006AB400u || origin == 0x006AB800u));
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-source-control] pc=0x%08X addr=0x%08X width=%u origin=0x%06X\n",
            pc, addr, width, origin);
        std::fflush(stderr);
    }
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-source] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X addr=0x%08X value=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X a3=0x%08X s0=0x%08X s1=0x%08X s2=0x%08X\n",
        rows++, phase, width, origin, pc, addr, value, a0, a1, a2, a3,
        s0, s1, s2);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_setup_contract(const char* edge, uint32_t pc,
                                                  uint32_t ra, uint32_t a0,
                                                  uint32_t a1, uint32_t a2,
                                                  uint32_t a3, uint32_t s0,
                                                  uint32_t s1, uint32_t s2,
                                                  uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_SETUP_CONTRACT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-setup-contract-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && (origin == 0x006AB400u || origin == 0x006AB800u));
    if (!target_phase) return;
    const bool ai_return = edge && edge[0] == 'a' && edge[1] == 'i' &&
        edge[2] == '-' && edge[3] == 'r';
    if (ai_return && g_m5_selector_ai_join.have_call &&
        g_m5_selector_ai_join.phase == rs64_phase_ord()) {
        static uint32_t join_phase = 0xFFFFFFFFu;
        static uint32_t join_rows = 0;
        const uint32_t join_phase_now = rs64_phase_ord();
        if (join_phase_now != join_phase) {
            join_phase = join_phase_now;
            join_rows = 0;
        }
        if (join_rows < 256u) {
            std::fprintf(stderr,
                "[m5-selector-ai-join] ordinal=%u phase=%u width=%u origin=0x%06X "
                "callsite=0x%08X input=0x%08X input_source=0x%08X "
                "call_a0=0x%08X call_a1=0x%08X call_a2=0x%08X "
                "call_s0=0x%08X call_s1=0x%08X call_v0=0x%08X result=0x%08X\n",
                join_rows++, join_phase_now, width, origin,
                g_m5_selector_ai_join.callsite,
                g_m5_selector_ai_join.have_input ? g_m5_selector_ai_join.input : 0,
                g_m5_selector_ai_join.have_input ? g_m5_selector_ai_join.input_source : 0,
                g_m5_selector_ai_join.call_a0, g_m5_selector_ai_join.call_a1,
                g_m5_selector_ai_join.call_a2, g_m5_selector_ai_join.call_s0,
                g_m5_selector_ai_join.call_s1, g_m5_selector_ai_join.call_v0, v0);
            std::fflush(stderr);
        }
    }
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-setup-contract] ordinal=%u phase=%u width=%u origin=0x%06X "
        "edge=%s pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X v0=0x%08X\n",
        rows++, phase, width, origin, edge ? edge : "?", pc, ra, a0, a1, a2,
        a3, s0, s1, s2, v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_store_entry(uint32_t pc, uint32_t ra,
                                                uint32_t a0, uint32_t a1,
                                                uint32_t a2, uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_STORE_ENTRY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    {   // s4711: ungated allocateSongChannelArray (pc 0x8008F000) caller census, all phases
        static const bool caller_log = [] {
            const char* e = std::getenv("ROGUESQ_LOG_ALLOC_CALLERS");
            return e && e[0] && e[0] != '0';
        }();
        static uint32_t n = 0;
        if (caller_log && pc == 0x8008EB5Cu && n < 256u) {   // s4712: reapplyDisplayMode entry, ra valid here
            std::fprintf(stderr,
                "[s4712-reapplyDisplayMode] n=%u ra=0x%08X a0=0x%08X width=%u origin=0x%06X\n",
                n++, ra, a0, rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu);
            std::fflush(stderr);
        }
        if (caller_log && pc == 0x8008F000u && n < 256u) {
            std::fprintf(stderr,
                "[s4711-alloc-caller] n=%u ra=0x%08X count=%u a1=0x%08X a2=0x%08X a3=0x%08X width=%u origin=0x%06X\n",
                n++, ra, a0 & 0xFFFFu, a1, a2, a3,
                rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu);
            std::fflush(stderr);
        }
    }
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-store-entry-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-store-entry] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, phase, width, origin, pc, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_producer_context(uint32_t pc, uint32_t ra,
                                                     uint32_t a0, uint32_t a1,
                                                     uint32_t a2, uint32_t a3,
                                                     uint32_t s0, uint32_t s1,
                                                     uint32_t s2) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_SELECTOR_PRODUCER_CONTEXT");
        return all && all[0] && all[0] != '0';
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-producer-context-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-producer-context] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X\n",
        rows++, phase, width, origin, pc, ra, a0, a1, a2, a3, s0, s1, s2);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_ai_boundary(uint32_t pc, uint32_t ra,
                                                uint32_t a0, uint32_t a1,
                                                uint32_t a2, uint32_t s0,
                                                uint32_t s1, uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY");
        return all && all[0] && all[0] != '0';
    }();
    if (!enabled) return;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-ai-boundary-probe-control] pc=0x%08X ra=0x%08X\n",
            pc, ra);
        std::fflush(stderr);
    }
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool title_phase = width == 1024u && origin == 0x00790400u;
    const bool hangar_phase = width == 512u &&
        (origin == 0x006AB400u || origin == 0x006AB800u);
    if (!title_phase && !hangar_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-ai-boundary-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-ai-boundary] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X "
        "s0=0x%08X s1=0x%08X v0=0x%08X\n",
        rows++, phase, width, origin, pc, ra, a0, a1, a2, s0, s1, v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_ai_return(uint32_t input, uint32_t result) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_AI_RETURN");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-ai-return-control] input=0x%08X result=0x%08X\n",
            input, result);
        std::fflush(stderr);
    }
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    if (width != 512u || origin != 0x006AB400u) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-ai-return] ordinal=%u phase=%u width=512 origin=0x%06X "
        "input=0x%08X result=0x%08X\n",
        rows++, phase, origin, input, result);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_ai_callsite(uint32_t callsite,
                                                uint32_t a0, uint32_t a1,
                                                uint32_t a2, uint32_t s0,
                                                uint32_t s1, uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY");
        return all && all[0] && all[0] != '0';
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    static bool latch_control_seen = false;
    if (!latch_control_seen) {
        std::fprintf(stderr,
            "[m5-selector-ai-call-latch-control] callsite=0x%08X width=%u origin=0x%06X\n",
            callsite, width, origin);
        std::fflush(stderr);
        latch_control_seen = true;
    }
    g_m5_selector_ai_call_latch.callsite = callsite;
    g_m5_selector_ai_call_latch.a0 = a0;
    g_m5_selector_ai_call_latch.a1 = a1;
    g_m5_selector_ai_call_latch.a2 = a2;
    g_m5_selector_ai_call_latch.s0 = s0;
    g_m5_selector_ai_call_latch.s1 = s1;
    g_m5_selector_ai_call_latch.v0 = v0;
    g_m5_selector_ai_call_latch.phase = rs64_phase_ord();
    g_m5_selector_ai_call_latch.input = g_m5_selector_ai_join.input;
    g_m5_selector_ai_call_latch.input_source = g_m5_selector_ai_join.input_source;
    g_m5_selector_ai_call_latch.valid = true;
    g_m5_selector_ai_join.phase = rs64_phase_ord();
    g_m5_selector_ai_join.callsite = callsite;
    g_m5_selector_ai_join.call_a0 = a0;
    g_m5_selector_ai_join.call_a1 = a1;
    g_m5_selector_ai_join.call_a2 = a2;
    g_m5_selector_ai_join.call_s0 = s0;
    g_m5_selector_ai_join.call_s1 = s1;
    g_m5_selector_ai_join.call_v0 = v0;
    g_m5_selector_ai_join.have_call = true;
    if (g_m5_selector_ai_join.have_input &&
        g_m5_selector_ai_join.phase == rs64_phase_ord()) {
        static uint32_t call_join_phase = 0xFFFFFFFFu;
        static uint32_t call_join_rows = 0;
        const uint32_t phase = rs64_phase_ord();
        if (phase != call_join_phase) {
            call_join_phase = phase;
            call_join_rows = 0;
        }
        if (call_join_rows < 256u) {
            std::fprintf(stderr,
                "[m5-selector-ai-call-join] ordinal=%u phase=%u width=%u origin=0x%06X "
                "callsite=0x%08X input=0x%08X input_source=0x%08X "
                "call_a0=0x%08X call_a1=0x%08X call_a2=0x%08X "
                "call_s0=0x%08X call_s1=0x%08X call_v0=0x%08X\n",
                call_join_rows++, phase, width, origin, callsite,
                g_m5_selector_ai_join.input, g_m5_selector_ai_join.input_source,
                a0, a1, a2, s0, s1, v0);
            std::fflush(stderr);
        }
    }
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-ai-callsite-control] callsite=0x%08X width=%u origin=0x%06X\n",
            callsite, width, origin);
        std::fflush(stderr);
    }
    const bool title_phase = width == 1024u && origin == 0x00790400u;
    const bool hangar_phase = width == 512u && origin == 0x006AB400u;
    if (!title_phase && !hangar_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-ai-callsite] ordinal=%u phase=%u width=%u origin=0x%06X "
        "callsite=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X v0=0x%08X\n",
        rows++, phase, width, origin, callsite, a0, a1, a2, s0, s1, v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_ai_call_latch_join(uint32_t width,
                                                       uint32_t origin,
                                                       uint32_t phase) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY");
        return all && all[0] && all[0] != '0';
    }();
    if (!enabled || width != 512u || origin != 0x006AB400u) return;
    if (g_m5_selector_ai_call_latch.consumed) return;
    g_m5_selector_ai_call_latch.consumed = true;
    if (!g_m5_selector_ai_call_latch.valid) {
        std::fprintf(stderr,
            "[m5-selector-ai-call-latch-join] phase=%u width=%u origin=0x%06X call=absent\n",
            phase, width, origin);
        std::fflush(stderr);
        return;
    }
    std::fprintf(stderr,
        "[m5-selector-ai-call-latch-join] phase=%u width=%u origin=0x%06X "
        "call_phase=%u callsite=0x%08X input=0x%08X input_source=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X v0=0x%08X\n",
        phase, width, origin, g_m5_selector_ai_call_latch.phase,
        g_m5_selector_ai_call_latch.callsite, g_m5_selector_ai_call_latch.input,
        g_m5_selector_ai_call_latch.input_source, g_m5_selector_ai_call_latch.a0,
        g_m5_selector_ai_call_latch.a1, g_m5_selector_ai_call_latch.a2,
        g_m5_selector_ai_call_latch.s0, g_m5_selector_ai_call_latch.s1,
        g_m5_selector_ai_call_latch.v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_caller(uint32_t caller_pc,
                                         uint32_t ra, uint32_t a0,
                                         uint32_t a1, uint32_t a2,
                                         uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_CALLER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-caller-control] phase=%u width=1024 origin=0x%06X pc=0x%08X\n",
            rs64_phase_ord(), origin, caller_pc);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-caller] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, rs64_phase_ord(), origin, caller_pc, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_precall(uint32_t pc, uint32_t stage,
                                             uint32_t index, uint32_t address,
                                             uint32_t value, uint32_t a0,
                                             uint32_t a1, uint32_t a2,
                                             uint32_t s0, uint32_t s1) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_PRECALL");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-precall-control] phase=%u width=1024 origin=0x%06X\n",
            rs64_phase_ord(), origin);
        std::fflush(stderr);
    }
    if (rows >= 2048u) return;
    std::fprintf(stderr,
        "[m5-selector-precall] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "stage=%u pc=0x%08X index=0x%08X address=0x%08X value=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X\n",
        rows++, rs64_phase_ord(), origin, stage, pc, index, address, value,
        a0, a1, a2, s0, s1);
    std::fflush(stderr);
}

extern "C" void rs64_m5_state_pointer_consumer(uint32_t s1) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-state-pointer-consumer] ordinal=%u phase=%u width=1024 origin=0x%06X s1=0x%08X "
        "edge_s1=%08X edge_a0=%08X edge_ra=%08X edge_ord=%u edge_match=%u "
        "c0=%08X/%08X/%08X/%u c1=%08X/%08X/%08X/%u c2=%08X/%08X/%08X/%u c3=%08X/%08X/%08X/%u "
        "down_pc=%08X down_addr=%08X down_value=%08X down_ord=%u\n",
        rows++, rs64_phase_ord(), origin, s1,
        g_rs64_m5_zcfree_edge.s1, g_rs64_m5_zcfree_edge.a0,
        g_rs64_m5_zcfree_edge.ra, g_rs64_m5_zcfree_edge.ordinal,
        g_rs64_m5_zcfree_edge.valid && g_rs64_m5_zcfree_edge.s1 == s1 ? 1u : 0u,
        g_rs64_m5_pointer_latest[0].pc, g_rs64_m5_pointer_latest[0].addr,
        g_rs64_m5_pointer_latest[0].value, g_rs64_m5_pointer_latest[0].phase,
        g_rs64_m5_pointer_latest[1].pc, g_rs64_m5_pointer_latest[1].addr,
        g_rs64_m5_pointer_latest[1].value, g_rs64_m5_pointer_latest[1].phase,
        g_rs64_m5_pointer_latest[2].pc, g_rs64_m5_pointer_latest[2].addr,
        g_rs64_m5_pointer_latest[2].value, g_rs64_m5_pointer_latest[2].phase,
        g_rs64_m5_pointer_latest[3].pc, g_rs64_m5_pointer_latest[3].addr,
        g_rs64_m5_pointer_latest[3].value, g_rs64_m5_pointer_latest[3].phase,
        g_rs64_m5_downstream_latest.pc, g_rs64_m5_downstream_latest.addr,
        g_rs64_m5_downstream_latest.value, g_rs64_m5_downstream_latest.ordinal);
    std::fflush(stderr);
}

static void rs64_m5_frequency_producer(uint8_t* rdram, recomp_context* ctx,
                                       uint32_t mq_addr, uint32_t msg,
                                       int32_t flag) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_PRODUCERS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return rs64_rdram_u32(rdram, p);
    };
    auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFFFFFFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    static std::atomic<uint32_t> send_seq{0};
    const uint32_t sequence = send_seq.fetch_add(1, std::memory_order_relaxed);
    std::fprintf(stderr,
        "[m5-frequency-producer] ordinal=%u seq=%u phase=%u width=%u origin=0x%06X "
        "mq=0x%08X msg=0x%08X flag=%d s0=0x%08X s1=0x%08X source_word=0x%08X "
        "source_byte=0x%02X branch_selector=0x%08X branch_state=0x%04X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X v0=0x%08X v1=0x%08X ra=0x%08X\n",
        rows++, sequence, rs64_phase_ord(), width, origin, mq_addr, msg, (int)flag, s0, s1,
        word(s0 + 0x60u), byte(s0 + 0x22u), U32(ctx->r2),
        word(s1 + 0x22u) & 0xFFFFu, U32(ctx->r4), U32(ctx->r5),
        U32(ctx->r6), U32(ctx->r7), U32(ctx->r2), U32(ctx->r3), U32(ctx->r31));
    std::fflush(stderr);
}

static void rs64_m5_frequency_receive_join(uint8_t* rdram,
                                             recomp_context* ctx,
                                             uint32_t mq_addr,
                                             int32_t flag,
                                             int32_t result,
                                             uint32_t delivered_hint) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_RECEIVES");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || result != 0 || mq_addr != 0x8010FEE0u) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    uint32_t delivered = delivered_hint;
    const uint32_t slot = U32(ctx->r5);
    if (delivered == 0xFFFFFFFFu && slot >= 0x80000000u && slot <= 0x807FFFFCu) {
        const uint32_t p = slot - 0x80000000u;
        delivered = rs64_rdram_u32(rdram, p);
    }
    std::fprintf(stderr,
        "[m5-frequency-receive] ordinal=%u phase=%u width=%u origin=0x%06X "
        "mq=0x%08X msg=0x%08X flag=%d result=%d slot=0x%08X delivered=0x%08X "
        "guest_pc=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, mq_addr, (uint32_t)ctx->r5,
        (int)flag, (int)result, slot, delivered,
        (unsigned)g_rs64_last_guest_pc, U32(ctx->r31));
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-frequency-receive-positive] post-receive join is live\n");
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_frequency_consumer(uint8_t* rdram,
                                               recomp_context* ctx,
                                               uint32_t callsite) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_CONSUMERS");
        const char* output = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_OUTPUT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0') ||
               (output && output[0] && output[0] != '0');
    }();
    if (!enabled || U32(ctx->r4) != 0x8010FEE0u || U32(ctx->r2) != 0) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    const uint32_t state = U32(ctx->r16);
    g_rs64_m5_frequency_pending = {U32(ctx->r4), U32(ctx->r5), callsite, state, true};
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return rs64_rdram_u32(rdram, p);
    };
    std::fprintf(stderr,
        "[m5-frequency-consumer] ordinal=%u phase=%u width=%u origin=0x%06X "
        "callsite=0x%08X mq=0x%08X msg_slot=0x%08X result=%d state=0x%08X "
        "state_word=0x%08X state_next=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X a3=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, callsite, U32(ctx->r4),
        U32(ctx->r5), (int)U32(ctx->r2), state, word(state),
        word(state + 0x1E8u), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),
        U32(ctx->r7), U32(ctx->r31));
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-frequency-consumer-positive] post-receive witness is live\n");
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_frequency_output_use(uint8_t* rdram,
                                                 recomp_context* ctx,
                                                 uint32_t callsite,
                                                 uint32_t output_pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_OUTPUT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    if (!g_rs64_m5_frequency_pending.valid ||
        g_rs64_m5_frequency_pending.callsite != callsite) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-frequency-output] ordinal=%u phase=%u width=%u origin=0x%06X "
        "queue=0x%08X msg=0x%08X callsite=0x%08X state=0x%08X "
        "output_pc=0x%08X output=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X a3=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, g_rs64_m5_frequency_pending.queue,
        g_rs64_m5_frequency_pending.msg, callsite,
        g_rs64_m5_frequency_pending.state, output_pc, U32(ctx->r3), U32(ctx->r4),
        U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r31));
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-frequency-output-positive] first post-consumer output is live\n");
        std::fflush(stderr);
    }
    g_rs64_m5_frequency_pending.valid = false;
}

extern "C" int rogue_current_thread_id(uint8_t* rdram);
// s4262: per-second table of (guest tid, mq, guest ra) osSendMesg counts for tid 0 and for
// every sender to 0x8011A818 (ROGUESQ_S4262=1). Correlate with [s4259] GAP t= lines.
// s4263: per-queue send/recv/full/would-block counters for the gated triple, printed with
// the s4262 per-second flush together with the guest flag bytes 0x8011A890..0x8011A8A0.
static const uint32_t kS4263Q[3] = {0x8011A818u, 0x8011A7E8u, 0x80128CF0u};
static std::atomic<uint64_t> g_s4263_send[3], g_s4263_full[3], g_s4263_recv[3], g_s4263_rblock[3];
static int s4263_idx(uint32_t mq) { for (int i = 0; i < 3; ++i) if (kS4263Q[i] == mq) return i; return -1; }
static void s4263_note(uint8_t* rdram, uint32_t mq, bool is_send, int32_t flag) {
    const int i = s4263_idx(mq);
    if (i < 0) return;
    const OSMesgQueue& q = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq);
    if (is_send) {
        static std::atomic<int> bt_n[3];
        if (bt_n[i].fetch_add(1) < 3) {
            void* fr[24]; const int nf = backtrace(fr, 24);
            std::fprintf(stderr, "[s4263-bt] send mq=0x%08X\n", mq); std::fflush(stderr);
            backtrace_symbols_fd(fr, nf, 2);
        }
    }
    if (is_send) { g_s4263_send[i]++; if (q.validCount >= q.msgCount) g_s4263_full[i]++; }
    else { g_s4263_recv[i]++; if (q.validCount == 0 && flag != 0) g_s4263_rblock[i]++; }
}
// s4264: guest-thread blocked-recv registry + per-(tid,mq) send/recv counts, flushed per second.
struct S4264Blk { uint32_t mq; int32_t flag; std::chrono::steady_clock::time_point t; bool active; };
static std::mutex g_s4264_m;
static S4264Blk g_s4264_blk[64];
static std::map<std::pair<int, uint32_t>, uint64_t> g_s4264_sends, g_s4264_recvs;
static void s4264_enter(int tid, uint32_t mq, int32_t flag) {
    std::lock_guard<std::mutex> lk(g_s4264_m);
    g_s4264_recvs[{tid, mq}]++;
    g_s4264_blk[tid & 63] = {mq, flag, std::chrono::steady_clock::now(), true};
}
static void s4264_exit(int tid) {
    std::lock_guard<std::mutex> lk(g_s4264_m);
    g_s4264_blk[tid & 63].active = false;
}
static void s4264_flush(int sec) {
    std::lock_guard<std::mutex> lk(g_s4264_m);
    auto now = std::chrono::steady_clock::now();
    for (int i = 0; i < 64; ++i) {
        if (!g_s4264_blk[i].active) continue;
        const double ms = std::chrono::duration<double, std::milli>(now - g_s4264_blk[i].t).count();
        std::fprintf(stderr, "[s4264-blk] t=%d tid=%d mq=0x%08X flag=%d blocked_ms=%.0f\n", sec, i, g_s4264_blk[i].mq, g_s4264_blk[i].flag, ms);
    }
    for (auto& kv : g_s4264_sends) std::fprintf(stderr, "[s4264-snd] t=%d tid=%d mq=0x%08X n=%llu\n", sec, kv.first.first, kv.first.second, (unsigned long long)kv.second);
    for (auto& kv : g_s4264_recvs) std::fprintf(stderr, "[s4264-rcv] t=%d tid=%d mq=0x%08X n=%llu\n", sec, kv.first.first, kv.first.second, (unsigned long long)kv.second);
    g_s4264_sends.clear(); g_s4264_recvs.clear();
}
static void s4263_flush(uint8_t* rdram, int sec) {
    s4264_flush(sec);
    char fl[64]; int n = 0;
    for (int a = 0; a < 16; ++a) n = rs64_apf(fl, sizeof fl, n, "%02X", (unsigned)MEM_BU(-0X5770 + a, (int64_t)(int32_t)0x80120000));
    for (int i = 0; i < 3; ++i) {
        const OSMesgQueue& q = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))kS4263Q[i]);
        std::fprintf(stderr, "[s4263] t=%d mq=0x%08X send=%llu full=%llu recv=%llu rblock=%llu valid=%d flags[8011A890]=%s\n", sec,
                     kS4263Q[i], (unsigned long long)g_s4263_send[i].exchange(0), (unsigned long long)g_s4263_full[i].exchange(0),
                     (unsigned long long)g_s4263_recv[i].exchange(0), (unsigned long long)g_s4263_rblock[i].exchange(0), (int)q.validCount, fl);
    }
}
static void s4262_note_send(uint8_t* rdram, uint32_t mq, uint32_t ra) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_S4262"); return e && *e && *e != '0'; }();
    if (!on) return;
    s4263_note(rdram, mq, true, 0);
    const int tid = rogue_current_thread_id(rdram) & 63;
    { std::lock_guard<std::mutex> lk2(g_s4264_m); g_s4264_sends[{tid, mq}]++; }
    if (tid != 0 && mq != 0x8011A818u) return;
    static std::mutex m;
    static std::map<std::tuple<int, uint32_t, uint32_t>, uint64_t> tab;
    static auto t0 = std::chrono::steady_clock::now();
    static int last_sec = 0;
    std::lock_guard<std::mutex> lk(m);
    tab[{tid, mq, ra}]++;
    const int sec = (int)std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    if (sec != last_sec) {
        for (auto& kv : tab)
            std::fprintf(stderr, "[s4262] t=%d tid=%d mq=0x%08X ra=0x%08X n=%llu\n", last_sec,
                         std::get<0>(kv.first), std::get<1>(kv.first), std::get<2>(kv.first),
                         (unsigned long long)kv.second);
        s4263_flush(rdram, last_sec);
        std::fflush(stderr);
        tab.clear();
        last_sec = sec;
    }
}


// s4580: ring of recv/send events on the rs_malloc lock queue 0x8010FEE0. A recv that blocks and is still
// blocked 1.5 s later dumps the ring plus the last unmatched holder. Env ROGUESQ_LOG_S4580=1. Diagnostic only.
namespace s4580 {
struct Ev { uint32_t seq; char k; uint64_t htid; int gtid; uint32_t sp, ra, c1, c2, pc; int vcb, vca; int flag; };
static std::mutex m; static Ev ring[128]; static uint32_t n = 0, nr = 0, ns = 0;
static uint64_t holder_h = 0; static int holder_g = -1; static uint32_t holder_seq = 0;
static std::atomic<uint32_t> blk_pending{0}; static int dumps = 0;
static bool on() { static const bool e = [] { const char* v = std::getenv("ROGUESQ_LOG_S4580"); return v && *v && *v != '0'; }(); return e; }
static void dump(const char* why) {
    std::lock_guard<std::mutex> lk(m);
    if (dumps++ >= 8) return;
    std::fprintf(stderr, "[s4580-dump] %s total=%u recvs=%u sends=%u holder_g=%d holder_h=%lx holder_seq=%u\n", why, n, nr, ns, holder_g, (unsigned long)holder_h, holder_seq);
    uint32_t cnt = n < 128 ? n : 128;
    for (uint32_t i = n - cnt; i < n; i++) { const Ev& e = ring[i & 127];
        std::fprintf(stderr, "[s4580-ev] seq=%u %c htid=%lx gtid=%d sp=%08X ra=%08X [sp+14]=%08X [sp+30]=%08X pc=%08X vc %d->%d flag=%d\n", e.seq, e.k, (unsigned long)e.htid, e.gtid, e.sp, e.ra, e.c1, e.c2, e.pc, e.vcb, e.vca, e.flag); }
    std::fflush(stderr);
}
static uint32_t rec(uint8_t* rdram, recomp_context* ctx, char k, int vcb, int vca, int flag) {
    { static std::once_flag once; std::call_once(once, [] { std::thread([] { for (int t : {60, 40, 40, 40}) { std::this_thread::sleep_for(std::chrono::seconds(t)); dump("periodic"); } }).detach(); }); }
    std::lock_guard<std::mutex> lk(m);
    uint32_t sp = (uint32_t)ctx->r29;
    Ev& e = ring[n & 127]; e.seq = n; e.k = k; e.htid = (uint64_t)(uintptr_t)pthread_self(); e.gtid = rogue_current_thread_id(rdram) & 63;
    e.sp = sp; e.ra = (uint32_t)ctx->r31; e.c1 = (uint32_t)MEM_W(0x14, (gpr)(int32_t)sp); e.c2 = (uint32_t)MEM_W(0x30, (gpr)(int32_t)sp);
    e.pc = (uint32_t)g_rs64_last_guest_pc; e.vcb = vcb; e.vca = vca; e.flag = flag;
    if (k == 'R') { nr++; holder_h = e.htid; holder_g = e.gtid; holder_seq = n; }
    if (k == 'S') { ns++; holder_g = -1; holder_h = 0; }
    return n++;
}
static int vc(uint8_t* rdram, uint32_t q) { return (int)TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))q)->validCount; }
}
/* s5038: log-only census of message-queue structure validity at osSendMesg/osRecvMesg entry. */
static void s5038_mq_census(uint8_t* rdram, uint32_t mq, uint32_t ra, const char* kind) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_MQ_CENSUS"); return e && e[0] && e[0] != '0'; }();
    static const bool force = [] { const char* e = std::getenv("ROGUESQ_MQ_CENSUS_FORCE"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static std::atomic<unsigned long> calls{0}, viol{0}; static std::atomic<int> shown_k[4]{}; /* s5040: per-kind log budget */
    const int ki = kind[0] == 'j' ? 0 : kind[0] == 's' && kind[1] == 'e' ? 1 : kind[0] == 's' ? 2 : 3;
    ++calls;
    auto kseg0 = [](uint32_t a, uint32_t n) { return a >= 0x80000000u && (uint64_t)(a - 0x80000000u) + n <= (rs64_ram_top - 0x80000000u); };
    bool bad = !kseg0(mq, sizeof(OSMesgQueue)) || (mq & 3u);
    int32_t mc = 0, vcnt = 0, first = 0; uint32_t msg = 0;
    if (!bad) {
        const OSMesgQueue* q = TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq);
        mc = q->msgCount; vcnt = q->validCount; first = q->first; msg = (uint32_t)q->msg;
        bad = mc < 0 || mc > 4096 || vcnt < 0 || vcnt > mc || (mc > 0 && (first < 0 || first >= mc)) ||
              (mc > 0 && (!kseg0(msg, (uint32_t)mc * 4u) || (msg & 3u)));
    }
    if (force) bad = true;
    if (!bad) return;
    unsigned long v = ++viol;
    if (shown_k[ki].fetch_add(1) < 16)
        std::fprintf(stderr, "[s5038-mq-census] %s ra=%08X mq=%08X msgCount=%d valid=%d first=%d msg=%08X calls=%lu viol=%lu%s\n",
                     kind, ra, mq, mc, vcnt, first, msg, calls.load(), v, force ? " (FORCE control)" : "");
}
/* s5039: strong definition of the lib's weak hook; covers osJamMesg (kind 0) and osSetEventMesg (kind 1, queue in r5). */
extern "C" void rs64_s5039_mq_hook(uint8_t* rdram, uint32_t mq, uint32_t ra, int kind) {
    s5038_mq_census(rdram, mq, ra, kind ? "setevent" : "jam");
}
// s7191 M6 boot freeze: passive per-guest-thread "current OS wait" table + a 48-event ring of every send/recv on the
// video-ack queue 0x80128CF0 (with validCount and vflag 0x80037808 at the event), printed by [stall-dump]
// (rt64_render_context.cpp). The s6993s L4 freeze left retrace (0x8011CD28) on CF0's full-send list with vflag=0 and no
// receiver: static census (s7191) shows that state needs a receiver whose post-recv vflag clear was delayed >=2 VIs and
// which then waits somewhere other than CF0. This names that thread and its wait (mq + guest ra) on the next recurrence
// without relying on the host sampler. Default on, ~zero cost; ROGUESQ_WAITTAB=0 off.
extern "C" {
struct Rs64WaitEnt { std::atomic<uint32_t> mq{0}, op{0}, pending{0}, n{0}; std::atomic<uintptr_t> ra{0}; };
Rs64WaitEnt g_rs64_waittab[64];
struct Rs64Cf0Ev { std::atomic<uint32_t> seq{0}, op{0}, tid{0}, valid{0}, vflag{0}, fullq{0}, mtq{0}; std::atomic<int64_t> us{0}; std::atomic<uintptr_t> ra{0}; };
static Rs64Cf0Ev g_rs64_cf0[48];
static std::atomic<uint32_t> g_rs64_cf0_n{0};
static bool rs64_waittab_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_WAITTAB"); return !(e && *e == '0'); }(); return on; }
static int64_t rs64_wt_us() { return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static void rs64_cf0_ev(uint8_t* rdram, char op, int tid, uintptr_t ra) {
    const uint32_t k = g_rs64_cf0_n.fetch_add(1, std::memory_order_relaxed);
    Rs64Cf0Ev& e = g_rs64_cf0[k % 48];
    const OSMesgQueue& q = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))0x80128CF0u);
    e.seq = k + 1; e.op = (uint32_t)op; e.tid = (uint32_t)tid; e.ra = ra; e.valid = (uint32_t)q.validCount;
    e.vflag = rdram[0x37808 ^ 3]; e.fullq = (uint32_t)q.blocked_on_send; e.mtq = (uint32_t)q.blocked_on_recv; e.us = rs64_wt_us();
}
struct Rs64WaitScope {
    uint8_t* rdram; uint32_t mq; uintptr_t ra; int tid; char op; bool on;
    Rs64WaitScope(uint8_t* r, uint32_t mq_, uintptr_t ra_, int32_t flag, char op_) : rdram(r), mq(mq_), ra(ra_), tid(-1), op(op_), on(false) {
        if (!rs64_waittab_on()) return;
        tid = rogue_current_thread_id(r);
        const bool cf0 = mq == 0x80128CF0u;
        on = flag != 0 || cf0;
        if (!on) return;
        if (flag != 0) { Rs64WaitEnt& w = g_rs64_waittab[tid & 63]; w.mq = mq; w.ra = ra; w.op = (uint32_t)op; w.pending = 1; w.n++; }
        if (cf0) rs64_cf0_ev(r, op, tid, ra);
    }
    ~Rs64WaitScope() {
        if (!on) return;
        Rs64WaitEnt& w = g_rs64_waittab[tid & 63];
        if (w.mq.load() == mq && w.ra.load() == ra) w.pending = 0;
        if (mq == 0x80128CF0u) rs64_cf0_ev(rdram, (char)(op | 0x20), tid, ra); // lower case = returned
    }
};
static const char* rs64_wt_sym(uintptr_t a, char* buf, size_t n) { // host caller -> recompiled function name+off
    Dl_info di{}; if (a && dladdr((void*)a, &di) && di.dli_sname) { std::snprintf(buf, n, "%s+0x%lx", di.dli_sname, (unsigned long)(a - (uintptr_t)di.dli_saddr)); return buf; }
    std::snprintf(buf, n, "%p", (void*)a); return buf; }
// Printed by [stall-dump]: one row per guest thread id seen, and the CF0 ring oldest first (age in ms before the dump).
void rs64_waittab_dump(void) {
    if (!rs64_waittab_on()) { std::fprintf(stderr, "[stall-wait] off (ROGUESQ_WAITTAB=0)\n"); return; }
    for (int i = 0; i < 64; ++i) {
        const Rs64WaitEnt& w = g_rs64_waittab[i];
        if (!w.n.load()) continue;
        char sb[160];
        std::fprintf(stderr, "[stall-wait] tid=%d %s op=%c mq=%08X caller=%s blocking_calls=%u\n", i, w.pending.load() ? "IN" : "last",
                     (char)w.op.load(), w.mq.load(), rs64_wt_sym(w.ra.load(), sb, sizeof sb), w.n.load());
    }
    const uint32_t n = g_rs64_cf0_n.load(); const int64_t now = rs64_wt_us();
    for (uint32_t k = (n > 48 ? n - 48 : 0); k < n; ++k) {
        const Rs64Cf0Ev& e = g_rs64_cf0[k % 48];
        char sb[160];
        std::fprintf(stderr, "[stall-cf0] seq=%u age_ms=%.1f op=%c tid=%u caller=%s valid=%u vflag=%u fullq=%08X mtq=%08X\n", e.seq.load(),
                     (now - e.us.load()) / 1000.0, (char)e.op.load(), e.tid.load(), rs64_wt_sym(e.ra.load(), sb, sizeof sb), e.valid.load(), e.vflag.load(), e.fullq.load(), e.mtq.load());
    }
}
}
// s7192 M6 boot freeze forced-state arm: ROGUESQ_CF0_DELAY_TEST=<k>[:<ms>] (default ms 40). On the k-th CF0 (0x80128CF0)
// blocking recv that returns a message, before guest code runs again (so before its vflag clear), block that guest thread
// cooperatively for <ms> on a private queue fed by osSetTimer (guest scratch 0x200 below the thread's sp).
// The retrace thread keeps running, so it posts CF0 again with vflag still set: the s6993 pre-state, on demand.
// Prints [cf0-delay] begin/end plus the CF0 ring (positive control: an S row by the retrace thread during the delay).
struct Rs64Cf0Delay {
    uint8_t* rdram; recomp_context* ctx; bool cf0;
    static int k_arm() { static const int k = [] { const char* e = std::getenv("ROGUESQ_CF0_DELAY_TEST"); return e ? atoi(e) : 0; }(); return k; }
    static int ms_arm() { static const int m = [] { const char* e = std::getenv("ROGUESQ_CF0_DELAY_TEST"); const char* c = e ? std::strchr(e, ':') : nullptr; return c ? atoi(c + 1) : 40; }(); return m; }
    Rs64Cf0Delay(uint8_t* r, recomp_context* c) : rdram(r), ctx(c), cf0(k_arm() > 0 && (uint32_t)c->r4 == 0x80128CF0u && (s32)c->r6 != 0) {}
    ~Rs64Cf0Delay() {
        // s7607 class UW: a destroyed thread unwinds thread_terminated through osRecvMesg_recomp. Blocking here (the
        // nested osRecvMesg below) during that unwind re-enters wait_for_resumed on a dead context, which throws again
        // inside a destructor -> std::terminate. The delay is a test arm; never run it while unwinding.
        if (std::uncaught_exceptions() > 0) return;
        if (!cf0 || (s32)ctx->r2 != 0) return;
        static std::atomic<int> n{0};
        if (n.fetch_add(1) + 1 != k_arm()) return;
        // Scratch on the receiver's own guest stack, 0x200 below sp (free; the nested wait is host-side). s7192 v1 used
        // 0x9FF00000: above rs64_ram_top, so mesgqueue_guard refused the queue, the recv returned at once and the timer's
        // post to the refused queue froze every boot (10/10) - an instrument artifact, not the s6993 state.
        // s7194: ROGUESQ_CF0_DELAY_TEST=<k>:<ms>:v1 restores the v1 scratch (0x9FF00000) as the refused-mq requeue test arm.
        static const bool v1 = [] { const char* e = std::getenv("ROGUESQ_CF0_DELAY_TEST"); return e && std::strstr(e, ":v1") != nullptr; }();
        const uint32_t base = v1 ? 0x9FF00000u : ((((uint32_t)ctx->r29) - 0x200u) & ~0xFu);
        const uint32_t mq = base, buf = base + 0x20u, tm = base + 0x40u;
        osCreateMesgQueue(rdram, (PTR(OSMesgQueue))mq, (PTR(OSMesg))buf, 1);
        const int ms = ms_arm(); const int64_t t0 = rs64_wt_us(); const uint32_t g0 = g_rs64_cf0_n.load();
        std::fprintf(stderr, "[cf0-delay] begin k=%d ms=%d tid=%d vflag=%u cf0_seq=%u\n", k_arm(), ms, rogue_current_thread_id(rdram), rdram[0x37808 ^ 3], g0);
        osSetTimer(rdram, (PTR(OSTimer))tm, (OSTime)ms * 46875ull, 0, (PTR(OSMesgQueue))mq, (OSMesg)0x7192);
        osRecvMesg(rdram, (PTR(OSMesgQueue))mq, (PTR(OSMesg))0, 1);
        const OSMesgQueue& q = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))0x80128CF0u);
        std::fprintf(stderr, "[cf0-delay] end waited_ms=%.1f cf0_events=%u valid=%d vflag=%u fullq=%08X\n", (rs64_wt_us() - t0) / 1000.0,
                     g_rs64_cf0_n.load() - g0, (int)q.validCount, rdram[0x37808 ^ 3], (uint32_t)q.blocked_on_send);
        rs64_waittab_dump();
    }
};
// s7193 M6 boot freeze, retrace-dependency census: ROGUESQ_RETRACE_HOLD_TEST=<start>:<period>:<ms>:<count> (default off).
// The retrace thread (tid 0, viRetraceHandlerThread) sends NOBLOCK to 0x80128D10 once per VI just before its vflag check and
// blocking CF0 post, whatever the vflag. On the start-th such send and every period-th after (up to count holds), hold the
// retrace thread for <ms> BEFORE the send, cooperatively on a private timer queue on its own stack (s7192 v2 scratch rule).
// Every other guest thread runs free, so at the end of the hold each one sits in the first wait that only the retrace thread
// can release. Prints [rt-hold] (CF0 state, vflag, 0x8011A8C8/C9/89D) and [rt-hold-w] per thread (IN = blocked now, mq, recompiled
// caller, blocking calls made during the hold). A thread that ends IN a queue other than CF0 with ~0 calls during the hold is a
// retrace-dependent second wait: the cycle edge the s6993 freeze needs (H-cycle). All waits on CF0 / VI-forwarded queues = H-none.
struct Rs64RetraceHold {
    static const int* cfg() { static int c[4] = {0, 0, 0, 0}; static const bool once = [] {
        const char* e = std::getenv("ROGUESQ_RETRACE_HOLD_TEST"); if (e && *e) std::sscanf(e, "%d:%d:%d:%d", &c[0], &c[1], &c[2], &c[3]); return true; }(); (void)once; return c; }
    static void maybe(uint8_t* rdram, recomp_context* ctx) {
        const int* c = cfg();
        if (c[0] <= 0 || (uint32_t)ctx->r4 != 0x80128D10u || (s32)ctx->r6 != 0) return;
        if (rogue_current_thread_id(rdram) != 0) return;
        static int vi = 0, held = 0; ++vi;
        if (vi < c[0] || held >= (c[3] > 0 ? c[3] : 1) || ((vi - c[0]) % (c[1] > 0 ? c[1] : 1)) != 0) return;
        ++held;
        uint32_t n0[64]; for (int i = 0; i < 64; ++i) n0[i] = g_rs64_waittab[i].n.load();
        const uint32_t base = (((uint32_t)ctx->r29) - 0x200u) & ~0xFu;
        const uint32_t mq = base, buf = base + 0x20u, tm = base + 0x40u;
        const int ms = c[2] > 0 ? c[2] : 50; const int64_t t0 = rs64_wt_us();
        osCreateMesgQueue(rdram, (PTR(OSMesgQueue))mq, (PTR(OSMesg))buf, 1);
        osSetTimer(rdram, (PTR(OSTimer))tm, (OSTime)ms * 46875ull, 0, (PTR(OSMesgQueue))mq, (OSMesg)0x7193);
        osRecvMesg(rdram, (PTR(OSMesgQueue))mq, (PTR(OSMesg))0, 1);
        const OSMesgQueue& q = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))0x80128CF0u);
        std::fprintf(stderr, "[rt-hold] n=%d vi=%d waited_ms=%.1f cf0_valid=%d cf0_fullq=%08X cf0_mtq=%08X vflag=%u c8=%u c9=%u f89d=%u\n", held, vi,
                     (rs64_wt_us() - t0) / 1000.0, (int)q.validCount, (uint32_t)q.blocked_on_send, (uint32_t)q.blocked_on_recv, rdram[0x37808 ^ 3],
                     rdram[0x11A8C8 ^ 3], rdram[0x11A8C9 ^ 3], rdram[0x11A89D ^ 3]);
        for (int i = 1; i < 64; ++i) {
            const Rs64WaitEnt& w = g_rs64_waittab[i];
            if (!w.n.load()) continue;
            char sb[160];
            std::fprintf(stderr, "[rt-hold-w] n=%d tid=%d %s op=%c mq=%08X caller=%s calls_during=%u\n", held, i, w.pending.load() ? "IN" : "last",
                         (char)w.op.load(), w.mq.load(), rs64_wt_sym(w.ra.load(), sb, sizeof sb), w.n.load() - n0[i]);
        }
    }
};
// s7392 class BB: guest message-queue drop census (ROGUESQ_S7392_MQ=1, default off). Every guest osSendMesg/osJamMesg result
// keyed by (kind, mq, caller ra, flags) and every external (host event / non-game-thread) delivery keyed by (mq, source):
// calls, failures (full-queue NOBLOCK returns / external drops), requeues, and the post-send high-water of validCount vs
// msgCount. Summary table every 10 s wall to stderr as [s7392-mq] rows (SIGKILL-safe). ROGUESQ_S7392_CTL=1 plants a
// capacity-1 queue below the guest $sp on the first game-thread send and fills it twice by each path: the census must count
// exactly one guest failure (ra=C7C7C7C7) and one external drop on that queue. Report: tools/s7392_mq_report.py <log>.
namespace s7392 {
struct Ent { char kind; uint32_t mq; uint64_t key; int flags; uint64_t calls, fails, rq; int hiv, cnt; double t_first_fail; };
static std::mutex mu; static Ent tab[512]; static int ntab = 0; static double t0 = 0, t_last = 0;
static bool on() { static const bool v = [] { const char* e = std::getenv("ROGUESQ_S7392_MQ"); return e && e[0] && e[0] != '0'; }(); return v; }
static double now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static void dump_locked(double t) {
    std::fprintf(stderr, "[s7392-mq-begin] t=%.1f n=%d\n", t - t0, ntab);
    for (int i = 0; i < ntab; i++) {
        const Ent& e = tab[i];
        char sb[160];
        if (e.kind == 'E') std::snprintf(sb, sizeof sb, "src%d", (int)(int64_t)e.key);
        else if (e.key == 0xC7C7C7C7u) std::snprintf(sb, sizeof sb, "CONTROL");
        else rs64_wt_sym((uintptr_t)e.key, sb, sizeof sb);
        std::fprintf(stderr, "[s7392-mq] t=%.1f kind=%c mq=%08X key=%s flags=%d calls=%llu fails=%llu rq=%llu hiv=%d cnt=%d tff=%.1f\n",
                     t - t0, e.kind, e.mq, sb, e.flags, (unsigned long long)e.calls, (unsigned long long)e.fails,
                     (unsigned long long)e.rq, e.hiv, e.cnt, e.fails ? e.t_first_fail - t0 : -1.0);
    }
    std::fflush(stderr);
}
static void note(uint8_t* rdram, char kind, uint32_t mq, uint64_t key, int flags, bool fail, bool rq) {
    int hiv = -1, cnt = -1;
    if (mq >= 0x80000000u && mq < rs64_ram_top) {
        const OSMesgQueue* q = TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq);
        hiv = q->validCount; cnt = q->msgCount;
    }
    std::lock_guard<std::mutex> lk(mu);
    const double t = now();
    if (t0 == 0) { t0 = t; t_last = t; }
    int i = 0;
    for (; i < ntab; i++) if (tab[i].kind == kind && tab[i].mq == mq && tab[i].key == key && tab[i].flags == flags) break;
    if (i == ntab) {
        if (ntab == 512) return;
        tab[ntab++] = Ent{kind, mq, key, flags, 0, 0, 0, -1, cnt, 0};
    }
    Ent& e = tab[i];
    e.calls++; if (rq) e.rq++;
    if (fail) { if (!e.fails) e.t_first_fail = t; e.fails++; }
    if (hiv > e.hiv) e.hiv = hiv;
    if (cnt >= 0) e.cnt = cnt;
    if (t - t_last >= 10.0) { t_last = t; dump_locked(t); }
}
static void control(uint8_t* rdram, recomp_context* ctx) {
    static const bool ctl = [] { const char* e = std::getenv("ROGUESQ_S7392_CTL"); return e && e[0] && e[0] != '0'; }();
    static std::atomic<bool> done{false};
    if (!ctl || done.exchange(true)) return;
    const uint32_t q = ((uint32_t)ctx->r29 - 0x100u) & ~7u, buf = q + 0x40u;
    osCreateMesgQueue(rdram, (int32_t)q, (int32_t)buf, 1);
    const s32 r1 = osSendMesg(rdram, (int32_t)q, (OSMesg)1, OS_MESG_NOBLOCK);
    note(rdram, 'S', q, 0xC7C7C7C7u, 0, r1 != 0, false);
    const s32 r2 = osSendMesg(rdram, (int32_t)q, (OSMesg)2, OS_MESG_NOBLOCK);
    note(rdram, 'S', q, 0xC7C7C7C7u, 0, r2 != 0, false);
    // external path: two non-requeue externals into the (full) planted queue; the next game-thread osSendMesg drains them
    ultramodern::enqueue_external_message((int32_t)q, (OSMesg)3, false, false);
    const s32 r3 = osSendMesg(rdram, (int32_t)q, (OSMesg)4, OS_MESG_NOBLOCK); // drains externals first, then fails itself
    std::fprintf(stderr, "[s7392-ctl] q=%08X r1=%d r2=%d r3=%d valid=%d\n", q, (int)r1, (int)r2, (int)r3,
                 (int)TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))q)->validCount);
}
} // namespace s7392
extern "C" void rs64_s7392_send(uint8_t* rdram, uint32_t mq, uint64_t ra, int flags, int result, int jam) {
    if (s7392::on()) s7392::note(rdram, jam ? 'J' : 'S', mq, ra, flags, result != 0, false);
}
extern "C" void rs64_s7392_ext(uint8_t* rdram, uint32_t mq, int src, int sent, int rq) {
    if (s7392::on()) s7392::note(rdram, 'E', mq, (uint64_t)(int64_t)src, 0, !sent, rq != 0);
}
// s7399 class BI: event-message payload census (ROGUESQ_S7399_EVP=1, default off). Every external delivery keyed by
// (mq, source, msg) and every guest receive on a hardware-event queue (VI 80114388, SI 80110770, SP 8011A420, DP 8011A408,
// AI 80149670) keyed by (mq, msg, first byte at msg when msg is a RAM pointer = the type byte the SP/AI consumers dispatch
// on). Table every 10 s wall as [s7399-ev] / [s7399-rv] rows (SIGKILL-safe). ROGUESQ_S7399_CTL=1 plants a capacity-2 queue
// 0x200 below the guest $sp at the first guest osSendMesg and posts one external message msg=BADC0DE0 source=Sp through the real
// enqueue -> dequeue path, then receives it: the report must show that (mq, Sp, BADC0DE0) row as a payload mismatch.
// Report: tools/s7399_evp_report.py <log>.
namespace s7399 {
struct Ev { uint32_t mq, msg; int src; uint64_t n, unsent; };
struct Rv { uint32_t mq, msg; int tb; uint64_t n; };
static std::mutex mu; static Ev ev[256]; static int nev = 0; static Rv rv[256]; static int nrv = 0; static double t_last = 0;
static uint32_t ctl_q = 0;
static bool on() { static const bool v = [] { const char* e = std::getenv("ROGUESQ_S7399_EVP"); return e && e[0] && e[0] != '0'; }(); return v; }
static double now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static void dump_locked() {
    std::fprintf(stderr, "[s7399-begin] nev=%d nrv=%d ctl_q=%08X\n", nev, nrv, ctl_q);
    for (int i = 0; i < nev; i++)
        std::fprintf(stderr, "[s7399-ev] mq=%08X src=%d msg=%08X n=%llu unsent=%llu\n", ev[i].mq, ev[i].src, ev[i].msg,
                     (unsigned long long)ev[i].n, (unsigned long long)ev[i].unsent);
    for (int i = 0; i < nrv; i++)
        std::fprintf(stderr, "[s7399-rv] mq=%08X msg=%08X tb=%d n=%llu\n", rv[i].mq, rv[i].msg, rv[i].tb, (unsigned long long)rv[i].n);
    std::fflush(stderr);
}
static void tick_locked() { const double t = now(); if (t_last == 0) t_last = t; if (t - t_last >= 10.0) { t_last = t; dump_locked(); } }
static bool evq(uint32_t mq) {
    return mq == 0x80114388u || mq == 0x80110770u || mq == 0x8011A420u || mq == 0x8011A408u || mq == 0x80149670u || (ctl_q && mq == ctl_q);
}
static void control(uint8_t* rdram, recomp_context* ctx) {
    static const bool ctl = [] { const char* e = std::getenv("ROGUESQ_S7399_CTL"); return e && e[0] && e[0] != '0'; }();
    static std::atomic<bool> done{false};
    if (!ctl || done.exchange(true)) return;
    const uint32_t q = ((uint32_t)ctx->r29 - 0x200u) & ~7u, buf = q + 0x40u, dst = q + 0x60u;
    osCreateMesgQueue(rdram, (int32_t)q, (int32_t)buf, 2);
    { std::lock_guard<std::mutex> lk(mu); ctl_q = q; }
    ultramodern::enqueue_external_message_src((int32_t)q, (OSMesg)0xBADC0DE0u, false, ultramodern::EventMessageSource::Sp);
    const s32 r = osRecvMesg(rdram, (int32_t)q, (int32_t)dst, OS_MESG_NOBLOCK); // drains externals, then receives the plant
    std::fprintf(stderr, "[s7399-ctl] q=%08X sp=%08X recv=%d got=%08X\n", q, (uint32_t)ctx->r29, (int)r, (uint32_t)*TO_PTR(OSMesg, (PTR(OSMesg))dst));
    std::fflush(stderr);
}
} // namespace s7399
extern "C" void rs64_s7399_ev(uint8_t* rdram, uint32_t mq, uint32_t msg, int src, int sent) {
    if (!s7399::on()) return;
    std::lock_guard<std::mutex> lk(s7399::mu);
    int i = 0;
    for (; i < s7399::nev; i++) if (s7399::ev[i].mq == mq && s7399::ev[i].src == src && s7399::ev[i].msg == msg) break;
    if (i == s7399::nev) { if (i == 256) return; s7399::ev[s7399::nev++] = s7399::Ev{mq, msg, src, 0, 0}; }
    s7399::ev[i].n++; if (!sent) s7399::ev[i].unsent++;
    s7399::tick_locked();
}
extern "C" void rs64_s7399_recv(uint8_t* rdram, uint32_t mq, uint32_t msg, uint32_t slot) {
    if (!s7399::on()) return;
    if (!s7399::evq(mq)) return;
    int tb = -1;
    if (msg >= 0x80000000u && msg < rs64_ram_top) tb = rdram[(msg & 0x1FFFFFFFu) ^ 3];
    std::lock_guard<std::mutex> lk(s7399::mu);
    int i = 0;
    for (; i < s7399::nrv; i++) if (s7399::rv[i].mq == mq && s7399::rv[i].msg == msg && s7399::rv[i].tb == tb) break;
    if (i == s7399::nrv) { if (i == 256) return; s7399::rv[s7399::nrv++] = s7399::Rv{mq, msg, tb, 0}; }
    s7399::rv[i].n++;
    s7399::tick_locked();
}
// s7393 class BC: guest osCreateMesgQueue on a LIVE queue (ROGUESQ_S7393_CQ=1, default off). Per (mq, recompiled caller):
// creates, re-creates (address created before in this run), and per create the pre-state: lost = validCount>0 (messages the
// reset discards), orphan_r / orphan_s = a thread on blocked_on_recv / blocked_on_send whose OSThread.queue points back at
// this queue (a live waiter the reset unlinks and nothing will wake), raw_r / raw_s = non-null link fields at all, held =
// re-create of a count-1 queue at validCount 0 (a mutex re-created while held). Each orphan/lost event prints one
// [s7393-ev] row at once; full [s7393-cq] table every 10 s wall (SIGKILL-safe). ROGUESQ_S7393_CTL=1 plants a queue below the
// guest $sp on the first create (validCount 1 + a fake waiter whose queue field points back) and re-creates it once through
// the hook: the table must show exactly 1 lost + 1 orphan_r on key CONTROL. Report: tools/s7393_cq_report.py <log>.
namespace s7393 {
struct Ent { uint32_t mq; uint64_t key; uint32_t gra; uint64_t creates, recreates, lost, orphan_r, orphan_s, raw_r, raw_s, held; int cnt; };
static std::mutex mu; static Ent tab[256]; static int ntab = 0; static double t0 = 0, t_last = 0;
static uint32_t seen[1024]; static int nseen = 0;
static bool on() { static const bool v = [] { const char* e = std::getenv("ROGUESQ_S7393_CQ"); return e && e[0] && e[0] != '0'; }(); return v; }
static double now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static bool inram(uint32_t a) { return a >= 0x80000000u && a < rs64_ram_top - 0x20u; }
static void dump_locked(double t) {
    std::fprintf(stderr, "[s7393-cq-begin] t=%.1f n=%d nseen=%d\n", t - t0, ntab, nseen);
    for (int i = 0; i < ntab; i++) {
        const Ent& e = tab[i]; char sb[160];
        if (e.key == 0xC7C7C7C7u) std::snprintf(sb, sizeof sb, "CONTROL"); else rs64_wt_sym((uintptr_t)e.key, sb, sizeof sb);
        std::fprintf(stderr, "[s7393-cq] mq=%08X key=%s gra=%08X cnt=%d creates=%llu recreates=%llu lost=%llu orphan_r=%llu orphan_s=%llu raw_r=%llu raw_s=%llu held=%llu\n",
            e.mq, sb, e.gra, e.cnt, (unsigned long long)e.creates, (unsigned long long)e.recreates, (unsigned long long)e.lost,
            (unsigned long long)e.orphan_r, (unsigned long long)e.orphan_s, (unsigned long long)e.raw_r, (unsigned long long)e.raw_s,
            (unsigned long long)e.held);
    }
    std::fflush(stderr);
}
static void note(uint8_t* rdram, uint32_t mq, uint64_t key, uint32_t gra, int cnt) {
    int valid = 0; uint32_t r = 0, sd = 0; bool orr = false, ors = false;
    if (inram(mq)) {
        const OSMesgQueue* q = TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq);
        valid = q->validCount; r = (uint32_t)q->blocked_on_recv; sd = (uint32_t)q->blocked_on_send;
        if (r && inram(r)) orr = (uint32_t)TO_PTR(OSThread, (PTR(OSThread))r)->queue == mq;
        if (sd && inram(sd)) ors = (uint32_t)TO_PTR(OSThread, (PTR(OSThread))sd)->queue == mq + 4u;
    }
    std::lock_guard<std::mutex> lk(mu);
    const double t = now();
    if (t0 == 0) { t0 = t; t_last = t; }
    bool re = false;
    for (int k = 0; k < nseen; k++) if (seen[k] == mq) { re = true; break; }
    if (!re && nseen < 1024) seen[nseen++] = mq;
    int i = 0;
    for (; i < ntab; i++) if (tab[i].mq == mq && tab[i].key == key) break;
    if (i == ntab) { if (ntab == 256) return; tab[ntab++] = Ent{mq, key, gra, 0, 0, 0, 0, 0, 0, 0, 0, cnt}; }
    Ent& e = tab[i];
    e.creates++; e.cnt = cnt; e.gra = gra;
    // pre-state only means something on an address this run already created (first creates see whatever was in the memory)
    if (re) {
        e.recreates++;
        if (valid > 0) e.lost++;
        if (orr) e.orphan_r++;
        if (ors) e.orphan_s++;
        if (r) e.raw_r++;
        if (sd) e.raw_s++;
        if (cnt == 1 && valid == 0) e.held++;
        if (valid > 0 || orr || ors) {
            static int nev = 0;
            if (nev++ < 200) {
                char sb[160];
                if (key == 0xC7C7C7C7u) std::snprintf(sb, sizeof sb, "CONTROL"); else rs64_wt_sym((uintptr_t)key, sb, sizeof sb);
                std::fprintf(stderr, "[s7393-ev] t=%.1f mq=%08X key=%s gra=%08X tid=%d valid=%d recv=%08X(%s) send=%08X(%s)\n", t - t0, mq, sb, gra,
                             rogue_current_thread_id(rdram), valid, r, orr ? "LIVE" : "-", sd, ors ? "LIVE" : "-");
            }
        }
    }
    if (t - t_last >= 10.0) { t_last = t; dump_locked(t); }
}
static void control(uint8_t* rdram, recomp_context* ctx) {
    static const bool ctl = [] { const char* e = std::getenv("ROGUESQ_S7393_CTL"); return e && e[0] && e[0] != '0'; }();
    static std::atomic<bool> done{false};
    if (!ctl || !ctx || done.exchange(true)) return;
    const uint32_t q = ((uint32_t)ctx->r29 - 0x200u) & ~0xFu, buf = q + 0x40u, th = q + 0x80u;
    osCreateMesgQueue(rdram, (int32_t)q, (int32_t)buf, 1);
    note(rdram, q, 0xC7C7C7C7u, 0, 1); // first create: not a re-create, must count nothing
    OSMesgQueue* mq = TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))q);
    TO_PTR(OSMesg, (PTR(OSMesg))buf)[0] = (OSMesg)0x7393; mq->validCount = 1; mq->first = 0;
    OSThread* t = TO_PTR(OSThread, (PTR(OSThread))th);
    t->next = 0; t->priority = 0; t->queue = (PTR(PTR(OSThread)))q; // fake waiter linked back to blocked_on_recv
    mq->blocked_on_recv = (PTR(OSThread))th;
    note(rdram, q, 0xC7C7C7C7u, 0, 1);
    osCreateMesgQueue(rdram, (int32_t)q, (int32_t)buf, 1);
    std::fprintf(stderr, "[s7393-ctl] q=%08X planted valid=1 recv=%08X\n", q, th);
}
} // namespace s7393
// s7394 class BD: heap-mutex re-seed window (ROGUESQ_S7394_BD=1, default off). A guest osCreateMesgQueue on 8010FEE0 at
// count 1 / validCount 0 (re-seed while held) opens a window owned by the creating guest thread; it closes on the owner's
// SECOND osSendMesg on 8010FEE0 (1st = the re-seed's own token, 2nd = rs_malloc's release) or on any OTHER thread's send on
// 8010FEE0 (foreign close = a second holder released). Per window: intr = osRecvMesg successes on 8010FEE0 by another thread
// inside the window (H-race), xcalls / ocalls = guest send/recv calls on ANY queue by other threads / by the owner (did any
// other thread run at all = H-port-timing), close kind + result (fail = token still unclaimed at close) + closing caller.
// ROGUESQ_S7394_CTL=1 positive control: in the first window that sees a foreign-thread call, that thread (real other guest
// thread context) takes the token NOBLOCK and returns it, through the same counter -> intr must be exactly 1 on that window;
// if no foreign call happens by the 3rd window, the owner injects the same take+return as fake tid 99 (CTLF, weaker).
// Rows: [s7394-win] per window (first 400), [s7394-sum] every 10 s wall. Report: tools/s7394_bd_report.py <log>.
static uint64_t s7394fix_nskip();
namespace s7394 {
static constexpr uint32_t MQ = 0x8010FEE0u;
static std::mutex mu; static bool open_ = false; static int owner = -1, osends = 0, nwin = 0, ctl_state = 0;
static uint64_t intr = 0, xcalls = 0, ocalls = 0, xtids = 0; static double topen = 0, t0 = 0, t_last = 0; static char okey[96];
static uint64_t s_win = 0, s_intr = 0, s_xwin = 0, s_foreign = 0, s_okfail = 0, s_okok = 0, s_ctl = 0; static int s_ctlwin = -1;
static uint64_t tid_recv[66]; static uint64_t s_wtids = 0; // whole-run 8010FEE0 recv successes per guest tid (65 = id<0 / >63); window owner tids
static double shadow_until = 0; static uint64_t s_shx = 0, s_shwin = 0; static bool sh_hit = false; // 20 ms after each close: xcalls counter control
static bool on() { static const bool v = [] { const char* e = std::getenv("ROGUESQ_S7394_BD"); return e && e[0] && e[0] != '0'; }(); return v; }
static bool ctl() { static const bool v = [] { const char* e = std::getenv("ROGUESQ_S7394_CTL"); return e && e[0] && e[0] != '0'; }(); return v; }
static double now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static void sum_locked(double t) {
    std::fprintf(stderr, "[s7394-sum] t=%.1f windows=%llu intr=%llu xwin=%llu foreign_close=%llu own_close_fail=%llu own_close_ok=%llu ctl=%llu ctlwin=%d ctlmode=%d open=%d shadow_x=%llu shadow_hitwin=%llu\n",
        t - t0, (unsigned long long)s_win, (unsigned long long)s_intr, (unsigned long long)s_xwin, (unsigned long long)s_foreign,
        (unsigned long long)s_okfail, (unsigned long long)s_okok, (unsigned long long)s_ctl, s_ctlwin, ctl_state, open_ ? 1 : 0,
        (unsigned long long)s_shx, (unsigned long long)s_shwin);
    std::fprintf(stderr, "[s7394-tid] t=%.1f owners=%llx", t - t0, (unsigned long long)s_wtids);
    std::fprintf(stderr, " holdfix_skips=%llu", (unsigned long long)s7394fix_nskip());
    for (int i = 0; i < 66; i++) if (tid_recv[i]) std::fprintf(stderr, " tid%d=%llu", i == 65 ? -1 : i, (unsigned long long)tid_recv[i]);
    std::fprintf(stderr, "\n");
    std::fflush(stderr);
}
static void close_locked(char kind, int tid, int result, uint64_t ra) {
    char sb[96]; rs64_wt_sym((uintptr_t)ra, sb, sizeof sb);
    const double t = now();
    s_win++; s_intr += intr; if (xcalls) s_xwin++;
    if (kind == 'F') s_foreign++; else if (result != 0) s_okfail++; else s_okok++;
    if (nwin <= 400)
        std::fprintf(stderr, "[s7394-win] n=%d t=%.2f owner=%d open=%s close=%c ctid=%d cres=%d ckey=%s us=%.0f intr=%llu xcalls=%llu xtids=%llx ocalls=%llu\n",
            nwin, topen - t0, owner, okey, kind, tid, result, sb, (t - topen) * 1e6, (unsigned long long)intr, (unsigned long long)xcalls,
            (unsigned long long)xtids, (unsigned long long)ocalls);
    open_ = false; shadow_until = t + 0.020; sh_hit = false;
    if (t - t_last >= 10.0) { t_last = t; sum_locked(t); }
}
// guest create hook (before the reset): valid = pre-create validCount
static void on_create(uint8_t* rdram, uint32_t mq, uint64_t ra, int cnt) {
    if (mq != MQ) return;
    const int valid = TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq)->validCount;
    std::lock_guard<std::mutex> lk(mu);
    const double t = now(); if (t0 == 0) { t0 = t; t_last = t; }
    if (cnt != 1 || valid != 0) return;
    if (open_) close_locked('N', rogue_current_thread_id(rdram), -9, ra); // nested re-seed: close the old one first
    open_ = true; owner = rogue_current_thread_id(rdram); s_wtids |= 1ull << (owner & 63); osends = 0; intr = xcalls = ocalls = xtids = 0; topen = t; nwin++;
    rs64_wt_sym((uintptr_t)ra, okey, sizeof okey);
}
static void take_return(uint8_t* rdram, uint32_t buf) { // NOBLOCK take of the token + give it back (net zero); lock NOT held
    if (osRecvMesg(rdram, (int32_t)MQ, (PTR(OSMesg))buf, 0) == 0) {
        { std::lock_guard<std::mutex> lk(mu); intr++; s_ctl++; }
        osSendMesg(rdram, (int32_t)MQ, 0, 0);
    }
}
// every guest send/recv on any queue, BEFORE the call (counts who runs inside the window; may run the control)
static void pre(uint8_t* rdram, recomp_context* ctx) {
    bool fire = false;
    {
        std::lock_guard<std::mutex> lk(mu);
        if (!open_) {
            if (shadow_until != 0 && rogue_current_thread_id(rdram) != owner && now() < shadow_until) { s_shx++; if (!sh_hit) { sh_hit = true; s_shwin++; } }
            return;
        }
        const int tid = rogue_current_thread_id(rdram);
        if (tid == owner) { ocalls++; return; }
        xcalls++; xtids |= 1ull << (tid & 63);
        if (ctl() && ctl_state == 0) { ctl_state = 1; s_ctlwin = nwin; fire = true; }
    }
    if (fire) take_return(rdram, ((uint32_t)ctx->r29 - 0x100u) & ~0xFu);
}
static void post_recv(uint8_t* rdram, uint32_t mq, int result) {
    if (mq != MQ || result != 0) return;
    std::lock_guard<std::mutex> lk(mu);
    const int tid = rogue_current_thread_id(rdram);
    tid_recv[(tid >= 0 && tid < 64) ? tid : 65]++;
    if (open_ && tid != owner) intr++;
}
static void post_send(uint8_t* rdram, recomp_context* ctx, uint32_t mq, int result, uint64_t ra) {
    if (mq != MQ) return;
    bool fire = false;
    {
        std::lock_guard<std::mutex> lk(mu);
        if (!open_) return;
        const int tid = rogue_current_thread_id(rdram);
        if (tid == owner) {
            if (++osends == 1) {
                if (ctl() && ctl_state == 0 && nwin >= 3) { ctl_state = 2; s_ctlwin = nwin; fire = true; } // CTLF: owner context
            } else close_locked('O', tid, result, ra);
        } else close_locked('F', tid, result, ra);
    }
    if (fire) take_return(rdram, ((uint32_t)ctx->r29 - 0x100u) & ~0xFu);
}
} // namespace s7394
// s7394 class BD fix (ROGUESQ_S7394_HOLDFIX, default ON, =0 retail): buildHeapFreeList (reached from rs_malloc ->
// ensureHeapInitialized with the heap mutex 8010FEE0 HELD) re-creates the mutex and posts a token at once, so until
// rs_malloc's own release the mutex is free while the critical section is still open; the release then drops (10/run).
// ORIGIN: retail code (buildHeapFreeList 0x80001fd4/0x80001fe8), not a port writer; s7394 measured 0 intrusions in 40
// windows but 5 thread ids take this mutex and a foreign thread ran inside 1/11 retail-arm windows. Fix: when the creating
// thread is the current holder (last successful recv, no release since), skip that one re-seed post; rs_malloc's release
// then supplies the single token -> same end state (1 token), no free token inside the section, no dropped release.
namespace s7394fix {
static std::atomic<int64_t> holder{-2}; static thread_local bool skip = false; static std::atomic<uint64_t> nskip{0};
static bool on() { static const bool v = [] { const char* e = std::getenv("ROGUESQ_S7394_HOLDFIX"); return !(e && e[0] == '0'); }(); return v; }
// s7608 class TK fix (ROGUESQ_S7608_TK, default ON, =0 = old OSId key): OSIds are not unique (s7608 witness: 8 distinct live
// threads carry id 0, 2 carry id 9) and a destroyed holder's id is re-used by the next incarnation, so "holder == my OSId" could
// name a different thread. ORIGIN: port code (this s7394 fix), not a game writer. Key the holder by host-thread incarnation
// instead: every osCreateThread spawns a new std::thread (threads.cpp), so a thread_local token is unique per guest incarnation.
static std::atomic<int64_t> gen_ctr{0};
static bool tk() { static const bool v = [] { const char* e = std::getenv("ROGUESQ_S7608_TK"); return !(e && e[0] == '0'); }(); return v; }
static int64_t me(uint8_t* rdram) {
    if (!tk()) return rogue_current_thread_id(rdram);
    static thread_local int64_t g = 0;
    if (!g) g = (int64_t(1) << 32) + gen_ctr.fetch_add(1) + 1; // never collides with an OSId (int32) or -1/-2
    return g;
}
}
static uint64_t s7394fix_nskip() { return s7394fix::nskip.load(); }
extern "C" void rs64_s7393_create(uint8_t* rdram, uint32_t mq, uint64_t ra, uint32_t gra, int cnt) {
    if (s7394::on()) s7394::on_create(rdram, mq, ra, cnt); // s7394
    if (mq == 0x8010FEE0u && cnt == 1 && s7394fix::on() && TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq)->validCount == 0 &&
        s7394fix::holder.load() == s7394fix::me(rdram)) {
        s7394fix::skip = true; // s7394 fix: next post on 8010FEE0 by this thread is the re-seed token; drop it (we hold the mutex)
        static std::atomic<bool> said{false};
        if (!said.exchange(true)) std::fprintf(stderr, "[s7394-holdfix] first held re-seed of 8010FEE0 by tid %d: re-seed post skipped (=0 retail)\n", rogue_current_thread_id(rdram));
    }
    if (!s7393::on()) return;
    s7393::note(rdram, mq, ra, gra, cnt);
}
extern "C" void osSendMesg_recomp(uint8_t* rdram, recomp_context* ctx) {
    Rs64RetraceHold::maybe(rdram, ctx);
    if (s7393::on()) s7393::control(rdram, ctx); // s7393 planted live-queue re-create control
    if (s7394::on()) s7394::pre(rdram, ctx); // s7394 window census
    if (s7394fix::skip && (uint32_t)ctx->r4 == 0x8010FEE0u) { // s7394 fix: the held re-seed's token post
        s7394fix::skip = false; s7394fix::nskip++; ctx->r2 = 0;
        if (s7394::on()) s7394::post_send(rdram, ctx, (uint32_t)ctx->r4, 0, (uint64_t)(uintptr_t)__builtin_return_address(0));
        return;
    }
    Rs64WaitScope s7191_ws(rdram, (uint32_t)ctx->r4, (uintptr_t)__builtin_return_address(0), (s32)ctx->r6, 'S');
    { /* s6571: every direct osSendMesg to the hud service queue (svc 0x80954F60 +0x1D0), any sender */
        static const bool on = [] { const char* e = std::getenv("ROGUESQ_SVCNULL"); return e && e[0] && e[0] != '0'; }();
        static int n = 0;
        if (on && (uint32_t)ctx->r4 == 0x80955130u && n++ < 40)
            std::fprintf(stderr, "[svcsend] mq=%08X msg=%08X ra=%08X flag=%d\n", (uint32_t)ctx->r4, (uint32_t)ctx->r5, (uint32_t)ctx->r31, (int)(s32)ctx->r6);
    }
    { // s6126: producer of PI OSIoMesg slots (ring 0x801107E0.., stride 0x18): log sender ra + slot dram at send time
        static const bool on = std::getenv("ROGUESQ_LOG_DMA") != nullptr;
        const uint32_t m = (uint32_t)ctx->r5;
        if (on && m >= 0x801107E0u && m < 0x80110900u) {
            fprintf(stderr, "[pi-slot-send] mq=0x%08X mb=0x%08X ra=0x%08X dram=0x%08X dev=0x%08X size=0x%X\n",
                (uint32_t)ctx->r4, m, (uint32_t)ctx->r31, (uint32_t)MEM_W(8, (int32_t)m), (uint32_t)MEM_W(0xC, (int32_t)m), (uint32_t)MEM_W(0x10, (int32_t)m));
        }
    }
    s5038_mq_census(rdram, (uint32_t)ctx->r4, (uint32_t)ctx->r31, "send");
    const bool s4580_q = s4580::on() && (uint32_t)ctx->r4 == 0x8010FEE0u; /* PATCH: s4580 */
    const int s4580_vcb = s4580_q ? s4580::vc(rdram, (uint32_t)ctx->r4) : 0;
    const uint32_t mq_addr = (uint32_t)ctx->r4;
    s4262_note_send(rdram, mq_addr, (uint32_t)ctx->r31);
    rs64_m5_frequency_producer(rdram, ctx, mq_addr, (uint32_t)ctx->r5,
                               (s32)ctx->r6);
    sendtgt_note(mq_addr, GetCurrentThreadId(),
                 recv_trace_enabled() || sendmesg_stack_enabled());
    log_m5_frame_sync_edge(rdram, "send", mq_addr, (uint32_t)ctx->r5,
                           (s32)ctx->r6);
    if (mq_addr == 0x8011A818u || mq_addr == 0x8011A7E8u || mq_addr == 0x8011A408u) {
        log_submit_boundary(rdram, "send", mq_addr, (uint32_t)ctx->r6);
    }
    if ((uint32_t)ctx->r4 == 0x8011A408u) {
        const OSMesgQueue before = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        const int32_t result = osSendMesg(rdram, (int32_t)ctx->r4,
                                          (OSMesg)ctx->r5, (s32)ctx->r6);
        const OSMesgQueue after = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        ctx->r2 = result;
        log_m5_dp_event_boundary("send", (uint32_t)ctx->r4, (uint32_t)ctx->r5,
                                 (s32)ctx->r6, result, before, after);
    } else {
        ctx->r2 = osSendMesg(rdram, (int32_t)ctx->r4, (OSMesg)ctx->r5, (s32)ctx->r6);
    }
    if (s7392::on()) { rs64_s7392_send(rdram, (uint32_t)ctx->r4, (uint64_t)(uintptr_t)__builtin_return_address(0), (int)(s32)ctx->r6, (int)(s32)ctx->r2, 0); s7392::control(rdram, ctx); }
    if (s7399::on()) s7399::control(rdram, ctx); // s7399
    if (s7394::on()) s7394::post_send(rdram, ctx, (uint32_t)ctx->r4, (int)(s32)ctx->r2, (uint64_t)(uintptr_t)__builtin_return_address(0)); // s7394
    if ((uint32_t)ctx->r4 == 0x8010FEE0u && (int32_t)ctx->r2 == 0) s7394fix::holder.store(-1); // s7394 fix: released
    if (s4580_q) s4580::rec(rdram, ctx, 'S', s4580_vcb, s4580::vc(rdram, (uint32_t)ctx->r4), (int)(s32)ctx->r6); /* PATCH: s4580 */
    static const bool enabled = [] {
        const char* rs64_la = std::getenv("ROGUESQ_LOG_ALL"); // s7728: LOG_ALL, as line ~7613
        const char* all = std::getenv("ROGUESQ_LOG_M5_DOWNSTREAM");
        return (rs64_la && *rs64_la && *rs64_la != '0') || (all && all[0] && all[0] != '0');
    }();
    if (enabled) {
        const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
        if (rs64_vi_committed_width() == 1024u &&
            (origin == 0x00790400u || origin == 0x00790800u)) {
            static uint32_t rows = 0;
            if (rows < 512u) {
                std::fprintf(stderr,
                    "[m5-os-send-return] ordinal=%u phase=%u origin=0x%06X "
                    "caller_ra=0x%08X mq=0x%08X msg=0x%08X flag=0x%08X result=0x%08X "
                    "s1=0x%08X s0=0x%08X\n",
                    rows++, rs64_phase_ord(), origin, U32(ctx->r31), U32(ctx->r4),
                    U32(ctx->r5), U32(ctx->r6), U32(ctx->r2), U32(ctx->r17), U32(ctx->r16));
                std::fflush(stderr);
            }
        }
    }
}

static void rs64_m5_frequency_contract(uint8_t* rdram, recomp_context* ctx) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_CONTRACT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;

    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) {
        bucket = key;
        rows = 0;
    }
    if (rows >= 256u) return;

    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return rs64_rdram_u32(rdram, p);
    };
    auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFFFFFFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    const uint32_t source_word = word(s0 + 0x60u);
    const uint32_t source_byte = byte(s0 + 0x22u);
    const uint32_t branch_state = word(s1 + 0x22u) & 0xFFFFu;
    std::fprintf(stderr,
        "[m5-frequency-contract] n=%u phase=%u width=%u origin=0x%06X "
        "s0=0x%08X s1=0x%08X source_word=0x%08X source_byte=0x%02X "
        "branch_selector=0x%08X branch_state=0x%04X a0=0x%08X a1=0x%08X "
        "a2=0x%08X a3=0x%08X v0=0x%08X v1=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, s0, s1, source_word,
        source_byte, U32(ctx->r2), branch_state, U32(ctx->r4), U32(ctx->r5),
        U32(ctx->r6), U32(ctx->r7), U32(ctx->r2), U32(ctx->r3), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_frequency_caller(uint8_t* rdram, recomp_context* ctx,
                                           uint32_t callsite) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_CALLERS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 256u) return;
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    auto word = [](uint8_t* rdram, uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return rs64_rdram_u32(rdram, p);
    };
    auto byte = [](uint8_t* rdram, uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFFFFFFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    std::fprintf(stderr,
        "[m5-frequency-caller] ordinal=%u phase=%u width=%u origin=0x%06X "
        "callsite=0x%08X s0=0x%08X s1=0x%08X source_word=0x%08X "
        "source_byte=0x%02X branch_selector=0x%08X branch_state=0x%04X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X v0=0x%08X v1=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, callsite, s0, s1,
        word(rdram, s0 + 0x60u), byte(rdram, s0 + 0x22u), U32(ctx->r2),
        word(rdram, s1 + 0x22u) & 0xFFFFu, U32(ctx->r4), U32(ctx->r5),
        U32(ctx->r6), U32(ctx->r7), U32(ctx->r2), U32(ctx->r3), U32(ctx->r31));
    std::fflush(stderr);
}

extern thread_local uint32_t g_s4911_guest_ra; extern thread_local void* g_s4911_host_ra;
static std::atomic<const char*> g_s4913_last_tag{"none"}; static std::atomic<int> g_s4913_last_tid{-1}; static std::atomic<uint32_t> g_s4913_last_k{0};
// s4913: ordering table for the swap handshake (ROGUESQ_S4913=1, ROGUESQ_S4913_SKIP=n events skipped, 12000 logged).
extern "C" void rs64_s4913_mark(uint8_t* rdram, const char* tag) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_S4913"); return e && *e && *e != '0'; }();
    if (!on) return;
    static std::atomic<uint32_t> n{0}; static const auto t0 = std::chrono::steady_clock::now();
    static const uint32_t skip = [] { const char* e = std::getenv("ROGUESQ_S4913_SKIP"); return e ? (uint32_t)std::atoi(e) : 0u; }();
    static const uint32_t s4913_max = [] { const char* e = std::getenv("ROGUESQ_S4913_MAX"); return e ? (uint32_t)std::atoi(e) : 12000u; }();
    const uint32_t k = n.fetch_add(1);
    g_s4913_last_tag.store(tag); g_s4913_last_tid.store((int)rogue_current_thread_id(rdram)); g_s4913_last_k.store(k);
    static std::once_flag poll_once;
    std::call_once(poll_once, [&] { std::thread([rdram] {
        // s4913 poll thread: logs every transition of byte 0x8011A8C8 with the last guest mark seen before it.
        auto addr = [&](uint32_t g) { return (volatile uint8_t*)&rdram[((uint64_t)(int64_t)(int32_t)g - 0xFFFFFFFF80000000ull) ^ 3u]; };
        volatile uint8_t* pa = addr(0x8011A8C8u); volatile uint8_t* pb = addr(0x8011A8C9u);
        uint8_t la = *pa, lb = *pb; uint32_t logged = 0, trans = 0;
        while (true) {
            const uint8_t ca = *pa, cb = *pb;
            if (ca != la || cb != lb) {
                const uint32_t kk = g_s4913_last_k.load(); ++trans;
                if (kk >= skip && logged < s4913_max) { ++logged;
                    std::fprintf(stderr, "[s4913p] t=%.3f A %u->%u B %u->%u last_k=%u last=%s last_tid=%d trans=%u\n",
                        std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count(),
                        la, ca, lb, cb, kk, g_s4913_last_tag.load(), g_s4913_last_tid.load(), trans); }
                la = ca; lb = cb;
            }
        }
    }).detach(); });
    if (k < skip || k >= skip + s4913_max) return;
    const uint8_t a = rdram[((uint64_t)(int64_t)(int32_t)0x8011A8C8u - 0xFFFFFFFF80000000ull) ^ 3u];
    const uint8_t b = rdram[((uint64_t)(int64_t)(int32_t)0x8011A8C9u - 0xFFFFFFFF80000000ull) ^ 3u];
    char slots[64] = "";
    if (tag[0] == 'p' || tag[0] == 'b' || tag[0] == 's') {   // psrr-* / bAlloc-*: arbiter slot bytes 0x80128EA8..B7
        for (uint32_t i = 0; i < 16; ++i)
            std::snprintf(slots + i * 3, 4, "%02x ", rdram[((uint64_t)(int64_t)(int32_t)(0x80128EA8u + i) - 0xFFFFFFFF80000000ull) ^ 3u]);
    }
    std::fprintf(stderr, "[s4913] k=%u t=%.3f tid=%d %s A=%u B=%u %s\n", k,
        std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count(),
        (int)rogue_current_thread_id(rdram), tag, a, b, slots);
}
struct S4913RecvScope {
    uint8_t* rdram; const char* tag;
    S4913RecvScope(uint8_t* r, uint32_t mq) : rdram(r), tag(mq == 0x80128CF0u ? "recv-ack" : mq == 0x8010FEE0u ? "recv-vi" : nullptr) { if (tag) rs64_s4913_mark(rdram, tag); }
    ~S4913RecvScope() { if (tag) rs64_s4913_mark(rdram, tag[5] == 'a' ? "recv-ack-ret" : "recv-vi-ret"); }
};
extern "C" void osRecvMesg_recomp(uint8_t* rdram, recomp_context* ctx) {
    Rs64Cf0Delay s7192_delay(rdram, ctx); // destructs last: after the recv and all bookkeeping
    if (s7394::on()) s7394::pre(rdram, ctx); // s7394 window census
    Rs64WaitScope s7191_ws(rdram, (uint32_t)ctx->r4, (uintptr_t)__builtin_return_address(0), (s32)ctx->r6, 'R');
    s5038_mq_census(rdram, (uint32_t)ctx->r4, (uint32_t)ctx->r31, "recv");
    S4913RecvScope s4913_scope(rdram, (uint32_t)ctx->r4);
    g_s4911_host_ra = __builtin_return_address(0); g_s4911_guest_ra = (uint32_t)ctx->r31; /* PATCH: s4911 guest call site of VI recv */
    const bool s4580_q = s4580::on() && (uint32_t)ctx->r4 == 0x8010FEE0u; /* PATCH: s4580 */
    int s4580_vcb = 0; uint32_t s4580_id = 0;
    if (s4580_q) { s4580_vcb = s4580::vc(rdram, (uint32_t)ctx->r4);
        if (s4580_vcb == 0 && (s32)ctx->r6 != 0) { s4580_id = s4580::rec(rdram, ctx, 'B', 0, 0, (int)(s32)ctx->r6) + 1; s4580::blk_pending = s4580_id;
            std::thread([s4580_id] { std::this_thread::sleep_for(std::chrono::milliseconds(1500)); if (s4580::blk_pending.load() == s4580_id) s4580::dump("recv still blocked 1.5s"); }).detach(); } }
    const uint32_t mq_addr = (uint32_t)ctx->r4;
    const int32_t flag = (s32)ctx->r6;
    const uint64_t tid = GetCurrentThreadId();
    uint32_t delivered_hint = 0xFFFFFFFFu;
    if (mq_addr == 0x8010FEE0u) {
        const OSMesgQueue& queue = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        if (queue.msg != NULLPTR && queue.first >= 0 && queue.first < queue.msgCount) {
            delivered_hint = (uint32_t)TO_PTR(OSMesg, queue.msg)[queue.first];
        }
    }
    { static const bool s4263_on = [] { const char* e = std::getenv("ROGUESQ_S4262"); return e && *e && *e != '0'; }();
      if (s4263_on) { s4263_note(rdram, mq_addr, false, flag); s4264_enter(rogue_current_thread_id(rdram) & 63, mq_addr, flag); } }
    rs64_m5_frequency_contract(rdram, ctx);
    recv_trace_enter(rdram, mq_addr, flag, tid);
    log_m5_frame_sync_edge(rdram, "recv", mq_addr, (uint32_t)ctx->r5, flag);
    if (mq_addr == 0x8011A818u || mq_addr == 0x8011A7E8u || mq_addr == 0x8011A408u) {
        log_submit_boundary(rdram, "recv", mq_addr, (uint32_t)flag);
    }
    if (mq_addr == 0x8011A408u) {
        const OSMesgQueue before = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        const int32_t result = osRecvMesg(rdram, (int32_t)ctx->r4,
                                          (PTR(OSMesg))ctx->r5, flag);
        const OSMesgQueue after = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        ctx->r2 = result;
        const int32_t consumed = after.msgCount > 0
            ? (after.first + after.msgCount - 1) % after.msgCount : 0;
        const uint32_t scheduler_msg =
            (result == 0 && after.msgCount > 0)
                ? (uint32_t)(uintptr_t)TO_PTR(OSMesg, after.msg)[consumed] : 0u;
        recv_trace_scheduler_type(rdram, scheduler_msg, result);
        log_m5_dp_event_boundary("recv", mq_addr, (uint32_t)ctx->r5,
                                 flag, result, before, after);
    } else if (mq_addr == 0x8010FEE0u) {
        const OSMesgQueue before = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        const int32_t result = osRecvMesg(rdram, (int32_t)ctx->r4,
                                          (PTR(OSMesg))ctx->r5, flag);
        const OSMesgQueue after = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        ctx->r2 = result;
        log_a1_queue_boundary(mq_addr, (PTR(OSMesg))ctx->r5, flag,
                              result, before, after);
    } else {
        ctx->r2 = osRecvMesg(rdram, (int32_t)ctx->r4, (PTR(OSMesg))ctx->r5, flag);
    }
    if (s7394::on()) s7394::post_recv(rdram, mq_addr, (int)(int32_t)ctx->r2); // s7394
    if (mq_addr == 0x8010FEE0u && (int32_t)ctx->r2 == 0) s7394fix::holder.store(s7394fix::me(rdram)); // s7394 fix (s7608: incarnation key)
    rs64_m5_frequency_receive_join(rdram, ctx, mq_addr, flag, (int32_t)ctx->r2,
                                   delivered_hint);
    { static const bool s4264_on = [] { const char* e = std::getenv("ROGUESQ_S4262"); return e && *e && *e != '0'; }();
      if (s4264_on) s4264_exit(rogue_current_thread_id(rdram) & 63); }
    recv_trace_exit(mq_addr, flag, tid, (int32_t)ctx->r2);
    if (s4580_q) { if (s4580_id) { uint32_t exp = s4580_id; s4580::blk_pending.compare_exchange_strong(exp, 0); }
        s4580::rec(rdram, ctx, 'R', s4580_vcb, s4580::vc(rdram, (uint32_t)ctx->r4), (int)(s32)ctx->r6); } /* PATCH: s4580 */
}

// Override upstream's osStopThread_recomp because upstream's osStopThread
// asserts(false) when called with a non-self thread handle (threads.cpp:278).
// RS64's func_80000C68 stops other threads. We replicate libultra's actual
// semantics: remove the target thread from any queue it's blocked on and
// mark it STOPPED so the scheduler doesn't try to schedule it. The host
// std::thread is parked in wait_for_resumed until a future osStartThread.
extern "C" void rs64_s7396_tq_tag(const char* t); // s7396 (ultramodern threadqueue.cpp)
extern "C" void osStopThread_recomp(uint8_t* rdram, recomp_context* ctx) {
    PTR(OSThread) t_ = (PTR(OSThread))(int32_t)ctx->r4;
    if (t_ == NULLPTR) {
        // Self-stop: same path upstream takes — yield to scheduler.
        ultramodern::run_next_thread_and_wait(PASS_RDRAM1);
        return;
    }
    OSThread* t = TO_PTR(OSThread, t_);
    if (t->state != OSThreadState::STOPPED) {
        if (t->queue != NULLPTR) {
            rs64_s7396_tq_tag("stop"); // s7396
            ultramodern::thread_queue_remove(PASS_RDRAM t->queue, t_);
        }
        t->state = OSThreadState::STOPPED;
    }
}

// s4899: per-VI ordered join of retrace-queue returns, audio-done queue returns and
// musyxSynthFrame entries. Kinds: 'R' recv1 return (0x80114388), 'T' recv2 return
// (0x80128D10), 'W' audio-loop recv enter (0x80149670), 'A' audio-loop recv return with
// message byte 1, 'a' other message byte, 'S' synth entry. Gate ROGUESQ_LOG_S4899=1.
// One [s4899-vi] row is flushed per update_screen with counts and the ordered event string.
#include <mutex>
#include <string>
extern "C" uint32_t rs64_ram_top; // s6132
namespace {
struct S4899 { std::mutex m; unsigned cnt[128] = {}; std::string order; unsigned swR = 0, swS = 0, swn = 0; uint32_t lastfb = ~0u; double tR1 = -1, tR2 = -1, tlast = 0, tB = -1, tD = -1; unsigned nB = 0, nD = 0; }; // s4903
static double s4902_ms() { using C = std::chrono::steady_clock; return std::chrono::duration<double, std::milli>(C::now().time_since_epoch()).count(); } // s4902
S4899& s4899() { static S4899 s; return s; }
bool s4899_on() { static const bool e = [] { const char* v = std::getenv("ROGUESQ_LOG_S4899"); return v && v[0] && v[0] != '0'; }(); return e; }
}
extern "C" void rs64_s4899_ev(char kind) {
    if (!s4899_on()) return;
    auto& s = s4899(); std::lock_guard<std::mutex> g(s.m);
    s.cnt[(unsigned char)kind & 127]++;
    if (kind == 'R') { s.swR++; double n = s4902_ms(); if (s.tR1 < 0) s.tR1 = n; else if (s.tR2 < 0) s.tR2 = n; } else if (kind == 'S') s.swS++;
    else if (kind == 'B') { s.nB++; if (s.tB < 0) s.tB = s4902_ms(); } else if (kind == 'D') { s.nD++; s.tD = s4902_ms(); } // s4903
    if (s.order.size() < 40) s.order.push_back(kind);
}
// s4900: one row per osViSwapBuffer that CHANGES the framebuffer (true origin change).
extern "C" void rs64_s4899_swap(uint32_t fb, uint32_t width) {
    if (!s4899_on()) return;
    auto& s = s4899(); std::lock_guard<std::mutex> g(s.m);
    s.swn++;
    if (fb != s.lastfb) {
        double now = s4902_ms();
        std::fprintf(stderr, "[s4899-sw] n=%u width=%u fb=0x%08X R=%u S=%u dt=%.2f r1=%.2f r2=%.2f nB=%u nD=%u b=%.2f d=%.2f\n", s.swn, width, fb, s.swR, s.swS,
                     now - s.tlast, s.tR1 < 0 ? -1.0 : now - s.tR1, s.tR2 < 0 ? -1.0 : now - s.tR2,
                     s.nB, s.nD, s.tB < 0 ? -1.0 : now - s.tB, s.tD < 0 ? -1.0 : now - s.tD); // s4902 s4903
        s.tlast = now; s.tR1 = s.tR2 = s.tB = s.tD = -1; s.nB = s.nD = 0;
        s.swR = 0; s.swS = 0; s.lastfb = fb;
    }
}
extern "C" void rs64_s4899_vi(uint32_t vi, uint32_t width) {
    if (!s4899_on()) return;
    auto& s = s4899(); std::lock_guard<std::mutex> g(s.m);
    std::fprintf(stderr, "[s4899-vi] vi=%u width=%u R=%u T=%u W=%u A=%u a=%u S=%u order=%s\n", vi, width,
        s.cnt['R'], s.cnt['T'], s.cnt['W'], s.cnt['A'], s.cnt['a'], s.cnt['S'], s.order.c_str());
    for (auto& c : s.cnt) c = 0;
    s.order.clear();
}

// s4432: read-only witness for the title audio loop 0x8008EE10..0x8008EE9C.
// Per (stage, phase) the first 12 hits print, then every 256th with a count.
extern "C" void rs64_audioloop_witness(uint8_t* rdram, recomp_context* ctx,
                                       uint32_t stage) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_AUDIOLOOP");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || stage > 4u) return;
    const uint32_t phase = rs64_phase_ord() & 15u;
    static uint32_t counts[5][16];
    const uint32_t n = counts[stage][phase]++;
    if (n >= 12u && (n & 255u) != 0u) return;
    auto byte = [](uint8_t* rdram, uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFFFFFFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    const uint32_t msg = U32(ctx->r29) + 0x10u;
    uint32_t msgp = 0xFFFFFFFFu, msgb = 0xFFFFFFFFu;
    if (stage == 1u && msg >= 0x80000000u && msg < 0x807FFFFCu) {
        const uint32_t p = msg - 0x80000000u;
        msgp = rs64_rdram_u32(rdram, p);
        msgb = byte(rdram, 0x80000000u | (msgp & 0x1FFFFFFFu));
    }
    std::fprintf(stderr,
        "[audioloop] stage=%u phase=%u width=%u n=%u s0=0x%08X s1=0x%08X "
        "s2=0x%08X s3=0x%08X msgptr=0x%08X msgbyte=0x%02X byte801596F0=0x%02X "
        "a0=0x%08X a1=0x%08X ra=0x%08X\n",
        stage, phase, rs64_vi_committed_width(), n, U32(ctx->r16), U32(ctx->r17),
        U32(ctx->r18), U32(ctx->r19), msgp, msgb, byte(rdram, 0x801596F0u),
        U32(ctx->r4), U32(ctx->r5), U32(ctx->r31));
    std::fflush(stderr);
}

// s4916: slot-table byte stores (0x80128EA8..B7) from the VI handler and producer-mark; tag interned.
extern "C" void rs64_s4916_sb(uint8_t* rdram, uint32_t pc, uint32_t addr, uint32_t val) {
    if (addr < 0x80128EA8u || addr >= 0x80128EB8u) return;
    static std::mutex mu; static std::set<std::string> tags;
    char b[64]; std::snprintf(b, sizeof b, "sb pc=%08X a=+%u v=%02X", pc, addr - 0x80128EA8u, val & 0xFF);
    const char* t; { std::lock_guard<std::mutex> g(mu); t = tags.insert(b).first->c_str(); }
    rs64_s4913_mark(rdram, t);
}

// s6892 G5a: cinematicSplineWalkerNpcHandler mesh pointer guard (tools/apply_s6892_walker_guard.py). Records the pointer
// op 1 stored at s2+0x18, and repairs it if a later read finds junk. Not the root cause: this names when it happened.
// ROGUESQ_S6892=0 off. ROGUESQ_S6892_TEST=<n> plants junk on the n-th tick read, as the positive control.
extern "C" void rs64_s6893_dump(const uint8_t* rdram);
namespace {
struct S6892Rec { uint32_t s2, mesh; };
S6892Rec s6892_rec[16];
unsigned s6892_next = 0, s6892_logged = 0;
unsigned long s6892_reads = 0;
// s7430 class CM: rs64_s6892.log is default-on and appended across runs (a crash run's lines survive for the next
// session) but had no cross-run cap. At process start: rotate it to .1 when it exceeds 256 KiB (ROGUESQ_S7430_CAP
// overrides), so it is bounded at ~2x cap. Writes nothing when the file is absent or small.
// ROGUESQ_S7430_NO_ROTATE=1 = old unbounded append.
struct S7430Rotate { S7430Rotate() {
    const char* nr = std::getenv("ROGUESQ_S7430_NO_ROTATE"); if (nr && *nr && *nr != '0') return;
    FILE* r = fopen("rs64_s6892.log", "r"); if (!r) return;
    fseek(r, 0, SEEK_END); const long sz = ftell(r); fclose(r);
    const char* c = std::getenv("ROGUESQ_S7430_CAP"); long cap = c ? atol(c) : 0; if (cap <= 0) cap = 256L * 1024;
    if (sz > cap && std::rename("rs64_s6892.log", "rs64_s6892.log.1") == 0)
        fprintf(stderr, "[s7430] rs64_s6892.log %ld B > cap %ld: rotated to rs64_s6892.log.1\n", sz, cap);
} } s7430_rotate;
bool s6892_valid(uint32_t v) { return (v & 3) == 0 && v >= 0x80000400u && v < 0x81800000u; } // s6893: covers the 0x81000000 spill arena of the wide bundles
uint32_t* s6892_word(uint8_t* rdram, uint32_t a) { return reinterpret_cast<uint32_t*>(rdram + (a - 0x80000000u)); }
bool s6892_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S6892"); return !(e && *e == '0'); }(); return on; }
void s6892_log(uint8_t* rdram, uint32_t s2, uint32_t bad, uint32_t good, uint32_t pc) {
    if (s6892_logged >= 32) return;
    ++s6892_logged;
    char line[1024];
    int n = snprintf(line, sizeof line, "[s6892] pc=%08X s2=%08X bad=%08X repair=%08X reads=%lu level=%u dump:", pc, s2, bad, good,
                     s6892_reads, (unsigned)rdram[(0x80130B40u ^ 3) - 0x80000000u]);
    if (s6892_valid(s2))
        for (uint32_t o = 0; o < 0x60 && n < 960; o += 4) n = rs64_apf(line, sizeof line, n, " %08X", *s6892_word(rdram, s2 + o));
    fprintf(stderr, "%s\n", line);
    static bool s7430_first = true;  // s7430: one run header per run, so appended runs can be told apart
    if (s7430_first) { s7430_first = false;
        if (FILE* f = fopen("rs64_s6892.log", "a")) { fprintf(f, "[s6892] run start pid=%d t=%ld\n", (int)getpid(), (long)time(nullptr)); fclose(f); } }
    if (FILE* f = fopen("rs64_s6892.log", "a")) { fprintf(f, "%s\n", line); fclose(f); }
}
}
extern "C" void rs64_s6892_note(uint32_t s2, uint32_t mesh) {
    if (!s6892_on()) return;
    for (S6892Rec& r : s6892_rec) if (r.s2 == s2) { r.mesh = mesh; fprintf(stderr, "[s6892] note s2=%08X mesh=%08X\n", s2, mesh); return; }
    s6892_rec[s6892_next++ & 15] = { s2, mesh };
    fprintf(stderr, "[s6892] note s2=%08X mesh=%08X\n", s2, mesh);
}
extern "C" uint32_t rs64_s6892_check(uint8_t* rdram, uint32_t s2, uint32_t v, uint32_t pc) {
    if (!s6892_on()) return v;
    ++s6892_reads;
    static const unsigned long test = [] { const char* e = std::getenv("ROGUESQ_S6892_TEST"); return e ? strtoul(e, nullptr, 0) : 0ul; }();
    if (test && s6892_reads == test) { v = 0x26282B2Bu; *s6892_word(rdram, s2 + 0x18) = v; }
    if (v == 0 || s6892_valid(v)) return v;
    uint32_t good = 0;
    for (const S6892Rec& r : s6892_rec) if (r.s2 == s2) good = r.mesh;
    s6892_log(rdram, s2, v, good, pc);
    if (s6892_reads != test) rs64_s6893_dump(rdram); // the planted control must not use up the one real dump
    if (s6892_valid(s2)) *s6892_word(rdram, s2 + 0x18) = good;
    return good;
}

/* s6963 G1e: clampGridCellLookup (0x80048948) chain-walk index. See tools/apply_s6963_cellidx.py.
   The burst seconds of the dd4 tail are this walk: an off-map cell clamps to an edge template and the function walks that
   template's instance chain (records at *(0x80137A5C), stride 0xB8, prev +4, next +6, owner +8, x +0x18, z +0x1A, own index +0x16)
   for the first record with this x,z. At dd>1 the window runs far past the map, so edge chains hold thousands of records.
   ROGUESQ_G1E_CELLIDX: 0 = retail walk, 1 = validated hits from the index (misses still walk), 2 = complete per-template index (std containers), 3 (s7024, default at dd>1; dd1 default 0) = mode 2 in a flat table, tog3 = 3 and 2 in 8 s blocks
   (one native snapshot walk per template, kept by the creation hook; misses trusted), tog = 2 and 0 in 8 s blocks.
   ROGUESQ_G1E_CELLIDX_CHECK=1: always run the retail walk and compare it with the mode-2 answer; =2 also flips every 997th answer
   (positive control: bad must count). Log line [g1e-cell] per second when ROGUESQ_G1B=1 or CHECK is set. */
#include <unordered_map>
#include <unordered_set>
#include <vector>
extern "C" { uint64_t rs64_s6963_it = 0; }
namespace {
/* s7024: mode 3 (default at dd>1) = the mode-2 index in a flat open-addressing table (linear probe, backward-shift erase) instead of
   std::unordered_map/set. s7024 measured clampGridCellLookup at 97-98% of getGridCellValueAt (123-155 ns/call, ~4500-6300 calls/frame
   at dd6). Key 0 is the empty slot (map keys carry s0 >= 0x80000000 in the high word; set keys are s0 itself). */
struct S7024Flat {
    std::vector<uint64_t> k; std::vector<uint16_t> v; size_t n = 0, mask = 0; int shift = 64;
    S7024Flat() { rehash(1 << 16); }
    void rehash(size_t cap) { std::vector<uint64_t> ok; std::vector<uint16_t> ov; ok.swap(k); ov.swap(v);
        k.assign(cap, 0); v.assign(cap, 0); mask = cap - 1; shift = 64 - __builtin_ctzll(cap); n = 0;
        for (size_t i = 0; i < ok.size(); i++) if (ok[i]) set(ok[i], ov[i]); }
    size_t h(uint64_t key) const { return (size_t)((key * 0x9E3779B97F4A7C15ull) >> shift); }
    bool get(uint64_t key, uint16_t& out) const { for (size_t i = h(key);; i = (i + 1) & mask) { const uint64_t q = k[i];
        if (q == key) { out = v[i]; return true; } if (!q) return false; } }
    void set(uint64_t key, uint16_t val) { if ((n + 1) * 2 > k.size()) rehash(k.size() * 2);
        for (size_t i = h(key);; i = (i + 1) & mask) { if (k[i] == key) { v[i] = val; return; } if (!k[i]) { k[i] = key; v[i] = val; n++; return; } } }
    void erase(uint64_t key) { size_t i = h(key); for (;; i = (i + 1) & mask) { if (!k[i]) return; if (k[i] == key) break; }
        k[i] = 0; n--; for (size_t j = (i + 1) & mask; k[j]; j = (j + 1) & mask) {  /* backward shift */
            const size_t d = h(k[j]); if (((j - d) & mask) >= ((j - i) & mask)) { k[i] = k[j]; v[i] = v[j]; k[j] = 0; i = j; } } }
    void clear() { if (n) { std::fill(k.begin(), k.end(), 0); n = 0; } }
    size_t size() const { return n; }
};
struct S6963U { std::unordered_map<uint64_t, uint16_t> m; std::unordered_set<uint32_t> c; S6963U() { m.reserve(1 << 16); }
    bool get(uint64_t q, uint16_t& o) const { auto f = m.find(q); if (f == m.end()) return false; o = f->second; return true; }
    void set(uint64_t q, uint16_t r) { m[q] = r; } void erase(uint64_t q) { m.erase(q); } size_t size() const { return m.size(); }
    bool done(uint32_t s0) const { return c.count(s0) != 0; } void mark(uint32_t s0) { c.insert(s0); } void unmark(uint32_t s0) { c.erase(s0); }
    void clear() { m.clear(); c.clear(); } void clearc() { c.clear(); } };
/* s7024 flat index with a record -> key reverse array: a record sits in one chain at one x,z, so it owns at most one key. A record
   re-used for another cell drops its old key instead of leaving it stale (the std index grew 7.5k -> 338k keys in 3 min at dd6,
   s7024 CHECK arm), so the table stays <= 65536 keys in 2^17 slots and never rehashes. */
struct S6963F { S7024Flat m, c; std::vector<uint64_t> rev; S6963F() { m.rehash(1 << 17); rev.assign(1 << 16, 0); }
    bool get(uint64_t q, uint16_t& o) const { return m.get(q, o); }
    void set(uint64_t q, uint16_t r) { uint16_t o;
        if (rev[r] && rev[r] != q && m.get(rev[r], o) && o == r) m.erase(rev[r]);
        if (m.get(q, o) && o != r && rev[o] == q) rev[o] = 0;
        m.set(q, r); rev[r] = q; }
    void erase(uint64_t q) { uint16_t o; if (m.get(q, o) && rev[o] == q) rev[o] = 0; m.erase(q); } size_t size() const { return m.size(); }
    bool done(uint32_t s0) const { uint16_t d; return c.get(s0, d); } void mark(uint32_t s0) { c.set(s0, 1); } void unmark(uint32_t s0) { c.erase(s0); }
    void clear() { m.clear(); c.clear(); std::fill(rev.begin(), rev.end(), 0); } void clearc() { c.clear(); } };
struct S6963 {
    int mode = 3, check = 0, lg = 0, blk = 8, tog = 0;  /* tog: 1 = modes 2/0 (CELLIDX=tog), 3 = modes 3/2 (CELLIDX=tog3, s7024 A/B) */
    S6963U u; S6963F f; uint32_t base = 0; uint64_t nextt = 0;
    uint64_t calls = 0, wfound = 0, wmiss = 0, ihit = 0, imiss = 0, ival = 0, snaps = 0, snapit = 0, cn = 0, cbad = 0, cpred = 0, it0 = 0, tbad = 0, tcn = 0;
    uint64_t lastsec = 0, lastblk = ~0ull, tflip = 0, tflipbad = 0; int on = 0, act = 0, fromhit = 0, flipped = 0, curf = 0; uint32_t pred = 0xFFFFu, maxchain = 0; unsigned badlines = 0;
    S6963() {
        const char* e = std::getenv("ROGUESQ_G1E_CELLIDX");
        { const char* d = std::getenv("ROGUESQ_DRAW_DISTANCE"); if (!(d && std::atof(d) > 1.0)) mode = 0; }  /* default on at dd>1 only; dd1 stays the retail walk unless set */
        if (e && *e) { if (!std::strcmp(e, "tog3")) { tog = 3; mode = 3; } else if (*e == 't') { tog = 1; mode = 2; } else mode = std::atoi(e); }
        if (const char* c = std::getenv("ROGUESQ_G1E_CELLIDX_CHECK")) check = std::atoi(c);
        if (const char* b = std::getenv("ROGUESQ_G1E_CELLIDX_BLK")) { int v = std::atoi(b); if (v > 0) blk = v; }
        const char* g = std::getenv("ROGUESQ_G1B"); lg = (g && *g && *g != '0') || check;
        act = tog ? 0 : mode;
        std::fprintf(stderr, "[g1e-cell] cfg mode=%d tog=%d check=%d blk=%d\n", mode, tog, check, blk);
    }
};
S6963& s6963() { static S6963 s; return s; }
inline uint16_t s6963_hu(const uint8_t* rd, uint32_t a) { return *(const uint16_t*)(rd + ((a ^ 2u) - 0x80000000u)); }
inline int16_t s6963_h(const uint8_t* rd, uint32_t a) { return (int16_t)s6963_hu(rd, a); }
inline uint32_t s6963_w(const uint8_t* rd, uint32_t a) { return *(const uint32_t*)(rd + (a - 0x80000000u)); }
inline bool s6963_ok(uint32_t a) { return a >= 0x80000000u && a < 0x9FFFFF00u; }
inline uint64_t s6963_key(uint32_t s0, int32_t x, int32_t z) { return ((uint64_t)s0 << 32) | ((uint64_t)(uint16_t)x << 16) | (uint16_t)z; }
inline void s6963_tick(S6963& S) {  /* s7024: one tick compare per call; mode/tog/log work runs only at second boundaries */
    /* s7433 class CP: with no toggle and no log (the default; check implies lg) the tick changes nothing (act == mode from the
       constructor, the per-second counters are only printed under lg), yet read the clock on every clampGridCellLookup call:
       ~0.04 ms/frame of guest CPU at dd4 by sample(1). ROGUESQ_S7433_TICK_ALWAYS=1 restores the old per-call tick. */
    static const bool always = [] { const char* e = std::getenv("ROGUESQ_S7433_TICK_ALWAYS"); return e && *e == '1'; }();
    if (!S.tog && !S.lg && !always) return;
    const uint64_t t = mach_absolute_time(); if (t < S.nextt) return;
    const uint64_t now = t / 24000000ull; S.nextt = (now + 1) * 24000000ull;
    if (S.tog) { const uint64_t b = now / (uint64_t)S.blk; if (b != S.lastblk) { S.lastblk = b; S.on = (int)(b & 1); S.u.clearc(); S.f.clearc(); } }
    S.act = S.tog == 3 ? (S.on ? 3 : 2) : S.tog == 1 ? (S.on ? 2 : 0) : S.mode;
    if (now != S.lastsec) {
        if (S.lg && S.lastsec) std::fprintf(stderr, "[g1e-cell] s=%llu on=%d calls=%llu it=%llu wfound=%llu wmiss=%llu ihit=%llu imiss=%llu ival=%llu snaps=%llu snapit=%llu maxchain=%u chk=%llu bad=%llu tot_chk=%llu tot_bad=%llu flip=%llu flipbad=%llu idx=%zu\n",
            (unsigned long long)now, S.act, (unsigned long long)S.calls, (unsigned long long)(rs64_s6963_it - S.it0), (unsigned long long)S.wfound, (unsigned long long)S.wmiss,
            (unsigned long long)S.ihit, (unsigned long long)S.imiss, (unsigned long long)S.ival, (unsigned long long)S.snaps, (unsigned long long)S.snapit, S.maxchain,
            (unsigned long long)S.cn, (unsigned long long)S.cbad, (unsigned long long)S.tcn, (unsigned long long)S.tbad, (unsigned long long)S.tflip, (unsigned long long)S.tflipbad, S.act == 3 ? S.f.size() : S.u.size());
        S.lastsec = now; S.calls = S.wfound = S.wmiss = S.ihit = S.imiss = S.ival = S.snaps = S.snapit = S.cn = S.cbad = 0; S.maxchain = 0; S.it0 = rs64_s6963_it;
    }
}
/* answer for (s0,x,z) from the index: record index or 0xFFFF. Snapshots the template chain on first use. */
template <class I> uint32_t s6963_answer(S6963& S, I& I_, const uint8_t* rd, uint32_t s0, int32_t x, int32_t z, uint32_t base, uint32_t head) {
    if (base != S.base) { S.base = base; S.u.clear(); S.f.clear(); }
    const bool T = g_rs64_s7022; const uint64_t ta = T ? mach_absolute_time() : 0;  /* s7025 */
    if (!I_.done(s0)) {
        uint32_t r = head, n = 0; static std::unordered_set<uint64_t> seen; seen.clear();
        while (r != 0xFFFFu && n < 200000u) {
            const uint32_t a = base + r * 0xB8u; if (!s6963_ok(a)) break;
            const uint64_t k = s6963_key(s0, s6963_h(rd, a + 0x18), s6963_h(rd, a + 0x1A));
            if (seen.insert(k).second) I_.set(k, (uint16_t)r);  /* first record in walk order wins, replacing any stale entry */
            r = s6963_hu(rd, a + 6); n++;
        }
        I_.mark(s0); S.snaps++; S.snapit += n; if (n > S.maxchain) S.maxchain = n;
        if (T) { g_s7025[8] += mach_absolute_time() - ta; g_s7025[9]++; g_s7025[10] += n; }
    }
    const uint64_t tg = T ? mach_absolute_time() : 0;
    const uint64_t key = s6963_key(s0, x, z); uint16_t r16;
    const bool got = I_.get(key, r16); const uint64_t tv = T ? mach_absolute_time() : 0; if (T) g_s7025[11] += tv - tg;
    if (!got) { if (T) g_s7025[14]++; return 0xFFFFu; }
    const uint32_t r = r16, a = base + r * 0xB8u, own = s6963_hu(rd, s0 + 0x16);
    bool v = s6963_ok(a) && s6963_h(rd, a + 0x18) == (int16_t)x && s6963_h(rd, a + 0x1A) == (int16_t)z && s6963_hu(rd, a + 8) == own;
    if (v) { const uint32_t p = s6963_hu(rd, a + 4); const uint32_t pn = p == own ? s6963_hu(rd, s0 + 6) : (s6963_ok(base + p * 0xB8u) ? s6963_hu(rd, base + p * 0xB8u + 6) : 0xFFFFu); v = pn == r; }
    if (T) { static uint32_t rp = 0; g_s7025[12] += mach_absolute_time() - tv; g_s7025[13]++; g_s7025[16] += r; if (r > g_s7025[17]) g_s7025[17] = r;
        g_s7025[18] += r > rp ? r - rp : rp - r; rp = r; g_s7025[19] += r >= 32768u; if (!v) g_s7025[15]++; }
    if (!v) { I_.erase(key); S.ival++; return 0xFFFFu; }
    return r;
}
template <class I> int s6963_pre_t(S6963& S, I& I_, uint8_t* rdram, recomp_context* ctx, int m) {
    const uint32_t base = s6963_w(rdram, 0x80137A5Cu), s0 = (uint32_t)ctx->r16, head = (uint32_t)ctx->r4 & 0xFFFFu;
    const int32_t x = (int32_t)ctx->r20, z = (int32_t)ctx->r19;
    if (S.check) { uint32_t p = s6963_answer(S, I_, rdram, s0, x, z, base, head); S.flipped = 0; if (S.check == 2 && (++S.cpred % 997u) == 0) { p = p == 0xFFFFu ? head : 0xFFFFu; S.flipped = 1; S.tflip++; } S.pred = p; return 0; }
    if (m == 1 && !I_.done(s0)) I_.mark(s0);  /* mode 1 never snapshots: hits learned from walks and creations only */
    const uint32_t r = s6963_answer(S, I_, rdram, s0, x, z, base, head);
    if (r != 0xFFFFu) {  /* register state of the walk's found exit */
        ctx->r4 = r; ctx->r5 = (gpr)(int32_t)(base + r * 0xB8u); ctx->r2 = 0xFFFF; ctx->r3 = (gpr)(int32_t)(r * 0xB8u); ctx->r6 = (gpr)(int32_t)base; ctx->r7 = 0xFFFF;
        S.ihit++; S.fromhit = 1; return 1;
    }
    if (m >= 2) { ctx->r4 = 0xFFFF; ctx->r2 = 0xFFFF; ctx->r6 = (gpr)(int32_t)base; ctx->r7 = 0xFFFF; S.imiss++; S.fromhit = 1; return 1; }  /* walk's miss exit; a1/v1 dead past 0x80048AC4 */
    return 0;
}
}
extern "C" int rs64_s6963_active() { return s6963().act; }
extern "C" int rs64_s7025_both();
extern "C" int rs64_s6963_pre(uint8_t* rdram, recomp_context* ctx) {
    const uint64_t t0 = g_rs64_s7022 ? mach_absolute_time() : 0;  /* s7025 */
    S6963& S = s6963(); s6963_tick(S); S.calls++; S.fromhit = 0;
    const int m = S.act;
    if (!m && !S.check) return 0;
    S.curf = m == 3;
    if (t0) g_s7025[7] += mach_absolute_time() - t0;
    const int rv = S.curf ? s6963_pre_t(S, S.f, rdram, ctx, m) : s6963_pre_t(S, S.u, rdram, ctx, m);
    if (t0) { g_s7025[5]++; g_s7025[6] += mach_absolute_time() - t0; }
    return rv;
}
extern "C" void rs64_s6963_post(uint8_t* rdram, recomp_context* ctx) {
    S6963& S = s6963();
    if (S.fromhit) { S.fromhit = 0; return; }
    const uint32_t r = (uint32_t)ctx->r4 & 0xFFFFFFFFu; const bool found = r != 0xFFFFu;
    if (found) S.wfound++; else S.wmiss++;
    const uint32_t s0 = (uint32_t)ctx->r16; const int32_t x = (int32_t)ctx->r20, z = (int32_t)ctx->r19;
    if (found) { if (S.curf) S.f.set(s6963_key(s0, x, z), (uint16_t)r); else S.u.set(s6963_key(s0, x, z), (uint16_t)r); }
    if (S.check) {
        S.cn++; S.tcn++;
        if ((found ? r : 0xFFFFu) != S.pred) {
            if (S.flipped) { S.tflipbad++; return; }
            S.cbad++; S.tbad++; if (S.curf) S.f.unmark(s0); else S.u.unmark(s0);
            if (S.badlines++ < 20) std::fprintf(stderr, "[g1e-cell] BAD s0=%08X x=%d z=%d walk=%04X idx=%04X\n", s0, x, z, found ? r : 0xFFFFu, S.pred);
        }
    }
    (void)rdram;
}
extern "C" void rs64_s6963_create(uint8_t* rdram, recomp_context* ctx) {  /* after 0x80048B4C: a1 = new record, now head of s0's chain */
    S6963& S = s6963(); const uint32_t a = (uint32_t)ctx->r5;
    if (!s6963_ok(a)) return;
    const uint64_t k = s6963_key((uint32_t)ctx->r16, (int32_t)ctx->r20, (int32_t)ctx->r19); const uint16_t r = s6963_hu(rdram, a + 0x16);
    /* s7025: update only the index in use. Updating both cost 88 ns -> 6.5 us per create over a dd6 hold (the std map is unbounded,
       338k keys in 3 min, s7024), ~50 ns per clamp call. Under tog/tog3 both stay current (the inactive one is re-snapshotted each
       block anyway). ROGUESQ_G1E_CREATE_BOTH=1 restores the old double update, =tog alternates it in 8 s blocks (same-run A/B). */
    const int both = rs64_s7025_both();
    if (both || S.tog || S.act != 3) S.u.set(k, r);
    if (both || S.tog || S.act == 3 || S.check) S.f.set(k, r);
}
extern "C" int rs64_s7025_both() {
    static int m = [] { const char* e = std::getenv("ROGUESQ_G1E_CREATE_BOTH"); return !e || !*e ? 0 : *e == 't' ? 2 : std::atoi(e) ? 1 : 0; }();
    if (m != 2) return m;
    return (int)((mach_absolute_time() / 24000000ull / 8ull) & 1ull);
}
/* s6993: mask for the game's "(p & 0xFF000000) == 0x80000000 means pointer" test (7 sites, tools/apply_s6993_ptrmask.py).
   0xF0000000 by default so dd>1 spill blocks at 0x81000000+ count as pointers; ROGUESQ_PTRMASK=0 restores retail 0xFF000000.
   Logs the first 16 calls where the two masks disagree (the positive control: L15 21:9 dd4 ltex_cache TLUT pointer). */
extern "C" uint32_t rs64_s6993_mask(uint32_t pc, uint32_t v) {
    static const bool wide = [] { const char* e = std::getenv("ROGUESQ_PTRMASK"); return !(e && e[0] == '0'); }();
    if ((v & 0xFF000000u) != 0x80000000u && (v & 0xF0000000u) == 0x80000000u) {
        static std::atomic<int> n{0};
        int k = n.fetch_add(1);
        if (k < 16) std::fprintf(stderr, "[s6993] pc=%08X v=%08X verdict %s (n=%d)\n", pc, v, wide ? "pointer (fixed)" : "slot id (retail mask)", k + 1);
    }
    return wide ? 0xF0000000u : 0xFF000000u;
}
// s7064 transition-stall audio wait (tools/apply_s7064_slotwait.py), ROGUESQ_S7064=<out path>. Episode = consecutive
// anyAudioSlotActive polls returning busy (v0==0) until one returns idle. Records B (begin: caller ra, active mask, slot count,
// base), S (slot snapshot, 34 guest words), M (mask change), F (synth frame inside an episode, snapshots of the episode's slots,
// first 96 frames), E (end: polls, synth frames, deacts), X (episode abandoned: >150 ms with no poll), D (deactivateVoice idx ra).
// G lines (total synth frames, run span: control rate) and fflush at each episode end; streamed (SIGKILL-safe). Measurement only.
extern "C" { int g_rs64_s7064 = [] { const char* e = getenv("ROGUESQ_S7064"); return (e && *e && *e != '0') ? 1 : 0; }(); }
namespace {
struct S7064 {
    std::mutex mu; FILE* fo = nullptr; size_t nev = 0; bool in = false; uint64_t t0 = 0, last = 0, first = 0; unsigned polls = 0,
    synth_at = 0, deact_at = 0, frames = 0; uint64_t mask = 0, emask = 0; unsigned long long synth = 0, deact = 0; double tb = 0;
    double ms(uint64_t t) { return (t - first) * tb * 1e-6; }
    void put(const char* fmt, ...) __attribute__((format(printf, 2, 3))) {
        if (nev > 400000 || !fo) return; nev++; va_list a; va_start(a, fmt); vfprintf(fo, fmt, a); va_end(a); fputc('\n', fo); }
    void flush() { if (fo) { fprintf(fo, "G synth=%llu deact=%llu span_ms=%.3f events=%zu\n", synth, deact, ms(mach_absolute_time()), nev); fflush(fo); } }
    static uint32_t w(const uint8_t* r, uint32_t va) { return rs64_rdram_u32(r, va - 0x80000000u); }
    static unsigned nslots(const uint8_t* r) { unsigned n = rs64_rdram_u8(r, 0x80141AD0u - 0x80000000u); return n > 64 ? 64 : n; }
    static uint32_t base(const uint8_t* r) { return w(r, 0x801496F8u); }
    static bool okb(uint32_t b) { return b >= 0x80000000u && b < 0x80800000u - 64 * 136; }
    uint64_t scan(const uint8_t* r) { uint32_t b = base(r); if (!okb(b)) return 0; uint64_t m = 0; unsigned n = nslots(r);
        for (unsigned i = 0; i < n; i++) if (rs64_rdram_u8(r, b + i * 136 - 0x80000000u)) m |= 1ull << i; return m; }
    void snap(const uint8_t* r, char k, uint64_t m) { uint32_t b = base(r); if (!okb(b)) return;
        for (unsigned i = 0; i < 64; i++) if (m >> i & 1) { std::string s; char h[12];
            for (unsigned j = 0; j < 34; j++) { snprintf(h, sizeof h, " %08X", w(r, b + i * 136 + j * 4)); s += h; }
            put("%c %.3f %u%s", k, ms(mach_absolute_time()), i, s.c_str()); } }
};
S7064& s7064() { static S7064* s = [] { auto* x = new S7064; mach_timebase_info_data_t i; mach_timebase_info(&i);
    x->tb = (double)i.numer / i.denom; x->first = mach_absolute_time(); x->fo = fopen(getenv("ROGUESQ_S7064"), "w"); return x; }(); return *s; }
}
extern "C" void rs64_s7064_poll(uint8_t* rdram, unsigned v0, unsigned ra) {
    S7064& s = s7064(); std::lock_guard<std::mutex> g(s.mu); const uint64_t t = mach_absolute_time();
    if (s.in && (t - s.last) * s.tb > 150e6) {
        s.put("X %.3f last=%.3f polls=%u synth=%llu", s.ms(t), s.ms(s.last), s.polls, s.synth - s.synth_at); s.in = false; s.flush(); }
    if (v0 == 0) {
        const uint64_t m = s.scan(rdram);
        if (!s.in) { s.in = true; s.t0 = t; s.polls = 0; s.frames = 0; s.synth_at = (unsigned)s.synth; s.deact_at = (unsigned)s.deact;
            s.mask = s.emask = m;
            s.put("B %.3f ra=%08X mask=%016llX n=%u base=%08X gate=%02X", s.ms(t), ra, (unsigned long long)m, S7064::nslots(rdram),
                  S7064::base(rdram), rs64_rdram_u8(rdram, 0x800A0F50u - 0x80000000u));
            s.snap(rdram, 'S', m); }
        else if (m != s.mask) { s.put("M %.3f mask=%016llX polls=%u", s.ms(t), (unsigned long long)m, s.polls); s.mask = m; s.emask |= m; }
        s.polls++;
    } else if (s.in) {
        s.put("E %.3f dur=%.3f polls=%u synth=%llu deact=%llu ra=%08X", s.ms(t), (t - s.t0) * s.tb * 1e-6, s.polls,
              s.synth - s.synth_at, s.deact - s.deact_at, ra);
        s.in = false; s.flush();
    }
    s.last = t;
}
extern "C" void rs64_s7064_deact(uint8_t* rdram, unsigned idx, unsigned ra) {
    S7064& s = s7064(); std::lock_guard<std::mutex> g(s.mu); s.deact++;
    s.put("D %.3f idx=%u ra=%08X in=%d", s.ms(mach_absolute_time()), idx, ra, (int)s.in); (void)rdram;
}
extern "C" void rs64_s7064_synth(uint8_t* rdram) {
    S7064& s = s7064(); std::lock_guard<std::mutex> g(s.mu); s.synth++;
    if (s.in && s.frames < 96) { s.frames++; const uint64_t m = s.scan(rdram);
        s.put("F %.3f k=%u mask=%016llX", s.ms(mach_absolute_time()), s.frames, (unsigned long long)m); s.snap(rdram, 'S', s.emask); }
}

/* s7496 class EU: which guest-heap blocks lie under a new fixed-RAM partition (DL-chunk pool rebuild, new colour/depth image)?
   rs64_s7496_overlap(lo, hi, cb, u) walks every rs_malloc arena chain (s7472 layout: heads 0x8010FEFC/FF00/FF18, 16 B headers,
   u16 flags 1 free / 2|6 used / 8 end, u32 size, next = h + 0x10 + size) and calls cb(hdr, size, flags, ra, age) for every block
   whose [hdr, hdr+0x10+size) intersects the physical range [lo, hi) (KSEG0 or physical, masked to 24 bits... callers pass phys).
   ra/age come from the s7475 live-record map when that block has a record (ROGUESQ_S7475_CANARY=1), else 0 / -1.
   Returns blocks visited, or -1 when a chain walk broke (a racing rs_malloc/rs_free on the guest thread: not scored).
   Self-control rs64_s7496_ctl(): the youngest s7475 record (malloc hook = second source) MUST be found used by the walk. */
extern "C" int rs64_s7496_overlap(uint32_t lo, uint32_t hi, void (*cb)(uint32_t, uint32_t, uint32_t, uint32_t, double, void*), void* u) {
    volatile uint8_t* r = g_recomp_rdram_for_wp_raw; if (!r) return -1;
    static const uint32_t heads[3] = {0x8010FEFCu, 0x8010FF00u, 0x8010FF18u};
    const uint32_t top = rs64_ram_top, vlo = 0x80000000u | lo, vhi = 0x80000000u | hi; uint32_t seen[3] = {0, 0, 0}; int narena = 0, nv = 0;
    const double now = s7325_now();
    for (int i = 0; i < 3; ++i) {
        const uint32_t h0 = s7472_rd(r, heads[i]);
        if (h0 < 0x80000000u || h0 >= top) continue;
        bool dup = false; for (int j = 0; j < narena; ++j) if (seen[j] == h0) dup = true;
        if (dup) continue; seen[narena++] = h0;
        uint32_t a = h0; int g = 0;
        for (; g < 400000; ++g) {
            const uint32_t w0 = s7472_rd(r, a), sz = s7472_rd(r, a + 4u), fl = w0 >> 16;
            if (fl & 8u) break;
            const uint32_t nx = a + 0x10u + sz;
            if ((fl != 1u && fl != 2u && fl != 6u) || (sz & 0xFu) || nx <= a || nx >= top) return -1;
            ++nv;
            if (a < vhi && nx > vlo && cb) {
                uint32_t ra = 0; double age = -1;
                { std::lock_guard<std::mutex> lk(s_s7475_mu); auto it = s_s7475_live.find(a + 0x10u); if (it != s_s7475_live.end()) { ra = it->second.ra; age = now - it->second.t; } }
                cb(a, sz, fl, ra, age, u); }
            a = nx; }
        if (g >= 400000) return -1; }
    return nv;
}
extern "C" int rs64_s7496_ctl(uint32_t* blk_out) {
    uint32_t best = 0; double bt = -1;
    { std::lock_guard<std::mutex> lk(s_s7475_mu); for (auto& kv : s_s7475_live) if (kv.second.t > bt) { bt = kv.second.t; best = kv.first; } }
    if (blk_out) *blk_out = best; if (!best) return -2;
    struct C { uint32_t want; int found; } c{best - 0x10u, 0};
    const int n = rs64_s7496_overlap((best - 0x10u) & 0xFFFFFFu, (best & 0xFFFFFFu) + 1u,
        [](uint32_t h, uint32_t, uint32_t fl, uint32_t, double, void* u) { C* p = (C*)u; if (h == p->want && fl != 1u) p->found = 1; }, &c);
    return n < 0 ? -1 : c.found;
}

// s7574 GUARD-6: ungated musyxKeyOnVoice div-trap tally (tools/apply_s7574_keyon_tally.py). kind 0 = divide
// (site = its break-7 pc), 1 = guard fire (break 7 / break 6 -> early return), 2 = entry. Returns 1 to force the
// first divide's divisor to 0 on its Nth evaluation (ROGUESQ_S7574_KEYON_FORCE0=N, positive control).
// s7576: out-of-range trunc.w.s/.d witness (include/rsp_dpc_macros.h RS64_TRUNC_W_S/D, tools/apply_s7576_trunc_total.py).
// R4300 traps on an unrepresentable trunc, so any natural hit is a port-only value: log the guest PC + value of the first
// hit per PC (up to 64 PCs) and a power-of-two total. ROGUESQ_S7576_TRUNC_CTL=N: the first N conversions report as forced.
extern "C" int rs64_s7576_trunc_ctl = [] { const char* e = getenv("ROGUESQ_S7576_TRUNC_CTL"); return e ? atoi(e) : 0; }();
extern "C" void rs64_s7576_trunc_oor(uint32_t pc, double v, int is_d) {
    static std::mutex mu; std::lock_guard<std::mutex> lk(mu);
    static uint32_t pcs[64]; static unsigned long cnt[64], total, forced; static int npc;
    bool oor = !(is_d ? (v > -2147483649.0 && v < 2147483648.0) : (v >= -2147483648.0 && v < 2147483648.0));
    if (!oor) {
        if (rs64_s7576_trunc_ctl > 0) { --rs64_s7576_trunc_ctl; ++forced;
            fprintf(stderr, "[s7576-trunc] FORCED ctl pc=%08X v=%.9g kind=%s forced=%lu\n", pc, v, is_d ? "d" : "s", forced); fflush(stderr); }
        return;
    }
    ++total; int i = 0;
    for (; i < npc; i++) if (pcs[i] == pc) break;
    if (i == npc && npc < 64) { pcs[npc] = pc; cnt[npc] = 0; npc++; }
    if (i < 64) ++cnt[i];
    if (i >= 64 || cnt[i] == 1 || (total & (total - 1)) == 0)
        fprintf(stderr, "[s7576-trunc] OOR pc=%08X v=%.9g kind=%s pc_hits=%lu total=%lu distinct_pcs=%d\n", pc, v,
                is_d ? "d" : "s", i < 64 ? cnt[i] : 0ul, total, npc), fflush(stderr);
}

extern "C" int rs64_s7574_keyon(uint32_t kind, uint32_t site, uint32_t num, uint32_t div) {
    static unsigned long ent, dv[4], gd[8], gtot; static uint32_t mind[4] = {~0u, ~0u, ~0u, ~0u};
    static long force = -2;
    static const uint32_t ds[4] = {0x80090CECu, 0x80090D30u, 0x80090D74u, 0x80090DB8u};
    static const uint32_t gs[8] = {0x80090CECu, 0x80090D04u, 0x80090D30u, 0x80090D48u,
                                   0x80090D74u, 0x80090D8Cu, 0x80090DB8u, 0x80090DD0u};
    if (force == -2) { const char* e = getenv("ROGUESQ_S7574_KEYON_FORCE0"); force = e ? atol(e) : 0; }
    auto summary = [&](const char* why) {
        fprintf(stderr, "[s7574-keyon] %s entries=%lu div=%lu,%lu,%lu,%lu mindiv=%u,%u,%u,%u guards=%lu g=", why, ent,
                dv[0], dv[1], dv[2], dv[3], mind[0], mind[1], mind[2], mind[3], gtot);
        for (int i = 0; i < 8; i++) fprintf(stderr, "%s%lu", i ? "," : "", gd[i]);
        fprintf(stderr, "\n"); fflush(stderr);
    };
    if (kind == 2) {
        ++ent;
        if (ent == 1 || (ent & (ent - 1)) == 0 || (ent % 4096) == 0) summary(ent == 1 ? "first" : "interval");
        return 0;
    }
    if (kind == 0) {
        for (int i = 0; i < 4; i++) if (ds[i] == site) {
            ++dv[i]; if (div < mind[i]) mind[i] = div;
            if (i == 0 && force > 0 && (long)dv[0] == force) {
                fprintf(stderr, "[s7574-keyon] FORCE0 site=%08X n=%lu num=%08X div=%u->0\n", site, dv[0], num, div);
                return 1;
            }
        }
        return 0;
    }
    ++gtot;
    for (int i = 0; i < 8; i++) if (gs[i] == site) ++gd[i];
    if (gtot <= 64) fprintf(stderr, "[s7574-keyon] GUARD site=%08X num=%08X div=%08X entries=%lu\n", site, num, div, ent);
    summary("guard");
    return 0;
}
