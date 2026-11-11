#!/usr/bin/env python3
"""s7115 fps60-wall-probe: opt-in near-pyramid y lift for the flight camera (applyPlayerVehicleStateUpdate exit), same-run arm.

s7115 offline (tools/s7115_neargap.py on s7114 runs a/c, exact eye-tile surface from the y-clamp sampler's own bytes): on eye-cell
near-z loss ticks the terrain is inside the render near pyramid (depth < near 30/256) on 58-61% of losses vs ~10% of flight ticks, and
every such pierce is crossed by an exact corner segment from the final eye (H-gap refuted). The retail push-out cannot clear it: its
ray test (sampleTerrainAtNpcPosition) never fires when the loop-start pos is already inside the terrain (19% / 37% of losses vs
0.5% / 1.2% of flight ticks), and the y clamp only lifts the eye to h(eye xz) - mg, so a wall rising ahead stays inside near.
(s7111's re-push "residual 0" used that same ray test.)

This arm tests the geometry the renderer clips: at the push-out exit it samples the near pyramid (9 x 5 screen rays x 4 depths up
to near = f20 / 2, half-tans 1.368 / 0.637 from s7108, basis from the corner offsets corner_i - p0) with the y-clamp height sampler
0x80067D90 (f12 = x, f14 = z, a3 = out, f0 = h; y points down, inside = y > h) and lifts pos.y by the deepest penetration + 5% near
(writes +0x14 and the +0x50 matrix copy), so no sampled point of the near pyramid is inside the terrain.
  ROGUESQ_S7115_NEARLIFT=1 | tog1   (tog1: odd absolute mach seconds, mach/24e6 & 1, the tools/s7114_parity.py clock)
Default off = retail. CHASE line (when ROGUESQ_S7101_CHASE is open): nl m= on= need= lift= (need = deepest penetration found).
NEARK (s7118): ROGUESQ_S7115_NEARK=<k>|togK:<k> sets the sampled depth to k * near (default 1.0); nl lines carry k=.
Positive control (offline): tools/s7115_neargap.py pierce on on-seconds must fall to ~0 while off-seconds stay ~10% of flight.
Idempotent; listed in fixup_game_funcs_vendored.py after apply_s7114_nearlod.py (needs the s7103/s7102 helpers)."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7115 nearlift"
FN = "RECOMP_FUNC void applyPlayerVehicleStateUpdate(uint8_t* rdram, recomp_context* ctx) {\n"
PRE = (
    '/* ' + MARK + ' */\n'
    'static int s7115_on(void) { static int md = -1; extern uint64_t mach_absolute_time(void);\n'
    '  if (md < 0) { const char* e = getenv("ROGUESQ_S7115_NEARLIFT"); md = !e || !*e || *e == \'0\' ? 0 : (!strcmp(e, "tog1") ? 2 : 1); }\n'
    '  if (md == 2) return (int)((mach_absolute_time() / 24000000ull) & 1); return md; }\n'
    '/* s7118 NEARK: ROGUESQ_S7115_NEARK=<k> samples depths s = 1..ceil(4k) (to k * near); togK:<k> = k on odd mach seconds, 1.0 on even */\n'
    'static float s7115_k(void) { static int md = -1; static float kv = 1.0f; extern uint64_t mach_absolute_time(void);\n'
    '  if (md < 0) { const char* e = getenv("ROGUESQ_S7115_NEARK"); md = 0;\n'
    '    if (e && !strncmp(e, "togK:", 5)) { md = 2; kv = (float)atof(e + 5); } else if (e && *e) { md = 1; kv = (float)atof(e); }\n'
    '    if (!(kv >= 0.25f && kv <= 8.0f)) { kv = 1.0f; md = 0; } }\n'
    '  if (md == 2) return ((mach_absolute_time() / 24000000ull) & 1) ? kv : 1.0f; return md ? kv : 1.0f; }\n'
    'static float s7115_h(uint8_t* rdram, recomp_context* ctx, float x, float z) {\n'
    '  recomp_context sv = *ctx; uint32_t ns = (uint32_t)ctx->r29 - 0x80; float h;\n'
    '  ctx->r29 = (int64_t)(int32_t)ns; ctx->f12.fl = x; ctx->f14.fl = z; ctx->r7 = (int64_t)(int32_t)(ns + 0x10);\n'
    '  wrapAngleToCyclicRange(rdram, ctx); h = ctx->f0.fl; *ctx = sv; return h; }\n'
    'static void s7115_lift(uint8_t* rdram, recomp_context* ctx, int on) {\n'
    '  uint32_t s1 = (uint32_t)ctx->r17, sp0 = (uint32_t)ctx->r29; float o[4][3], c[3], p[3], r[3], u[3], f[3], n, need = 0.0f, lift = 0.0f;\n'
    '  float f20 = s7103_f20, nr = 0.5f * f20; if (!(f20 > 0.01f && f20 < 10.0f)) return;\n'
    '  for (int i = 0; i < 4; i++) { s7102_v3(rdram, sp0 + 0x48 + 12 * i, c); float l = 0;\n'
    '    for (int q = 0; q < 3; q++) { o[i][q] = c[q] - s7103_p0[q]; l += o[i][q] * o[i][q]; }\n'
    '    l = sqrtf(l); if (!(l > 0.5f * f20 && l < 2.0f * f20)) return; }  /* corner loop skipped: no frame */\n'
    '  for (int q = 0; q < 3; q++) { r[q] = o[1][q] - o[0][q]; u[q] = o[2][q] - o[1][q]; }\n'
    '  n = sqrtf(r[0] * r[0] + r[1] * r[1] + r[2] * r[2]); if (!(n > 1e-6f)) return; for (int q = 0; q < 3; q++) r[q] /= n;\n'
    '  n = sqrtf(u[0] * u[0] + u[1] * u[1] + u[2] * u[2]); if (!(n > 1e-6f)) return; for (int q = 0; q < 3; q++) u[q] /= n;\n'
    '  f[0] = r[1] * u[2] - r[2] * u[1]; f[1] = r[2] * u[0] - r[0] * u[2]; f[2] = r[0] * u[1] - r[1] * u[0];\n'
    '  if (f[0] * o[0][0] + f[1] * o[0][1] + f[2] * o[0][2] < 0) for (int q = 0; q < 3; q++) f[q] = -f[q];\n'
    '  s7102_v3(rdram, s1 + 0x10, p);\n'
    '  { float h = s7115_h(rdram, ctx, p[0], p[2]); if (p[1] - h > need) need = p[1] - h; }\n'
    '  float k = s7115_k(); int smax = (int)ceilf(4.0f * k - 1e-4f); if (smax < 1) smax = 1;\n'
    '  for (int gx = -4; gx <= 4; gx++) for (int gy = -2; gy <= 2; gy++) for (int s = 1; s <= smax; s++) {\n'
    '    float t = 0.25f * s * nr, q3[3];\n'
    '    for (int q = 0; q < 3; q++) q3[q] = p[q] + t * (f[q] + 0.25f * gx * 1.368f * r[q] + 0.5f * gy * 0.637f * u[q]);\n'
    '    float h = s7115_h(rdram, ctx, q3[0], q3[2]); if (q3[1] - h > need) need = q3[1] - h; }\n'
    '  if (on && need > 0.0f) { lift = need + 0.05f * nr; float y = p[1] - lift; uint32_t w; memcpy(&w, &y, 4);\n'
    '    MEM_W(0x14, (int64_t)(int32_t)s1) = w; MEM_W(0x50, (int64_t)(int32_t)s1) = w; }\n'
    '  if (s7101_cf) fprintf(s7101_cf, "nl m=%llu cam=%08X on=%d k=%.3g need=%.6g lift=%.6g\\n", s7102_m(), s1, on, (double)k, (double)need, (double)lift); }\n'
)
OLD_PRE = (pathlib.Path(__file__).with_name("s7115_nearlift_oldpre.txt")).read_text()  # s7115 PRE, for in-place upgrade
A_END = "L_8004D050:\n    if (s7103_in) { int fx = s7103_fix_on();"
L_END = ("L_8004D050:\n    if (s7103_in) { int on = s7115_on(); if (on || s7101_cf) s7115_lift(rdram, ctx, on); } /* " + MARK + " */\n"
         "    if (s7103_in) { int fx = s7103_fix_on();")


def apply(text):
    if MARK in text and "s7115_k(" not in text and OLD_PRE in text:  # s7118: upgrade a pre-NEARK patched tree in place
        return text.replace(OLD_PRE, PRE, 1), 1
    if MARK in text or text.count(FN) != 1:
        return text, 0
    s = text.index(FN); e = text.index("RECOMP_FUNC", s + len(FN)); body = text[s:e]
    if body.count(A_END) != 1 or "static float s7103_p0[3]" not in text[:s] or "s7102_v3(" not in text[:s]:
        print("anchor miss", body.count(A_END)); return text, 0
    body = body.replace(A_END, L_END, 1)
    return text[:s] + PRE + body + text[e:], 1


if __name__ == "__main__":
    p = BASE / "funcs_10.c"
    t, n = apply(p.read_text(errors="surrogateescape"))
    if n:
        p.write_text(t, errors="surrogateescape")
    print(f"funcs_10.c s7115 nearlift x{n}")
