"""s6027 G1c: ROGUESQ_DD_CELLMUL=<m> scales the incoming cell count ($a0) of allocAndInitGridCellArray (0x80047E50, funcs_10.c)
BEFORE rs_malloc latches it (s6026: post-load rewrites of the grid words were void). Default unset = retail. Idempotent; mirrored into fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
HDR = '''/* PATCH: s6027 cellmul */
static double rs6027_mul(void) { static double m = -1; if (m < 0) { const char* e = getenv("ROGUESQ_DD_CELLMUL"); m = (e && *e) ? atof(e) : 0.0; } return m; }
'''
OLD = "    // 0x80047E58: addu        $s1, $a0, $zero\n    ctx->r17 = ADD32(ctx->r4, 0);\n"
NEW = ("    { /* PATCH: s6027 cellmul */ double m6027 = rs6027_mul(); if (m6027 > 0.0) { int32_t n0 = (int32_t)ctx->r4; int32_t n1 = (int32_t)(n0 * m6027); if (n1 < 1) n1 = 1; "
       "ctx->r4 = (int64_t)n1; fprintf(stderr, \"[cellmul] count %d -> %d\\n\", n0, n1); } }\n")
def apply10(text):
    if "RECOMP_FUNC void allocAndInitGridCellArray(" not in text or "PATCH: s6027 cellmul" in text: return text, 0
    assert text.count(OLD) == 1
    i = text.find("RECOMP_FUNC void allocAndInitGridCellArray(")
    text = text[:i] + HDR + text[i:]
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    p = base / "funcs_10.c"; t = p.read_text(); t2, n = apply10(t)
    if n: p.write_text(t2)
    print("funcs_10.c live patched x%d" % n)
