#!/usr/bin/env python3
"""s6907 G5g: hangar "fish-eye" while scrolling ships. In a scroll (state byte 0x800CC3E4 == 2, 3.85 s) the authored eye and look paths turn the view ~90 deg in the first
0.6 s, then the next craft comes on screen at the lens edge and takes ~2 s to reach centre, 5-10 units from the eye. Fix: at 0x800AD284 updateHangarBayScene holds the raw
view direction at sp+0x28; turn it from its value at the press to eye->destination craft (table 0x800CC404[cursor 0x800CD6E8], list 0x800CDA5C + i*0x278 + 0xC) over
ROGUESQ_G5G_TURN s (1.6), and back onto the raw direction over the last ROGUESQ_G5G_REL s (0.9). The eye path and all game state stay retail, settled frames are unchanged.
ROGUESQ_G5G_AIM default on, =0 retail, =tog flips every 2 scrolls. ROGUESQ_G5G_LENS=<fovy> opt-in eases fovy mid scroll. ROGUESQ_G5G_CAM=<file> logs. Runs after apply_s6904_fog
in RS64_REPLAY.  Usage: apply_s6907_aim.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6907 g5g aim"
f28 = D / "funcs_28.c"; f4 = D / "funcs_4.c"
t = f28.read_text(errors="surrogateescape"); u = f4.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
HELP = r'''/* PATCH: s6907 g5g aim */
#include <math.h>
float g_rs64_s6907_w; double g_rs64_s6907_t;
static inline float s6907_g(uint8_t* rdram, uint32_t a) { union { uint32_t u; float f; } v; v.u = (uint32_t)MEM_W(0, (int64_t)(int32_t)a); return v.f; }
static inline void s6907_slerp(const float* a, const float* b, float s, float* o) { float d = a[0]*b[0] + a[1]*b[1] + a[2]*b[2], sa = 1.0f - s, sb = s, l; int i;
  if (d > 1.0f) d = 1.0f; if (d < -0.999f) { for (i = 0; i < 3; i++) o[i] = b[i]; return; }
  if (d < 0.9999f) { float w = acosf(d), sw = sinf(w); sa = sinf((1.0f - s) * w) / sw; sb = sinf(s * w) / sw; }
  for (i = 0; i < 3; i++) o[i] = a[i] * sa + b[i] * sb; l = sqrtf(o[0]*o[0] + o[1]*o[1] + o[2]*o[2]); if (l > 1e-6f) for (i = 0; i < 3; i++) o[i] /= l; }
static inline float s6907_ease(float q) { if (q < 0.0f) q = 0.0f; if (q > 1.0f) q = 1.0f; return q * q * (3.0f - 2.0f * q); }
/* dp = guest address of the raw view direction (target - eye) on the stack, just built by updateHangarBayScene */
static void rs64_s6907_aim(uint8_t* rdram, recomp_context* ctx, uint32_t dp) {
  extern double rs64_elapsed_seconds(void);
  static int md = -1, on = 1, ps, act, fade, li = -1; static float tt = 1.6f, tr = 0.9f, dur = 3.85f, ds[3], lo[3]; static unsigned sc; static FILE* lf; static double t0, te;
  if (md < 0) { const char* e = getenv("ROGUESQ_G5G_AIM"); md = 1; if (e && *e) md = !strcmp(e, "tog") ? 2 : atoi(e) != 0;
    e = getenv("ROGUESQ_G5G_TURN"); if (e && *e && atof(e) > 0.05) tt = (float)atof(e);
    e = getenv("ROGUESQ_G5G_REL"); if (e && *e && atof(e) > 0.05) tr = (float)atof(e);
    e = getenv("ROGUESQ_G5G_CAM"); if (e && *e) lf = fopen(e, "w"); fprintf(stderr, "[g5g] aim mode %d turn %g rel %g\n", md, tt, tr); }
  double now = rs64_elapsed_seconds(); int st = (int)MEM_BU(0, (int64_t)(int32_t)0x800CC3E4u), i; float raw[3], rl, E[3], B[3], g[3], o[3], gl = 0, s = 0, r = 0;
  for (i = 0; i < 3; i++) { raw[i] = s6907_g(rdram, dp + 4 * i); E[i] = s6907_g(rdram, 0x800CD810u + 4 * i); }
  rl = sqrtf(raw[0]*raw[0] + raw[1]*raw[1] + raw[2]*raw[2]); if (rl < 1e-4f) { ps = st; return; }
  for (i = 0; i < 3; i++) { raw[i] /= rl; o[i] = raw[i]; }
  if (st == 2 && ps != 2) { sc++; if (md == 2) on = ((sc - 1) >> 1) & 1 ? 0 : 1; t0 = now; li = -1; act = 0; fade = 0; for (i = 0; i < 3; i++) ds[i] = raw[i]; }
  if (st != 2 && ps == 2 && act) { te = now; fade = 1; }
  ps = st;
  uint32_t list = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x800CDA5Cu); unsigned cur = (unsigned)MEM_BU(0, (int64_t)(int32_t)0x800CD6E8u), idx = (unsigned)MEM_BU(0, (int64_t)(int32_t)(0x800CC404u + cur));
  if (st != 2 || list < 0x80000000u || list >= RS64_RAM_TOP || cur > 8u || idx > 47u) { g_rs64_s6907_w = 0.0f; /* pan ended before the release finished (retarget): fade onto raw */
    if (fade) { float q = (float)((now - te) / 0.4); if (q >= 1.0f) fade = 0; else { s6907_slerp(lo, raw, s6907_ease(q), o); for (i = 0; i < 3; i++) { union { uint32_t u; float f; } v; v.f = o[i] * rl; MEM_W(0, (int64_t)(int32_t)(dp + 4 * i)) = (int32_t)v.u; } } }
    return; }
  if (li >= 0 && (int)idx != li && act) { t0 = now; for (i = 0; i < 3; i++) ds[i] = lo[i]; } /* press mid pan: the game retargets, restart the turn from the current view */
  li = (int)idx;
  for (i = 0; i < 3; i++) { B[i] = s6907_g(rdram, list + idx * 0x278u + 0xCu + 4 * i); g[i] = B[i] - E[i]; gl += g[i] * g[i]; }
  gl = sqrtf(gl); float tau = (float)(now - t0);
  if (gl > 1e-3f) { for (i = 0; i < 3; i++) g[i] /= gl; s = s6907_ease(tau / tt); r = s6907_ease((tau - (dur - tr)) / tr); }
  g_rs64_s6907_w = sinf(3.14159265f * s6907_ease(tau / dur)); g_rs64_s6907_t = now;
  if (on && md && gl > 1e-3f) { float a[3]; s6907_slerp(ds, g, s, a); s6907_slerp(a, raw, r, o); for (i = 0; i < 3; i++) { union { uint32_t u; float f; } v; v.f = o[i] * rl; MEM_W(0, (int64_t)(int32_t)(dp + 4 * i)) = (int32_t)v.u; lo[i] = o[i]; } act = 1; } else act = 0;
  if (lf) { static unsigned n; fprintf(lf, "%.4f %u %d %u %.3f %.3f %.3f %.3f %.3f %.3f %.4f %.4f %.4f %.4f %.4f %.4f %.3f\n", now, sc, on && md, idx, E[0], E[1], E[2], B[0], B[1], B[2], raw[0], raw[1], raw[2], o[0], o[1], o[2], gl); if ((++n & 31) == 0) fflush(lf); }
}
'''
A = "RECOMP_FUNC void "
i = t.find(A); assert i > 0
t = t[:i] + HELP + t[i:]
OLD = "    // 0x800AD284: lw          $t4, 0x28($sp)\n"
assert t.count(OLD) == 1, t.count(OLD)
t = t.replace(OLD, "    rs64_s6907_aim(rdram, ctx, (uint32_t)ADD32(ctx->r29, 0X28)); /* " + TAG + " */\n" + OLD)
L = '    { /* PATCH: s6031 far */'
a = u.find("RECOMP_FUNC void setupCameraMatrices("); assert a > 0
j = u.find(L, a); assert j > 0
LENS = ('    { /* ' + TAG + ' lens */ extern float g_rs64_s6907_w; extern double g_rs64_s6907_t; extern double rs64_elapsed_seconds(void); static float l6907 = -1.0f;\n'
        '      if (l6907 < 0.0f) { const char* e = getenv("ROGUESQ_G5G_LENS"); l6907 = (e && *e) ? (float)atof(e) : 0.0f; }\n'
        '      if (l6907 > 0.0f && (uint32_t)ctx->r17 == 0x800CD670u && rs64_elapsed_seconds() - g_rs64_s6907_t < 0.1) { union { uint32_t u; float f; } o; o.u = (uint32_t)ctx->r6; o.f += (l6907 - o.f) * g_rs64_s6907_w; ctx->r6 = (int32_t)o.u; } }\n')
u = u[:j] + LENS + u[j:]
f28.write_text(t, errors="surrogateescape"); f4.write_text(u, errors="surrogateescape"); print("applied", TAG)
