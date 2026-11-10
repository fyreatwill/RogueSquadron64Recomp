#!/usr/bin/env python3
"""s7103 fps60-wall-camera: exit-state residual test of the flight camera near-plane push-out + y-clamp inputs + fix arm.

applyPlayerVehicleStateUpdate 0x8004CD00 (funcs_10.c): the corner loop pushes pos (s1+0x10) out of the terrain one corner at a
time, each against the corner points built BEFORE the loop (absolute sp+0x48/0x54/0x60/0x6C, never moved with pos), then a y
clamp (0x8004CFDC..0x8004D04C: h = 0x80067D90(x=+0x4C, z=+0x54, out sp+0x78); d = f0(0x8001CF2C) - +0x50; if d < +0xB8 then
y = out.y - +0xB8) may move y. Nothing re-tests the corners after the later pushes or after the clamp.

At the function exit this patch re-tests all 4 corners as offsets of the loop-start pos (corner_i - p0) from the FINAL pos
(scratch sampleTerrainAtNpcPosition calls on a frame below sp; the callee writes only its own stack and the scratch record):
  rx m= cam= fx=<arm on> r=<residual mask before fix> f=<mask after fix> np=<fix passes> h= d= mg= yc=<clamp taken, -1 not reached>
     o=<clamp out point> p0=<loop-start pos> pos=<final pos after fix>
Written into the ROGUESQ_S7101_CHASE file (s7101_cf), just before the s7102 pe line.
ROGUESQ_S7103_CAMFIX=1|tog (tog: on during odd 30 s wall-clock halves): while any corner is inside (up to 4 passes), push
pos = hit - f20 * unit(offset) exactly as the loop does, and copy pos to the +0x4C matrix copy. Default off = retail.
Idempotent; listed in fixup_game_funcs_vendored.py after apply_s7102_pushlog.py (needs its anchors and helpers)."""
import pathlib
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7103 camfix"
FN = "RECOMP_FUNC void applyPlayerVehicleStateUpdate(uint8_t* rdram, recomp_context* ctx) {\n"
S7102_PRE_END = "static unsigned long long s7102_m(void) {"
PRE = (
    '/* ' + MARK + ' state */\n'
    'static int s7103_in, s7103_yc; static float s7103_p0[3], s7103_f20, s7103_h, s7103_d, s7103_mg;\n'
    'static int s7103_fix_on(void) { static int md = -1; static uint64_t t0; extern uint64_t mach_absolute_time(void);\n'
    '  if (md < 0) { const char* e = getenv("ROGUESQ_S7103_CAMFIX"); md = !e || !*e || *e == \'0\' ? 0 : (!strcmp(e, "tog") ? 2 : 1); t0 = mach_absolute_time(); }\n'
    '  if (md < 2) return md; return (int)(((mach_absolute_time() - t0) / (30ull * 24000000ull)) & 1); }\n'
    'static int s7103_ray(uint8_t* rdram, recomp_context* ctx, uint32_t s1, const float* d, float* hp) {\n'
    '  recomp_context sv = *ctx; uint32_t ns = (uint32_t)ctx->r29 - 0x80; int h;\n'
    '  for (int q = 0; q < 3; q++) { uint32_t u; memcpy(&u, &d[q], 4); MEM_W(0x40 + 4 * q, (int64_t)(int32_t)ns) = u; }\n'
    '  ctx->r29 = (int64_t)(int32_t)ns; ctx->r4 = (int64_t)(int32_t)(s1 + 0x10); ctx->r5 = (int64_t)(int32_t)(ns + 0x40);\n'
    '  ctx->r6 = (int64_t)(int32_t)0x80138058u; ctx->r7 = (int64_t)(int32_t)(ns + 0x10);\n'
    '  sampleTerrainAtNpcPosition(rdram, ctx); h = (int)ctx->r2; for (int q = 0; q < 3; q++) { uint32_t u = (uint32_t)MEM_W(0x10 + 4 * q, (int64_t)(int32_t)ns); memcpy(&hp[q], &u, 4); }\n'
    '  *ctx = sv; return h != 0; }\n'
    'static int s7103_mask(uint8_t* rdram, recomp_context* ctx, uint32_t s1, float off[4][3], int push) {\n'
    '  int m = 0; for (int i = 0; i < 4; i++) { float p[3], d[3], hp[3]; s7102_v3(rdram, s1 + 0x10, p); (void)p;\n'
    '    for (int q = 0; q < 3; q++) d[q] = off[i][q];\n'
    '    if (!s7103_ray(rdram, ctx, s1, d, hp)) continue; m |= 1 << i; if (!push) continue;\n'
    '    float n = sqrtf(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]); if (!(n > 1e-6f)) continue;\n'
    '    for (int q = 0; q < 3; q++) { float v = hp[q] - s7103_f20 * d[q] / n; uint32_t u; memcpy(&u, &v, 4);\n'
    '      MEM_W(0x10 + 4 * q, (int64_t)(int32_t)s1) = u; MEM_W(0x4C + 4 * q, (int64_t)(int32_t)s1) = u; } }\n'
    '  return m; }\n'
)
A_INIT = "    s7102_c4 = s7102_cam4_on(); /* PATCH: s7102 pushlog */\n"
L_INIT = A_INIT + ("    s7103_in = 1; s7103_yc = -1; s7103_h = s7103_d = s7103_mg = __builtin_nanf(\"\"); s7102_v3(rdram, (uint32_t)ctx->r17 + 0x10, s7103_p0); /* " + MARK + " */\n")
A_BOT = "    ctx->r2 = SIGNED(ctx->r20) < (s7102_c4 ? 0X4 : 0X3) ? 1 : 0;\n"
L_BOT = "    s7103_f20 = ctx->f20.fl; /* " + MARK + " */\n" + A_BOT
A_H = "    after_10:\n"
L_H = A_H + "    s7103_h = ctx->f0.fl; /* " + MARK + " */\n"
A_C = "    c1cs = ctx->f20.fl < ctx->f2.fl;\n"
L_C = A_C + "    s7103_d = ctx->f20.fl; s7103_mg = ctx->f2.fl; s7103_yc = c1cs; /* " + MARK + " */\n"
A_END = "L_8004D050:\n    if (s7101_cf) { float p[3]; s7102_v3(rdram, (uint32_t)ctx->r17 + 0x10, p); /* PATCH: s7102 pushlog */\n"
L_END = (
    "L_8004D050:\n"
    "    if (s7103_in) { int fx = s7103_fix_on(); s7103_in = 0; /* " + MARK + " */\n"
    "      if (s7101_cf || fx) { uint32_t s1 = (uint32_t)ctx->r17, sp0 = (uint32_t)ctx->r29; float off[4][3], c[3], o[3], p[3]; int r, f, np = 0;\n"
    "        for (int i = 0; i < 4; i++) { s7102_v3(rdram, sp0 + 0x48 + 12 * i, c); for (int q = 0; q < 3; q++) off[i][q] = c[q] - s7103_p0[q]; }\n"
    "        r = s7103_mask(rdram, ctx, s1, off, fx); f = r;\n"
    "        while (fx && f && np < 4) { np++; f = s7103_mask(rdram, ctx, s1, off, np < 4); }\n"
    "        if (s7101_cf) { s7102_v3(rdram, sp0 + 0x78, o); s7102_v3(rdram, s1 + 0x10, p);\n"
    "          fprintf(s7101_cf, \"rx m=%llu cam=%08X fx=%d r=%d f=%d np=%d h=%.6g d=%.6g mg=%.6g yc=%d o=%.6g,%.6g,%.6g p0=%.6g,%.6g,%.6g pos=%.6g,%.6g,%.6g\\n\",\n"
    "            s7102_m(), s1, fx, r, f, np, (double)s7103_h, (double)s7103_d, (double)s7103_mg, s7103_yc, o[0], o[1], o[2],\n"
    "            s7103_p0[0], s7103_p0[1], s7103_p0[2], p[0], p[1], p[2]); } } }\n"
    "    if (s7101_cf) { float p[3]; s7102_v3(rdram, (uint32_t)ctx->r17 + 0x10, p); /* PATCH: s7102 pushlog */\n"
)
PAIRS = [(A_INIT, L_INIT), (A_BOT, L_BOT), (A_H, L_H), (A_C, L_C), (A_END, L_END)]


def apply(text):
    if MARK in text or text.count(FN) != 1 or text.count(S7102_PRE_END) != 1:
        return text, 0
    s = text.index(FN); e = text.index("RECOMP_FUNC", s + len(FN)); body = text[s:e]
    for a, _ in PAIRS:
        if body.count(a) != 1:
            print("anchor miss:", a.splitlines()[0][:70], body.count(a)); return text, 0
    for a, l in PAIRS:
        body = body.replace(a, l, 1)
    # helpers need s7102_v3 (defined in the s7102 PRE block, which sits right before the function)
    return text[:s] + PRE + body + text[e:], 1


if __name__ == "__main__":
    p = BASE / "funcs_10.c"
    t, n = apply(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_10.c s7103 camfix x{n}")
