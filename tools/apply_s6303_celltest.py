"""s6303 G3c(a): log the per-cell r^2 visibility test in buildGridCellMeshForFace.

At 0x800434E4 the cell's squared distance (0x8($s0)) is compared with the
terrain radius^2 (0x8009DEB4); failing cells have their neighbour link
severed (grid truncation). Opt-in via ROGUESQ_G3C_CELLTEST=1; normal runs are
unchanged. Survives regeneration through the vendored fixup.
"""

import pathlib

BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CMP = '    c1cs = ctx->f2.fl < ctx->f0.fl;\n'
ANCHOR = '    c1cs = ctx->f2.fl < ctx->f0.fl;\n    // 0x800434E8: nop\n'


def apply9(text):
    n = 0
    i = text.find("    // 0x800434E4: c.lt.s")
    if i < 0:
        return text, 0
    j = text.find(CMP, i)
    if j < 0 or j - i > 400:
        raise RuntimeError("s6303 anchor not found")
    j += len(CMP)
    if "PATCH: s6303 celltest" not in text[i:j + 1200]:
        probe = (
            '    { /* PATCH: s6303 celltest */ static int en6303 = -1; static unsigned n6303 = 0;\n'
            '      if (en6303 < 0) { const char* e = getenv("ROGUESQ_G3C_CELLTEST"); en6303 = (e && *e && *e != \'0\') ? 1 : 0; }\n'
            '      if (en6303 && (n6303 < 40000u || (n6303 % 20u) == 0u)) {\n'
            '        fprintf(stderr, "[celltest] n=%u cell=0x%08X d2=%g r2=%g pass=%d \\n", n6303, (unsigned)ctx->r16, ctx->f2.fl, ctx->f0.fl, (int)c1cs);\n'
            '      }\n'
            '      n6303++; }\n'
        )
        text = text[:j] + probe + text[j:]
        n += 1
    k = text.find("    c1cs = ctx->f2.fl < ctx->f0.fl;\n", i) + len("    c1cs = ctx->f2.fl < ctx->f0.fl;\n")
    if "PATCH: s6306 edgedrop" not in text[i:k + 1500]:
        drop = (
            '    { /* PATCH: s6306 edgedrop */ static double ed6306 = -1.0; if (ed6306 < 0.0) { const char* e = getenv("ROGUESQ_EDGE_DROP_D2"); ed6306 = (e && *e) ? atof(e) : 0.0; if (ed6306 > 0.0) fprintf(stderr, "[g3c] edge drop d2>%g\\n", ed6306); }\n'
            '      if (ed6306 > 0.0 && (double)ctx->f2.fl > ed6306) c1cs = 0; }\n'
        )
        text = text[:k] + drop + text[k:]
        n += 1
    return text, n


if __name__ == "__main__":
    p = BASE / "funcs_9.c"
    t = p.read_text()
    t2, n = apply9(t)
    if n:
        p.write_text(t2)
    print(f"funcs_9.c live patched x{n}")
