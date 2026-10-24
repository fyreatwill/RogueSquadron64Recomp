"""s6031 G1c: ROGUESQ_DD_FAR=<m> scales the `far` stack arg (sp+0x14) and ROGUESQ_DD_NEAR=<m> the `near` arg (sp+0x10)
of the guPerspective call in setupCameraMatrices (0x80016D10, funcs_4.c). Default unset = retail. Idempotent; mirrored into fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
HDR = '''/* PATCH: s6031 far */
static double rs6031_env(const char* k) { const char* e = getenv(k); return (e && *e) ? atof(e) : 0.0; }
static double rs6031_far(void) { double f = rs6031_env("ROGUESQ_DD_FAR"), d = rs6031_env("ROGUESQ_DRAW_DISTANCE"); return (f > 0.0) ? f : (d > 1.0 ? d : 0.0); } /* s6073: DRAW_DISTANCE>1 scales far */
'''
OLD = "    guPerspective(rdram, ctx);\n        goto after_0;\n"
NEW = ('    { /* PATCH: s6031 far */ static int n6031; double mf = rs6031_far(), mn = rs6031_env("ROGUESQ_DD_NEAR");\n'
       '      if (mf > 0.0 || mn > 0.0) { uint32_t nu = MEM_W(0X10, ctx->r29), fu = MEM_W(0X14, ctx->r29); float nf, ff; memcpy(&nf, &nu, 4); memcpy(&ff, &fu, 4);\n'
       '        if ((n6031++ % 600) == 0) fprintf(stderr, "[far] near %g far %g fov %g aspect %g (mn %g mf %g)\\n", nf, ff, 0.0, 0.0, mn, mf);\n'
       '        if (mf > 0.0) { ff = (float)(ff * mf); memcpy(&fu, &ff, 4); MEM_W(0X14, ctx->r29) = fu; }\n'
       '        if (mn > 0.0) { nf = (float)(nf * mn); memcpy(&nu, &nf, 4); MEM_W(0X10, ctx->r29) = nu; } } }\n')
ASP = ('    { /* PATCH: s6104 aspect */ static double k6104 = -1.0; if (k6104 < 0.0) { const char* e = getenv("ROGUESQ_ASPECT_SCALE"); k6104 = (e && *e) ? atof(e) : 0.0; if (k6104 > 0.0) fprintf(stderr, "[g1d] guPerspective aspect x%g\\n", k6104); }\n'
       '      if (k6104 > 0.0) { uint32_t au = (uint32_t)ctx->r7; float af; memcpy(&af, &au, 4); af = (float)(af * k6104); memcpy(&au, &af, 4); ctx->r7 = (int32_t)au; } }\n')
def apply4(text):
    if "PATCH: s6104 aspect" not in text and "PATCH: s6031 far */ static int" in text:
        return text.replace(OLD, ASP + OLD, 1), 1
    if "PATCH: s6031 far" in text:
        if "rs6031_far" in text: return text, 0
        text = text.replace('static double rs6031_env(const char* k) { const char* e = getenv(k); return (e && *e) ? atof(e) : 0.0; }\n', 'static double rs6031_env(const char* k) { const char* e = getenv(k); return (e && *e) ? atof(e) : 0.0; }\n' + HDR.split('\n')[2] + '\n', 1)
        return text.replace('mf = rs6031_env("ROGUESQ_DD_FAR")', 'mf = rs6031_far()'), 1
    a = text.find("RECOMP_FUNC void setupCameraMatrices(")
    if a < 0: return text, 0
    i = text.find(OLD, a); assert i > 0
    text = text[:a] + HDR + text[a:]
    return text.replace(OLD, NEW + ASP + OLD, 1), 1
if __name__ == "__main__":
    p = base / "funcs_4.c"; t = p.read_text(); t2, n = apply4(t)
    if n: p.write_text(t2)
    print("funcs_4.c live patched x%d" % n)
