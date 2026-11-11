#!/usr/bin/env python3
"""s7108 fps60-wall-nearclip: flight camera near-plane push-out corner width vs the real projection, + widening arm.

applyPlayerVehicleStateUpdate 0x8004CD00 builds its corner vector from the camera struct s2 = 0x80138D18 + i*0x144
(s2+0x18 = cam+0x10 viewport w, s2+0x1C = cam+0x14 h, s2+0x28 = cam+0x20 fovy, s2+0x2C = cam+0x24 near):
  x = w*0.5*240/h, y = 120, z = 120/tan((fovy+2)/2 deg), all scaled by f20 = 2*near   (constants 0x8003A8D0..F0)
so the corner half-tan is (w/h)*tan((fovy+2)/2) horizontally and tan((fovy+2)/2) vertically. setupCameraMatrices 0x80016D10
hands guPerspective aspect = (w/h)*(vs_w/vi_w)*k(0x8011A840) * ROGUESQ_ASPECT_SCALE (s6104), fovy = cam+0x20, near = 256*cam+0x24.
This patch records the final guPerspective args per camera struct (just before the call) and, at the push-out corner store
(0x8004CEA4, x), prints once per 600 calls:
  [s7108] s2= cam= w= h= fov= asp= near= pnear= hx= px= vy= pv= k= on=     (hx/px: corner vs projection horizontal half-tan,
                                                                             vy/pv: vertical; k = px/hx)
ROGUESQ_S7108_CAMWIDE=1|tog: scale the corner x by max(1, px/hx*tan((fovy+2)/2)/tan(fovy/2)) so the corners cover the
projection's horizontal extent with the retail 2-degree margin. tog: on in odd absolute mach seconds (mach/24e6 & 1), so any
offline log with mach stamps splits by state with no t0. Default off = retail. Idempotent."""
import pathlib
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7108 camwide"

F4_ANCHOR = "    guPerspective(rdram, ctx);\n        goto after_0;\n"
F4_FN = "RECOMP_FUNC void setupCameraMatrices(uint8_t* rdram, recomp_context* ctx) {\n"
F4_PRE = (
    "/* " + MARK + " projection record */\n"
    "uint32_t rs64_s7108_cam[8]; float rs64_s7108_fov[8], rs64_s7108_asp[8], rs64_s7108_near[8]; int rs64_s7108_n;\n"
)
F4_NEW = (
    "    { /* " + MARK + " */ uint32_t c = (uint32_t)ctx->r17; int i; union { uint32_t u; float f; } a, f, n;\n"
    "      a.u = (uint32_t)ctx->r7; f.u = (uint32_t)ctx->r6; n.u = MEM_W(0X10, ctx->r29);\n"
    "      for (i = 0; i < rs64_s7108_n && rs64_s7108_cam[i] != c; i++) {}\n"
    "      if (i == rs64_s7108_n && i < 8) rs64_s7108_cam[rs64_s7108_n++] = c;\n"
    "      if (i < 8) { rs64_s7108_fov[i] = f.f; rs64_s7108_asp[i] = a.f; rs64_s7108_near[i] = n.f; } }\n"
) + F4_ANCHOR

