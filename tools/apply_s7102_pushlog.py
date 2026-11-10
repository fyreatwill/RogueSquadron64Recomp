#!/usr/bin/env python3
"""s7102 fps60-wall-camera: per-corner log of the flight camera near-plane push-out + a 4-corner arm.

applyPlayerVehicleStateUpdate 0x8004CD00 (funcs_10.c) builds 4 near-plane corners at sp+0x48/0x54/0x60/0x6C, then its loop
0x8004CF0C..0x8004CFC0 (s3 = corner base - 0x38, s4 = i, s5 = sp+0x10 hit record, s1 = camera) ray-tests pos -> corner
(sampleTerrainAtNpcPosition, a1 = corner - pos at sp+0x38) for i < 3 only. On a hit: pos = hit - f20 * unit(corner - pos)
(0x800AA350 normalise, 0x800AA3E0 add-scaled), pos copied to +0x4C. After the loop a y floor (0x8004D040..4C) may lift y.

Log lines (into the ROGUESQ_S7101_CHASE file, s7101_cf, so they interleave with the ch/bv lines):
  pu m= cam= i= hit= c=corner pre=pos-before hp=hit-point post=pos-after f20=     (one per tested corner)
  pc m= cam= hit= c=corner3 pos= hp=   corner 3 ray-tested from a scratch call on the final loop pos, only when the
                                       CAM4 arm is off this call (the call writes only its own stack and the scratch record)
  yf m= cam= y=                        y floor taken
  pe m= cam= cam4= pos=                function exit (final pos)
ROGUESQ_S7102_CAM4=1|tog: loop bound 3 -> 4 (tog: on during odd 30 s wall-clock halves). Default off = retail.
Idempotent; listed in fixup_game_funcs_vendored.py after apply_s7101_chaselog.py (needs its s7101_cf)."""
import pathlib
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7102 pushlog"
FN = "RECOMP_FUNC void applyPlayerVehicleStateUpdate(uint8_t* rdram, recomp_context* ctx) {\n"
PRE = (
    '/* ' + MARK + ' state */\n'
    'extern FILE* s7101_cf; static int s7102_c4, s7102_hit; static float s7102_pre[3];\n'
    'static int s7102_cam4_on(void) { static int md = -1; static uint64_t t0; extern uint64_t mach_absolute_time(void);\n'
    '  if (md < 0) { const char* e = getenv("ROGUESQ_S7102_CAM4"); md = !e || !*e || *e == \'0\' ? 0 : (!strcmp(e, "tog") ? 2 : 1); t0 = mach_absolute_time(); }\n'
    '  if (md < 2) return md; return (int)(((mach_absolute_time() - t0) / (30ull * 24000000ull)) & 1); }\n'
    'static void s7102_v3(uint8_t* rdram, uint32_t a, float* o) { for (int q = 0; q < 3; q++) { uint32_t u = (uint32_t)MEM_W(4 * q, (int64_t)(int32_t)a); memcpy(&o[q], &u, 4); } }\n'
    'static unsigned long long s7102_m(void) { extern uint64_t mach_absolute_time(void); return (unsigned long long)mach_absolute_time(); }\n'
)
# loop init (s4 = 0) is at 0x8004CE74; the cam4 decision is taken once per call at the first loop entry (0x8004CF08).
A_INIT = "    ctx->r16 = ADD32(ctx->r17, 0X10);\nL_8004CF0C:\n"
L_INIT = ("    ctx->r16 = ADD32(ctx->r17, 0X10);\n    s7102_c4 = s7102_cam4_on(); /* " + MARK + " */\nL_8004CF0C:\n"
          "    if (s7101_cf) { s7102_v3(rdram, (uint32_t)ctx->r17 + 0x10, s7102_pre); s7102_hit = 0; } /* " + MARK + " */\n")
