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


if __name__ == "__main__":
    p = BASE / "funcs_10.c"
    t = p.read_text()
    t2, n = apply10(t)
    if n:
        p.write_text(t2)
    print(f"funcs_10.c live patched x{n}")
