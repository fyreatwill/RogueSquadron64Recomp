"""s6311 G3c(a): hook the epilogue of the terrain point-light RGB accumulator 0x8004B644.

All paths of the function converge on L_8004B910 (a0 = output RGB bytes, the
caller's world-position floats sit at 0x48/0x4C/0x50($sp) in the callee frame).
Opt-in env knobs (normal runs unchanged):
  ROGUESQ_EDGE_FADE_TEST=<s>  multiply the three clamped bytes by s (positive control)
  ROGUESQ_G3C_POSLOG=1        log a0 and the x/y/z floats (first 4000 calls, then 1/50)
Survives regeneration through the vendored fixup.
"""

import pathlib

BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
LABEL = "L_8004B910:\n"


def apply10(text):
    i = text.find(LABEL)
    if i < 0:
        return text, 0
    if "PATCH: s6311 edgefade" in text[i:i + 2500]:
        return text, 0
    j = i + len(LABEL)
    code = (
        '    { /* PATCH: s6311 edgefade */ static int en6311 = -1; static double sc6311 = 1.0; static unsigned n6311 = 0;\n'
        '      if (en6311 < 0) { const char* e = getenv("ROGUESQ_EDGE_FADE_TEST"); const char* l = getenv("ROGUESQ_G3C_POSLOG");\n'
        '        en6311 = 0; if (e && *e) { sc6311 = atof(e); en6311 |= 1; } if (l && *l && *l != \'0\') en6311 |= 2; }\n'
        '      if (en6311) {\n'
        '        if ((en6311 & 2) && (n6311 < 4000u || (n6311 % 50u) == 0u)) {\n'
        '          uint32_t xi = (uint32_t)MEM_W(0X48, ctx->r29), yi = (uint32_t)MEM_W(0X4C, ctx->r29), zi = (uint32_t)MEM_W(0X50, ctx->r29);\n'
        '          float xf, yf, zf; memcpy(&xf, &xi, 4); memcpy(&yf, &yi, 4); memcpy(&zf, &zi, 4);\n'
        '          fprintf(stderr, "[edgepos] n=%u a0=0x%08X rgb=%u,%u,%u pos=%g,%g,%g\\n", n6311, (unsigned)ctx->r4,\n'
        '            (unsigned)(uint8_t)MEM_B(0X0, ctx->r4), (unsigned)(uint8_t)MEM_B(0X1, ctx->r4), (unsigned)(uint8_t)MEM_B(0X2, ctx->r4), xf, yf, zf);\n'
        '        }\n'
        '        if (en6311 & 1) { for (int k6311 = 0; k6311 < 3; k6311++) { double v6311 = (double)(uint8_t)MEM_B(k6311, ctx->r4) * sc6311; if (v6311 > 255.0) v6311 = 255.0; if (v6311 < 0.0) v6311 = 0.0; MEM_B(k6311, ctx->r4) = (int8_t)(uint8_t)v6311; } }\n'
        '        n6311++; }\n'
        '    }\n'
    )
    return text[:j] + code + text[j:], 1


LABEL2 = "L_8004AA74:\n"


def apply10b(text):
    """s6314: sibling accumulator 0x8004A6C0 (reached via 0x8004AA94) also writes lit RGB to a0."""
    i = text.find(LABEL2)
    if i < 0 or "PATCH: s6314 edgefade2" in text[i:i + 1200]:
        return text, 0
    j = i + len(LABEL2)
    code = (
        '    { /* PATCH: s6314 edgefade2 */ static int en6314 = -1; static double sc6314 = 1.0; static unsigned n6314 = 0;\n'
        '      if (en6314 < 0) { const char* e = getenv("ROGUESQ_EDGE_FADE_TEST2"); en6314 = 0; if (e && *e) { sc6314 = atof(e); en6314 = 1; } }\n'
        '      if (en6314) { n6314++; if ((n6314 & 0xFFFFu) == 1u) fprintf(stderr, "[edgefade2] calls=%u a0=0x%08X\\n", n6314, (unsigned)ctx->r4);\n'
        '        for (int k = 0; k < 3; k++) { double v = (double)(uint8_t)MEM_B(k, ctx->r4) * sc6314; if (v > 255.0) v = 255.0; if (v < 0.0) v = 0.0; MEM_B(k, ctx->r4) = (int8_t)(uint8_t)v; } }\n'
        '    }\n'
    )
    return text[:j] + code + text[j:], 1


