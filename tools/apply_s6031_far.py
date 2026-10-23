"""s6031 G1c: ROGUESQ_DD_FAR=<m> scales the `far` stack arg (sp+0x14) and ROGUESQ_DD_NEAR=<m> the `near` arg (sp+0x10)
of the guPerspective call in setupCameraMatrices (0x80016D10, funcs_4.c). Default unset = retail. Idempotent; mirrored into fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
HDR = '''/* PATCH: s6031 far */
static double rs6031_env(const char* k) { const char* e = getenv(k); return (e && *e) ? atof(e) : 0.0; }
'''
OLD = "    guPerspective(rdram, ctx);\n        goto after_0;\n"
NEW = ('    { /* PATCH: s6031 far */ static int n6031; double mf = rs6031_env("ROGUESQ_DD_FAR"), mn = rs6031_env("ROGUESQ_DD_NEAR");\n'
       '      if (mf > 0.0 || mn > 0.0) { uint32_t nu = MEM_W(0X10, ctx->r29), fu = MEM_W(0X14, ctx->r29); float nf, ff; memcpy(&nf, &nu, 4); memcpy(&ff, &fu, 4);\n'
       '        if ((n6031++ % 600) == 0) fprintf(stderr, "[far] near %g far %g fov %g aspect %g (mn %g mf %g)\\n", nf, ff, 0.0, 0.0, mn, mf);\n'
       '        if (mf > 0.0) { ff = (float)(ff * mf); memcpy(&fu, &ff, 4); MEM_W(0X14, ctx->r29) = fu; }\n'
       '        if (mn > 0.0) { nf = (float)(nf * mn); memcpy(&nu, &nf, 4); MEM_W(0X10, ctx->r29) = nu; } } }\n')
def apply4(text):
    if "PATCH: s6031 far" in text: return text, 0
    a = text.find("RECOMP_FUNC void setupCameraMatrices(")
    if a < 0: return text, 0
    i = text.find(OLD, a); assert i > 0
    text = text[:a] + HDR + text[a:]
    return text.replace(OLD, NEW + OLD, 1), 1
if __name__ == "__main__":
    p = base / "funcs_4.c"; t = p.read_text(); t2, n = apply4(t)
    if n: p.write_text(t2)
    print("funcs_4.c live patched x%d" % n)