A_HIT = "    after_7:\n    // 0x8004CF58: beql        $v0, $zero, L_8004CFBC\n"
L_HIT = A_HIT + "    s7102_hit = (int)ctx->r2; /* " + MARK + " */\n"
A_BOT = "L_8004CFBC:\n    // 0x8004CFBC: slti        $v0, $s4, 0x3\n    ctx->r2 = SIGNED(ctx->r20) < 0X3 ? 1 : 0;\n"
L_BOT = (
    "L_8004CFBC:\n"
    "    if (s7101_cf) { float c[3], hp[3], po[3]; uint32_t s1 = (uint32_t)ctx->r17; /* " + MARK + " */\n"
    "      s7102_v3(rdram, (uint32_t)ctx->r19 + 0x38, c); s7102_v3(rdram, (uint32_t)ctx->r21, hp); s7102_v3(rdram, s1 + 0x10, po);\n"
    "      fprintf(s7101_cf, \"pu m=%llu cam=%08X i=%d hit=%d c=%.6g,%.6g,%.6g pre=%.6g,%.6g,%.6g hp=%.6g,%.6g,%.6g post=%.6g,%.6g,%.6g f20=%.6g\\n\",\n"
    "        s7102_m(), s1, (int)ctx->r20 - 1, s7102_hit, c[0], c[1], c[2], s7102_pre[0], s7102_pre[1], s7102_pre[2], hp[0], hp[1], hp[2], po[0], po[1], po[2], (double)ctx->f20.fl); }\n"
    "    ctx->r2 = SIGNED(ctx->r20) < (s7102_c4 ? 0X4 : 0X3) ? 1 : 0;\n"
)
A_AFT = "L_8004CFC8:\n"
L_AFT = (
    "L_8004CFC8:\n"
    "    if (s7101_cf && !s7102_c4) { /* " + MARK + " probe: ray-test corner 3 (sp+0x6C) from the final pos on a scratch frame */\n"
    "      recomp_context sv = *ctx; uint32_t s1 = (uint32_t)ctx->r17, sp0 = (uint32_t)ctx->r29; float c[3], p[3], hp[3]; int h;\n"
    "      s7102_v3(rdram, sp0 + 0x6C, c); s7102_v3(rdram, s1 + 0x10, p);\n"
    "      uint32_t ns = sp0 - 0x80; for (int q = 0; q < 3; q++) { float d = c[q] - p[q]; uint32_t u; memcpy(&u, &d, 4); MEM_W(0x40 + 4 * q, (int64_t)(int32_t)ns) = u; }\n"
    "      ctx->r29 = (int64_t)(int32_t)ns; ctx->r4 = (int64_t)(int32_t)(s1 + 0x10); ctx->r5 = (int64_t)(int32_t)(ns + 0x40);\n"
    "      ctx->r6 = (int64_t)(int32_t)0x80138058u; ctx->r7 = (int64_t)(int32_t)(ns + 0x10);\n"
    "      sampleTerrainAtNpcPosition(rdram, ctx); h = (int)ctx->r2; s7102_v3(rdram, ns + 0x10, hp); *ctx = sv;\n"
    "      fprintf(s7101_cf, \"pc m=%llu cam=%08X hit=%d c=%.6g,%.6g,%.6g pos=%.6g,%.6g,%.6g hp=%.6g,%.6g,%.6g\\n\", s7102_m(), s1, h,\n"
    "        c[0], c[1], c[2], p[0], p[1], p[2], hp[0], hp[1], hp[2]); }\n"
)
A_YF = "    { MEM_W(0X14, ctx->r17) = ctx->f0.u32l; RS64_S5798_ST(0x8004D04Cu, 0X14, ctx->r17, 4); }\n"
L_YF = A_YF + ("    if (s7101_cf) fprintf(s7101_cf, \"yf m=%llu cam=%08X y=%.6g\\n\", s7102_m(), (uint32_t)ctx->r17, (double)ctx->f0.fl); /* " + MARK + " */\n")
A_END = "L_8004D050:\n    // 0x8004D050: lw          $ra, 0xC8($sp)\n"
L_END = ("L_8004D050:\n    if (s7101_cf) { float p[3]; s7102_v3(rdram, (uint32_t)ctx->r17 + 0x10, p); /* " + MARK + " */\n"
         "      fprintf(s7101_cf, \"pe m=%llu cam=%08X cam4=%d pos=%.6g,%.6g,%.6g\\n\", s7102_m(), (uint32_t)ctx->r17, s7102_c4, p[0], p[1], p[2]); }\n"
         "    // 0x8004D050: lw          $ra, 0xC8($sp)\n")
PAIRS = [(A_INIT, L_INIT), (A_HIT, L_HIT), (A_BOT, L_BOT), (A_AFT, L_AFT), (A_YF, L_YF), (A_END, L_END)]


def apply(text):
    if MARK in text or text.count(FN) != 1:
        return text, 0
    s = text.index(FN); e = text.index("RECOMP_FUNC", s + len(FN)); body = text[s:e]
    for a, _ in PAIRS:
        if body.count(a) != 1:
            print("anchor miss:", a.splitlines()[0][:70], body.count(a)); return text, 0
    for a, l in PAIRS:
        body = body.replace(a, l, 1)
    return text[:s] + PRE + body + text[e:], 1


if __name__ == "__main__":
    p = BASE / "funcs_10.c"
    t, n = apply(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_10.c s7102 pushlog x{n}")