def apply10c(text):
    """s6315: ROGUESQ_EDGE_FADE=start,end[,r,g,b] distance fade of the lit RGB written by 0x8004A6C0.
    a1 (ctx->r5) = grid-unit x,y,z floats; centre = player record 0x80137DBC floats [1],[3] * ROGUESQ_EDGE_GRIDSCALE (default 0.5).
    ROGUESQ_EDGE_FADE_LOG=1 logs grid pos, player/camera floats and distance (calibration)."""
    i = text.find(LABEL2)
    if i < 0:
        return text, 0
    j = i + len(LABEL2)
    # insert after the s6314 block (ends at its closing brace line)
    k = text.find("    }\n", j)
    if k < 0 or "PATCH: s6315 edgefade3" in text[j:j + 4000]:
        return text, 0
    k += len("    }\n")
    code = (
        '    { /* PATCH: s6315 edgefade3 */ static int en6315 = -1; static double st6315 = 0, en_6315 = 1, hz6315[3] = {200,215,235}, gs6315 = 0.5; static int lg6315 = 0; static unsigned n6315 = 0;\n'
        '      if (en6315 < 0) { const char* e = getenv("ROGUESQ_EDGE_FADE"); en6315 = 0; lg6315 = (getenv("ROGUESQ_EDGE_FADE_LOG") != NULL);\n'
        '        const char* g = getenv("ROGUESQ_EDGE_GRIDSCALE"); if (g && *g) gs6315 = atof(g);\n'
        '        if (e && *e) { double a = 0, b = 1, r = 200, gg = 215, bb = 235; int c = sscanf(e, "%lf,%lf,%lf,%lf,%lf", &a, &b, &r, &gg, &bb); if (c >= 2) { st6315 = a; en_6315 = b; if (c >= 5) { hz6315[0] = r; hz6315[1] = gg; hz6315[2] = bb; } en6315 = 1; } } }\n'
        '      if (en6315 || lg6315) { uint32_t pb = 0x80137DBCu; uint32_t pxi = (uint32_t)MEM_W(0X4, pb), pzi = (uint32_t)MEM_W(0XC, pb), gx = (uint32_t)MEM_W(0X0, ctx->r5), gz = (uint32_t)MEM_W(0X8, ctx->r5);\n'
        '        float pxf, pzf, gxf, gzf; memcpy(&pxf, &pxi, 4); memcpy(&pzf, &pzi, 4); memcpy(&gxf, &gx, 4); memcpy(&gzf, &gz, 4);\n'
        '        double dx = gxf - pxf * gs6315, dz = gzf - pzf * gs6315, d = sqrt(dx * dx + dz * dz);\n'
        '        double f = 0.0; if (en6315) { f = (d - st6315) / (en_6315 - st6315); if (f < 0) f = 0; if (f > 1) f = 1; f = f * f * (3.0 - 2.0 * f); }\n'
        '        n6315++; if (lg6315 && ((n6315 < 600u) || (n6315 % 4001u) == 0u)) fprintf(stderr, "[edgefade3] n=%u g=%g,%g pl=%g,%g d=%g f=%g\\n", n6315, gxf, gzf, pxf, pzf, d, f);\n'
        '        if (f > 0.0) for (int q = 0; q < 3; q++) { double v = (double)(uint8_t)MEM_B(q, ctx->r4); v = v + (hz6315[q] - v) * f; if (v > 255.0) v = 255.0; if (v < 0.0) v = 0.0; MEM_B(q, ctx->r4) = (int8_t)(uint8_t)v; } }\n'
        '    }\n'
    )
    return text[:k] + code + text[k:], 1


if __name__ == "__main__":
    p = BASE / "funcs_10.c"
    t = p.read_text()
    t2, n = apply10(t)
    t2, n2 = apply10b(t2)
    n += n2
    t2, n3 = apply10c(t2)
    n += n3
    if n:
        p.write_text(t2)
    print(f"funcs_10.c live patched x{n}")
