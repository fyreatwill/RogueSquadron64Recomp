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
    if "PATCH: s6311 edgefade" in text[i:i + 9000]:
        return text, 0
    j = i + len(LABEL)
    code = (
        '    { /* PATCH: s6311 edgefade */ static int en6311 = -1; static double sc6311 = 1.0; static unsigned n6311 = 0;\n'
        '      if (en6311 < 0) { const char* e = getenv("ROGUESQ_EDGE_FADE_TEST"); const char* l = getenv("ROGUESQ_G3C_POSLOG");\n'
        '        en6311 = 0; if (e && *e) { sc6311 = atof(e); en6311 |= 1; } if (l && *l && *l != \'0\') en6311 |= 2; }\n'
        '      if (en6311) {\n'
        '        if ((en6311 & 2) && (n6311 < 2000u || (n6311 % 7u) == 0u)) {\n'
        '          uint32_t xi = (uint32_t)MEM_W(0X48, ctx->r29), yi = (uint32_t)MEM_W(0X4C, ctx->r29), zi = (uint32_t)MEM_W(0X50, ctx->r29);\n'
        '          float xf, yf, zf; memcpy(&xf, &xi, 4); memcpy(&yf, &yi, 4); memcpy(&zf, &zi, 4);\n'
        '          { uint32_t cp6 = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80138D1Cu); uint32_t cxi = 0, czi = 0; if (cp6 >= 0x80000000u && cp6 < 0x80800000u) { cxi = (uint32_t)MEM_W(0x4C + 0x0, (int64_t)(int32_t)cp6); czi = (uint32_t)MEM_W(0x54, (int64_t)(int32_t)cp6); } float cxf, czf; memcpy(&cxf, &cxi, 4); memcpy(&czf, &czi, 4);\n'
        '          fprintf(stderr, "[edgepos] n=%u a0=0x%08X rgb=%u,%u,%u pos=%g,%g,%g cam=%g,%g\\n", n6311, (unsigned)ctx->r4,\n'
        '            (unsigned)(uint8_t)MEM_B(0X0, ctx->r4), (unsigned)(uint8_t)MEM_B(0X1, ctx->r4), (unsigned)(uint8_t)MEM_B(0X2, ctx->r4), xf, yf, zf, cxf, czf); }\n'
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


EF4_LINE = (
        '        if (lg6315 && ((n6315 < 40u) || (n6315 % 4001u) == 0u)) { uint32_t w0 = (uint32_t)MEM_W(0X0, pb), s3 = (uint32_t)ctx->r19; fprintf(stderr, "[edgefade4] slot=%08X %08X %08X %08X %08X obj=", (unsigned)w0, (unsigned)MEM_W(0X4, pb), (unsigned)MEM_W(0X8, pb), (unsigned)MEM_W(0XC, pb), (unsigned)MEM_W(0X10, pb)); if (w0 >= 0x80000000u && w0 < 0x80800000u) for (int q = 0; q < 12; q++) { uint32_t u = (uint32_t)MEM_W(q * 4, w0); float fv; memcpy(&fv, &u, 4); fprintf(stderr, "%g ", fv); } fprintf(stderr, " s3=%08X cell=%d,%d\\n", (unsigned)s3, (s3 >= 0x80000000u && s3 < 0x80800000u) ? (int)(int16_t)MEM_H(0X18, s3) : -1, (s3 >= 0x80000000u && s3 < 0x80800000u) ? (int)(int16_t)MEM_H(0X1A, s3) : -1); }\n'
)


def apply10d(text):
    """s6316: calibration log [edgefade4] (slot words, *slot floats, cell idx), inserted before n6315++."""
    key = '        n6315++; if (lg6315'
    if 'edgefade4' in text or 'PATCH: s6315 edgefade3' not in text:
        return text, 0
    k = text.find(key)
    if k < 0:
        return text, 0
    return text[:k] + EF4_LINE + text[k:], 1


EF5_LINE = (
    '        if (lg6315 && ((n6315 % 5u) == 0u) && n6315 < 60000u) { fprintf(stderr, "[edgefade5] n=%u cell=%d,%d cam=", n6315, (int)rs64_ef_col, (int)rs64_ef_row); for (int q = 0; q < 32; q++) { uint32_t u = (uint32_t)MEM_W(q * 4, 0x80138D20u); float fv; memcpy(&fv, &u, 4); fprintf(stderr, "%g,", fv); } fprintf(stderr, "pl="); for (int q = 0; q < 12; q++) { uint32_t u = (uint32_t)MEM_W(q * 4, 0x80137DBCu); float fv; memcpy(&fv, &u, 4); fprintf(stderr, "%g,", fv); } fprintf(stderr, "\\n"); }\n'
)


def apply10e(text):
    """s6317: stash cell col,row (a0+0x18/+0x1A) at 0x8004AA94 entry (A6C0 epilogue r19 is not AA94's s3) and log camera struct floats."""
    if 'rs64_ef_col' in text or 'edgefade4' not in text:
        return text, 0
    fn = text.find('RECOMP_FUNC void mapCellGeometryToGridSpace(')
    first = text.find('RECOMP_FUNC')
    anchor = '    ctx->r19 = ADD32(ctx->r4, 0);\n'
    a = text.find(anchor, fn)
    if fn < 0 or a < 0:
        return text, 0
    a += len(anchor)
    text = text[:a] + '    rs64_ef_col = MEM_H(ctx->r19, 0X18); rs64_ef_row = MEM_H(ctx->r19, 0X1A); /* PATCH: s6317 cellstash */\n' + text[a:]
    text = text[:first] + 'static int32_t rs64_ef_col = 0, rs64_ef_row = 0; /* PATCH: s6317 cellstash */\n' + text[first:]
    k = text.find('        n6315++; if (lg6315')
    if k < 0:
        return text, 0
    return text[:k] + EF5_LINE + text[k:], 1


EF6_LINE = (
    '        if (lg6315 && ((n6315 % 5u) == 0u) && n6315 < 60000u) { fprintf(stderr, "[edgefade6] n=%u gl=", n6315); for (int q = 0; q < 3; q++) { uint32_t u = (uint32_t)MEM_W(q * 4, (int64_t)(int32_t)0x80130C10u); float fv; memcpy(&fv, &u, 4); fprintf(stderr, "%g,", fv); } fprintf(stderr, "org="); for (int q = 0; q < 3; q++) { uint32_t u = (uint32_t)MEM_W(0x14 + q * 4, (int64_t)(int32_t)0x80136DC0u); float fv; memcpy(&fv, &u, 4); fprintf(stderr, "%g,", fv); } { uint32_t u = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8003A518u); float fv; memcpy(&fv, &u, 4); fprintf(stderr, "k=%g", fv); } fprintf(stderr, "\\n"); }\n'
)


def apply10f(text):
    """s6323: log the terrain builder's camera-relative grid origin (0x80130C10 = (cam-org)*k, set at 0x80043840..)."""
    if 'edgefade6' in text or 'edgefade5' not in text:
        return text, 0
    k = text.find('        n6315++; if (lg6315')
    if k < 0:
        return text, 0
    return text[:k] + EF6_LINE + text[k:], 1


EF7_CODE = (
    '    { /* PATCH: s6325 radfade */ static int en6325 = -1; static double r0_6325 = 0, r1_6325 = 1, hz6325[3] = {0,0,0}; static unsigned n6325 = 0; static double mx6325 = 0;\n'
    '      if (en6325 < 0) { const char* e = getenv("ROGUESQ_EDGE_FADE_R"); en6325 = 0; if (e && *e) { double a = 0, b = 1, r = 0, g = 0, bb = 0; int c = sscanf(e, "%lf,%lf,%lf,%lf,%lf", &a, &b, &r, &g, &bb); if (c >= 2) { r0_6325 = a; r1_6325 = b; if (c >= 5) { hz6325[0] = r; hz6325[1] = g; hz6325[2] = bb; } en6325 = 1; } } }\n'
    '      if (en6325) { uint32_t cp = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80138D1Cu);\n'
    '        if (cp >= 0x80000000u && cp < 0x80800000u) { uint32_t xi = (uint32_t)MEM_W(0X48, ctx->r29), zi = (uint32_t)MEM_W(0X50, ctx->r29), cxi = (uint32_t)MEM_W(0x4C, (int64_t)(int32_t)cp), czi = (uint32_t)MEM_W(0x54, (int64_t)(int32_t)cp);\n'
    '          float xf, zf, cxf, czf; memcpy(&xf, &xi, 4); memcpy(&zf, &zi, 4); memcpy(&cxf, &cxi, 4); memcpy(&czf, &czi, 4);\n'
    '          double dx = xf - cxf * 0.5, dz = zf - czf * 0.5, d = sqrt(dx * dx + dz * dz), f = (d - r0_6325) / (r1_6325 - r0_6325); if (f < 0) f = 0; if (f > 1) f = 1; f = f * f * (3.0 - 2.0 * f);\n'
    '          if (d > mx6325 && d < 1000.0) mx6325 = d; n6325++; if ((n6325 % 200000u) == 1u) fprintf(stderr, "[radfade] n=%u maxr=%g r=%g f=%g\\n", n6325, mx6325, d, f);\n'
    '          if (f > 0.0) for (int q = 0; q < 3; q++) { double v = (double)(uint8_t)MEM_B(q, ctx->r4); v = v + (hz6325[q] - v) * f; if (v > 255.0) v = 255.0; if (v < 0.0) v = 0.0; MEM_B(q, ctx->r4) = (int8_t)(uint8_t)v; } } }\n'
    '    }\n'
)


def apply10g(text):
    """s6325: ROGUESQ_EDGE_FADE_R=r0,r1[,R,G,B] radius fade (cells, centre cam*0.5) of lit RGB at the 0x8004B910 epilogue; default target black."""
    i = text.find(LABEL)
    if i < 0 or "PATCH: s6325 radfade" in text[i:i + 6000]:
        return text, 0
    j = i + len(LABEL)
    return text[:j] + EF7_CODE + text[j:], 1


EF8_CODE = (
    '    { /* PATCH: s6327 forcered */ static int en6327 = -1; if (en6327 < 0) { const char* e = getenv("ROGUESQ_EDGE_FORCE_RED"); en6327 = (e && *e && *e != \'0\') ? 1 : 0; }\n'
    '      if (en6327) { MEM_B(0, ctx->r4) = (int8_t)0xFF; MEM_B(1, ctx->r4) = 0; MEM_B(2, ctx->r4) = 0; } }\n'
)


def apply10h(text):
    """s6327: ROGUESQ_EDGE_FORCE_RED=1 forces lit RGB to (255,0,0) at the 0x8004B910 epilogue (write-path positive control)."""
    i = text.find(LABEL)
    if i < 0 or "PATCH: s6327 forcered" in text[i:i + 12000]:
        return text, 0
    k = text.find("PATCH: s6325 radfade", i)
    if k < 0:
        return text, 0
    e = text.find("    }\n", text.find("MEM_B(q, ctx->r4)", k))
    e += len("    }\n")
    return text[:e] + EF8_CODE + text[e:], 1


EF9_CODE = (
    '    { /* PATCH: s6328 radfade2 */ static int en6328 = -1, xo6328 = 0x40, zo6328 = 0x48, lg6328 = 0; static double r0_6328 = 0, r1_6328 = 1, hz6328[3] = {0,0,0}; static unsigned n6328 = 0;\n'
    '      if (en6328 < 0) { en6328 = 0; lg6328 = getenv("ROGUESQ_EDGE_FADE_R2_LOG") ? 1 : 0; const char* e = getenv("ROGUESQ_EDGE_FADE_R2"); if (e && *e) { double a = 0, b = 1, r = 0, g = 0, bb = 0; int xo = 0x40, zo = 0x48; int c = sscanf(e, "%lf,%lf,%d,%d,%lf,%lf,%lf", &a, &b, &xo, &zo, &r, &g, &bb); if (c >= 2) { r0_6328 = a; r1_6328 = b; if (c >= 4) { xo6328 = xo; zo6328 = zo; } if (c >= 7) { hz6328[0] = r; hz6328[1] = g; hz6328[2] = bb; } en6328 = 1; } } }\n'
    '      if (en6328 || lg6328) { uint32_t cp = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80138D1Cu); n6328++;\n'
    '        if (cp >= 0x80000000u && cp < 0x80800000u) { float w[12]; for (int q = 0; q < 12; q++) { uint32_t wi = (uint32_t)MEM_W(0x38 + 4 * q, ctx->r29); memcpy(&w[q], &wi, 4); }\n'
    '          uint32_t xi = (uint32_t)MEM_W(xo6328, ctx->r29), zi = (uint32_t)MEM_W(zo6328, ctx->r29), cxi = (uint32_t)MEM_W(0x4C, (int64_t)(int32_t)cp), czi = (uint32_t)MEM_W(0x54, (int64_t)(int32_t)cp);\n'
    '          float xf, zf, cxf, czf; memcpy(&xf, &xi, 4); memcpy(&zf, &zi, 4); memcpy(&cxf, &cxi, 4); memcpy(&czf, &czi, 4);\n'
    '          double dx = xf - cxf * 0.5, dz = zf - czf * 0.5, d = sqrt(dx * dx + dz * dz), f = (d - r0_6328) / (r1_6328 - r0_6328); if (f < 0) f = 0; if (f > 1) f = 1; f = f * f * (3.0 - 2.0 * f);\n'
    '          if (lg6328 && (n6328 < 120u || (n6328 % 20011u) == 0u)) fprintf(stderr, "[radfade2] n=%u d=%g f=%g cam=%g,%g w38..64=%g %g %g %g %g %g %g %g %g %g %g %g\\n", n6328, d, f, cxf, czf, w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8], w[9], w[10], w[11]);\n'
    '          if (en6328 && f > 0.0) for (int q = 0; q < 3; q++) { double v = (double)(uint8_t)MEM_B(q, ctx->r4); v = v + (hz6328[q] - v) * f; if (v > 255.0) v = 255.0; if (v < 0.0) v = 0.0; MEM_B(q, ctx->r4) = (int8_t)(uint8_t)v; } } }\n'
    '    }\n'
)


def apply10i(text):
    """s6328: ROGUESQ_EDGE_FADE_R2=r0,r1[,xoff,zoff[,R,G,B]] radius fade at the proven-live A6C0 AA74 write site (stack-arg float offsets from callee sp); ROGUESQ_EDGE_FADE_R2_LOG=1 dumps 12 stack words."""
    i = text.find(LABEL2)
    if i < 0 or "PATCH: s6328 radfade2" in text[i:i + 3000]:
        return text, 0
    j = i + len(LABEL2)
    return text[:j] + EF9_CODE + text[j:], 1


if __name__ == "__main__":
    p = BASE / "funcs_10.c"
    t = p.read_text()
    t2, n = apply10(t)
    t2, n2 = apply10b(t2)
    n += n2
    t2, n3 = apply10c(t2)
    n += n3
    t2, n4 = apply10d(t2)
    n += n4
    t2, n5 = apply10e(t2)
    n += n5
    t2, n6 = apply10f(t2)
    n += n6
    t2, n7 = apply10g(t2)
    n += n7
    t2, n8 = apply10h(t2)
    n += n8
    t2, n9 = apply10i(t2)
    n += n9
    if n:
        p.write_text(t2)
    print(f"funcs_10.c live patched x{n}")