F10_FN = "RECOMP_FUNC void applyPlayerVehicleStateUpdate(uint8_t* rdram, recomp_context* ctx) {\n"
F10_PRE = (
    "/* " + MARK + " state */\n"
    "extern uint32_t rs64_s7108_cam[8]; extern float rs64_s7108_fov[8], rs64_s7108_asp[8], rs64_s7108_near[8]; extern int rs64_s7108_n;\n"
    "static uint32_t s7108_s2;\n"
    "static int s7108_on(void) { static int md = -1; extern uint64_t mach_absolute_time(void);\n"
    "  if (md < 0) { const char* e = getenv(\"ROGUESQ_S7108_CAMWIDE\"); md = !e || !*e || *e == '0' ? 0 : (!strcmp(e, \"tog\") ? 2 : 1);\n"
    "    if (md) fprintf(stderr, \"[s7108] camwide mode %d\\n\", md); }\n"
    "  if (md < 2) return md; return (int)((mach_absolute_time() / 24000000ull) & 1); }\n"
    "static float s7108_x(uint8_t* rdram, float x) { static unsigned nc; int on = s7108_on(), i, j = -1; uint32_t s2 = s7108_s2;\n"
    "  int w = (int32_t)MEM_W(0X18, (int64_t)(int32_t)s2), h = (int32_t)MEM_W(0X1C, (int64_t)(int32_t)s2); union { uint32_t u; float f; } fv, nr;\n"
    "  fv.u = MEM_W(0X28, (int64_t)(int32_t)s2); nr.u = MEM_W(0X2C, (int64_t)(int32_t)s2);\n"
    "  for (i = 0; i < rs64_s7108_n; i++) if (rs64_s7108_cam[i] == s2 + 8) j = i;\n"
    "  if (j < 0 || h <= 0) { if ((nc++ % 600) == 0) fprintf(stderr, \"[s7108] s2=%08X no projection record (n=%d)\\n\", s2, rs64_s7108_n); return x; }\n"
    "  double d2r = 3.14159265358979 / 360.0, tm = __builtin_tan((fv.f + 2.0) * d2r), tp = __builtin_tan(rs64_s7108_fov[j] * d2r);\n"
    "  double hx = (double)w / h * tm, px = rs64_s7108_asp[j] * tp, k = px / hx * tm / tp; float r = x;\n"
    "  if (on && k > 1.0) r = (float)(x * k);\n"
    "  if ((nc++ % 600) == 0) fprintf(stderr, \"[s7108] s2=%08X cam=%08X w=%d h=%d fov=%.4g pfov=%.4g asp=%.5g near=%.5g pnear=%.5g hx=%.5g px=%.5g vy=%.5g pv=%.5g k=%.5g on=%d\\n\",\n"
    "    s2, rs64_s7108_cam[j], w, h, (double)fv.f, (double)rs64_s7108_fov[j], (double)rs64_s7108_asp[j], (double)nr.f * 256.0, (double)rs64_s7108_near[j],\n"
    "    hx, px, tm, tp, k, on);\n"
    "  return r; }\n"
)
F10_A1 = "    { MEM_W(0X40, ctx->r29) = ctx->f2.u32l; RS64_S5798_ST(0x8004CE58u, 0X40, ctx->r29, 4); }\n"
F10_L1 = "    s7108_s2 = (uint32_t)ctx->r18; /* " + MARK + " */\n" + F10_A1
F10_A2 = "    { MEM_W(0X38, ctx->r29) = ctx->f4.u32l; RS64_S5798_ST(0x8004CEA4u, 0X38, ctx->r29, 4); }\n"
F10_L2 = "    ctx->f4.fl = s7108_x(rdram, ctx->f4.fl); /* " + MARK + " */\n" + F10_A2


def apply4(text):
    if MARK in text or text.count(F4_FN) != 1:
        return text, 0
    s = text.index(F4_FN); e = text.index("RECOMP_FUNC", s + len(F4_FN)); body = text[s:e]
    if body.count(F4_ANCHOR) != 1:
        print("s7108 f4 anchor miss", body.count(F4_ANCHOR)); return text, 0
    return text[:s] + F4_PRE + body.replace(F4_ANCHOR, F4_NEW, 1) + text[e:], 1


def apply10(text):
    if MARK in text or text.count(F10_FN) != 1:
        return text, 0
    s = text.index(F10_FN); e = text.index("RECOMP_FUNC", s + len(F10_FN)); body = text[s:e]
    for a in (F10_A1, F10_A2):
        if body.count(a) != 1:
            print("s7108 f10 anchor miss", a[:60], body.count(a)); return text, 0
    body = body.replace(F10_A1, F10_L1, 1).replace(F10_A2, F10_L2, 1)
    return text[:s] + F10_PRE + body + text[e:], 1


if __name__ == "__main__":
    tot = 0
    for fn, f in (("funcs_4.c", apply4), ("funcs_10.c", apply10)):
        p = BASE / fn; t, n = f(p.read_text())
        if n:
            p.write_text(t)
        tot += n; print(f"{fn} s7108 camwide x{n}")
