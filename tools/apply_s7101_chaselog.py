#!/usr/bin/env python3
"""s7101 fps60-wall-camera: per-tick log of the flight chase-camera step (updatePlayerVehicleByControlMode, mode 3).

Hook at 0x8004D6C8, right after vec3Length(target - pos): f0 = distance, f20 = the dt the chase step will use (the call's
a1, or the old cam+0xA4 on the split branch), s2 = camera object. Logs pos (+0x10..0x18), target (sp+0x20..0x28), dist,
dt, cam+0x94 (stand-off), +0x98 (speed), +0x9C (gain k), +0xA4 (the min-dt field), lim (0x80128EAF), frame counter
0x8011A890 and mach time. Env ROGUESQ_S7101_CHASE=<path>. No store-diag needed. Measurement only.
Positive control: one line per chase tick in flight (~60/s at lim 1). Idempotent; in fixup_game_funcs_vendored.py's list."""
import pathlib
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7101 chaselog"
ANCHOR = "    after_8:\n    // 0x8004D6C8: lui         $at, 0x8004\n"
LINE = (
    '    { /* ' + MARK + ' */ static FILE* f7101 = (FILE*)1;\n'
    '      if (f7101 == (FILE*)1) { const char* e = getenv("ROGUESQ_S7101_CHASE"); f7101 = (e && *e && *e != \'0\') ? fopen(e, "w") : NULL; }\n'
    '      if (f7101) { extern uint64_t mach_absolute_time(void); uint32_t s2 = (uint32_t)ctx->r18, sp = (uint32_t)ctx->r29;\n'
    '        float v[13]; uint32_t u; static const int so[13] = {0x10,0x14,0x18,0x94,0x98,0x9C,0xA4,0x58,0x5C,0x60,0,0,0};\n'
    '        for (int q = 0; q < 10; q++) { u = (uint32_t)MEM_W(so[q], (int64_t)(int32_t)s2); memcpy(&v[q], &u, 4); }\n'
    '        for (int q = 0; q < 3; q++) { u = (uint32_t)MEM_W(0x20 + 4 * q, (int64_t)(int32_t)sp); memcpy(&v[10 + q], &u, 4); }\n'
    '        fprintf(f7101, "ch m=%llu lim=%u fc=%u cam=%08X dist=%.6g dt=%.6g pos=%.6g,%.6g,%.6g tgt=%.6g,%.6g,%.6g d0=%.6g spd=%.6g k=%.6g mindt=%.6g off=%.6g,%.6g,%.6g\\n",\n'
    '          (unsigned long long)mach_absolute_time(), (unsigned)MEM_BU(0, (int64_t)(int32_t)0x80128EAFu), (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8011A890u), s2,\n'
    '          (double)ctx->f0.fl, (double)ctx->f20.fl, v[0], v[1], v[2], v[10], v[11], v[12], v[3], v[4], v[5], v[6], v[7], v[8], v[9]); }\n'
    '      s7101_cf = f7101; { uint32_t s2 = (uint32_t)ctx->r18, sp = (uint32_t)ctx->r29; uint32_t u;\n'
    '        for (int q = 0; q < 3; q++) { u = (uint32_t)MEM_W(0x20 + 4 * q, (int64_t)(int32_t)sp); memcpy(&s7101_t[q], &u, 4);\n'
    '          u = (uint32_t)MEM_W(0x10 + 4 * q, (int64_t)(int32_t)s2); memcpy(&s7101_p[q], &u, 4); }\n'
    '        s7101_dist = ctx->f0.fl; s7101_valid = 1; } }\n'
)


FN = "RECOMP_FUNC void updatePlayerVehicleByControlMode(uint8_t* rdram, recomp_context* ctx) {\n"
PRE = (
    '/* ' + MARK + ' state + s7101 camclamp arm */\n'
    'static float s7101_t[3], s7101_p[3], s7101_dist; static int s7101_valid; FILE* s7101_cf;\n'
    '/* ROGUESQ_S7101_CAMCLAMP=1: if the chase step is longer than the distance to the target, land on the target (no\n'
    '   overshoot). =tog: on during odd 30 s wall-clock halves (same-run A/B). Default off = retail. */\n'
    'static int s7101_clamp_on(void) { static int md = -1; static uint64_t t0; extern uint64_t mach_absolute_time(void);\n'
    '  if (md < 0) { const char* e = getenv("ROGUESQ_S7101_CAMCLAMP"); md = !e || !*e || *e == \'0\' ? 0 : (!strcmp(e, "tog") ? 2 : 1); t0 = mach_absolute_time(); }\n'
    '  if (md < 2) return md; return (int)(((mach_absolute_time() - t0) / (30ull * 24000000ull)) & 1); }\n'
)
ANCHOR2 = "    // 0x8004D7E0: swc1        $f2, 0x50($s2)\n"
LINE2 = (
    '    { /* ' + MARK + ' clamp */ if (s7101_valid) { int on = s7101_clamp_on(); float dx = ctx->f0.fl - s7101_p[0], dy = ctx->f2.fl - s7101_p[1], dz = ctx->f4.fl - s7101_p[2];\n'
    '        float st = sqrtf(dx * dx + dy * dy + dz * dz); int over = st > s7101_dist;\n'
    '        if (on && over) { ctx->f0.fl = s7101_t[0]; ctx->f2.fl = s7101_t[1]; ctx->f4.fl = s7101_t[2];\n'
    '          MEM_W(0x10, ctx->r18) = ctx->f0.u32l; MEM_W(0x14, ctx->r18) = ctx->f2.u32l; MEM_W(0x18, ctx->r18) = ctx->f4.u32l; }\n'
    '        if (s7101_cf) fprintf(s7101_cf, "cl step=%.6g over=%d on=%d\\n", (double)st, over, on); s7101_valid = 0; } }\n'
)


def apply(text):
    if MARK in text:
        return text, 0
    if text.count(ANCHOR) != 1 or text.count(ANCHOR2) != 1 or text.count(FN) != 1:
        return text, 0
    text = text.replace(FN, PRE + FN, 1)
    text = text.replace(ANCHOR, ANCHOR.split("\n")[0] + "\n" + LINE + "    // 0x8004D6C8: lui         $at, 0x8004\n", 1)
    return text.replace(ANCHOR2, LINE2 + ANCHOR2, 1), 1


# s7101 H-order: at buildVisibleTerrainGridAroundCamera entry (funcs_9.c, before the s6321 camlog line) log the camera
# translation the builder is about to read (cam+0x4C..0x54) into the same file, so each builder read is ordered against
# the chase writes by mach time. Opens the file itself if the chase hook has not run yet.
MARK9 = "PATCH: s7101 bvread"
ANCHOR9 = "    { /* PATCH: s6321 camlog */"
LINE9 = (
    '    { /* ' + MARK9 + ' */ extern FILE* s7101_cf; static int en = -1; if (en < 0) { const char* e = getenv("ROGUESQ_S7101_CHASE"); en = (e && *e && *e != \'0\') ? 1 : 0; }\n'
    '      if (en && s7101_cf) { extern uint64_t mach_absolute_time(void); uint32_t cp = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80138D1Cu); float v[3] = {0, 0, 0};\n'
    '        if (cp >= 0x80000000u && cp < 0x80800000u) for (int q = 0; q < 3; q++) { uint32_t u = (uint32_t)MEM_W(0x4C + 4 * q, (int64_t)(int32_t)cp); memcpy(&v[q], &u, 4); }\n'
    '        fprintf(s7101_cf, "bv m=%llu fc=%u cam=%08X rd=%.6g,%.6g,%.6g\\n", (unsigned long long)mach_absolute_time(), (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8011A890u), cp, v[0], v[1], v[2]); } }\n'
)


def apply9(text):
    if MARK9 in text or text.count(ANCHOR9) != 1:
        return text, 0
    return text.replace(ANCHOR9, LINE9 + ANCHOR9, 1), 1


if __name__ == "__main__":
    p = BASE / "funcs_10.c"
    t, n = apply(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_10.c s7101 chaselog x{n}")
    p = BASE / "funcs_9.c"
    t, n = apply9(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_9.c s7101 bvread x{n}")
