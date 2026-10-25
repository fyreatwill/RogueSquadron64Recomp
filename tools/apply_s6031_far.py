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
VPW = ('    { /* PATCH: s6112 vpw */ static double kv = -1.0; static uint32_t sp6112[8]; static int32_t og6112[8][2]; static int nl6112, ns6112; if (kv < 0.0) { const char* e = getenv("ROGUESQ_VPW_SCALE"); kv = (e && *e) ? atof(e) : 0.0; }\n'
       '      if (nl6112 < 12 || (kv > 0.0 && (nl6112 % 600) == 0)) fprintf(stderr, "[vpw] cam %08x w %d h %d cx %d cy %d kv %g\\n", (unsigned)ctx->r17, (int)MEM_W(ctx->r17, 0X10), (int)MEM_W(ctx->r17, 0X14), (int)MEM_W(ctx->r17, 0X18), (int)MEM_W(ctx->r17, 0X1C), kv); nl6112++;\n'
       '      if (kv > 0.0) { int i, f = -1; for (i = 0; i < ns6112; i++) if (sp6112[i] == (uint32_t)ctx->r17) f = i; if (f < 0 && ns6112 < 8) { f = ns6112++; sp6112[f] = (uint32_t)ctx->r17; og6112[f][0] = (int32_t)MEM_W(ctx->r17, 0X10); og6112[f][1] = (int32_t)MEM_W(ctx->r17, 0X18); }\n'
       '        if (f >= 0) { MEM_W(0X10, ctx->r17) = (uint32_t)(int32_t)(og6112[f][0] * kv); MEM_W(0X18, ctx->r17) = (uint32_t)(int32_t)(og6112[f][1] * kv); } } }\n')
def _apply4_old(text):
    if "PATCH: s6104 aspect" in text and "PATCH: s6112 vpw" not in text:
        return text.replace(OLD, VPW + OLD, 1), 1
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
if False:
    p = base / "funcs_4.c"; t = p.read_text(); t2, n = apply4(t)
    if n: p.write_text(t2)
    print("funcs_4.c live patched x%d" % n)

# s6113 G1d: ROGUESQ_FB_WIDTH=<w> widens the identified 512-wide video states (a0 of the video-state-update fn, stored at 0x8011A838 = scissor/colour-image width source).
FBW_ANCHOR = "    int c1cs = 0;\n    // 0x80017B88: addiu       $sp, $sp, -0x70\n"
FBW = ('    { /* PATCH: s6113 fbw */ static int wv = -1, nl; if (wv < 0) { const char* e = getenv("ROGUESQ_FB_WIDTH"); wv = (e && *e) ? atoi(e) : 0; }\n'
       '      if (nl < 16) { fprintf(stderr, "[fbw] vsu a0=%d a1=%d wv=%d\\n", (int)ctx->r4, (int)ctx->r5, wv); nl++; }\n'
       '      if (wv > 0 && (int)ctx->r4 == 512 && ((int)ctx->r5 == 448 || (int)ctx->r5 == 340)) ctx->r4 = (gpr)wv; }\n')
def applyfbw(text):
    if "PATCH: s6113 fbw" in text:
        old = '      if (wv > 0 && (int)ctx->r4 == 512 && (int)ctx->r5 == 448) ctx->r4 = (gpr)wv; }\n'
        new = '      if (wv > 0 && (int)ctx->r4 == 512 && ((int)ctx->r5 == 448 || (int)ctx->r5 == 340)) ctx->r4 = (gpr)wv; }\n'
        if old in text: return text.replace(old, new, 1), 1
        return text, 0
    assert text.count(FBW_ANCHOR) == 1, text.count(FBW_ANCHOR)
    return text.replace(FBW_ANCHOR, "    int c1cs = 0;\n" + FBW + "    // 0x80017B88: addiu       $sp, $sp, -0x70\n", 1), 1
def apply4(text):
    text, n = _apply4_old(text)
    text, m = applyfbw(text)
    return text, n + m

# s6115 G1d: partitionFramebufferMemory(a0,a1,a2=w,a3=h) sizes each fb as w*h*2 (0x70000 for 512x448); widen w under ROGUESQ_FB_WIDTH so flip buffers do not overlap.
PFM_ANCHOR = "    int c1cs = 0;\n    // 0x80000DD4: addu        $t5, $a0, $zero\n"
PFM = ('    int ow = (int)ctx->r6, oh = (int)ctx->r7;\n'
       '    { /* PATCH: s6115 pfm */ static int wv = -1, nl; if (wv < 0) { const char* e = getenv("ROGUESQ_FB_WIDTH"); wv = (e && *e) ? atoi(e) : 0; }\n'
       '      if (nl < 16) { fprintf(stderr, "[fbw] pfm a2=%d a3=%d wv=%d\\n", ow, oh, wv); nl++; }\n'
       '      if (wv > 0 && ow == 512 && (oh == 448 || oh == 340)) ctx->r6 = (gpr)wv; }\n')
def applypfm(text):
    if "PATCH: s6115 pfm" in text:
        current = '      if (wv > 0 && ow == 512 && oh == 448) ctx->r6 = (gpr)wv; }\n'
        current_new = '      if (wv > 0 && ow == 512 && (oh == 448 || oh == 340)) ctx->r6 = (gpr)wv; }\n'
        if current in text:
            return text.replace(current, current_new, 1), 1
        old = ('    { /* PATCH: s6115 pfm */ static int wv = -1, nl; if (wv < 0) { const char* e = getenv("ROGUESQ_FB_WIDTH"); wv = (e && *e) ? atoi(e) : 0; }\n'
               '      if (nl < 16) { fprintf(stderr, "[fbw] pfm a2=%d a3=%d wv=%d\\n", (int)ctx->r6, (int)ctx->r7, wv); nl++; }\n'
               '      if (wv > 0 && (int)ctx->r6 == 512 && ((int)ctx->r7 == 448 || (int)ctx->r7 == 340)) ctx->r6 = (gpr)wv; }\n')
        old2 = ('    { /* PATCH: s6115 pfm */ static int wv = -1, nl; int ow = (int)ctx->r6, oh = (int)ctx->r7; if (wv < 0) { const char* e = getenv("ROGUESQ_FB_WIDTH"); wv = (e && *e) ? atoi(e) : 0; }\n'
                '      if (nl < 16) { fprintf(stderr, "[fbw] pfm a2=%d a3=%d wv=%d\\n", ow, oh, wv); nl++; }\n'
                '      if (wv > 0 && ow == 512 && (oh == 448 || oh == 340)) ctx->r6 = (gpr)wv; }\n')
        if old in text:
            text = text.replace(old, PFM, 1)
        elif old2 in text:
            text = text.replace(old2, PFM, 1)
        else:
            return text, 0
    else:
        assert text.count(PFM_ANCHOR) == 1, text.count(PFM_ANCHOR)
        text = text.replace(PFM_ANCHOR, "    int c1cs = 0;\n" + PFM + "    // 0x80000DD4: addu        $t5, $a0, $zero\n", 1)
    start = text.find("RECOMP_FUNC void partitionFramebufferMemory(")
    if start < 0:
        return text, 0
    end = text.find("    return;\n    // 0x80001084: nop", start)
    if end < 0 or "PATCH: s6168 fballoc" in text[start:end]:
        return text, 0
    tail = ('    { /* PATCH: s6168 fballoc */ static int en = -1, n; if (en < 0) { const char* e = getenv("ROGUESQ_LOG_FB_ALLOC"); en = (e && *e && *e != \'0\') ? 1 : 0; }\n'
            '      if (en && n < 80) { fprintf(stderr, "[fballoc] in=%dx%d out=%dx%d p0=0x%08X/%u p1=0x%08X/%u top=0x%08X/%u/%u/%u\\n", ow, oh, (int)ctx->r6, (int)ctx->r7, U32(ctx->r13), U32(MEM_W(ctx->r13, 0)), U32(ctx->r14), U32(MEM_W(ctx->r14, 0)), U32(MEM_W(S32(0x8011 << 16), 0x63D8)), U32(MEM_W(S32(0x8011 << 16), 0x63DC)), U32(MEM_W(S32(0x8011 << 16), 0x63E0)), U32(MEM_W(S32(0x8011 << 16), 0x63E4))); fflush(stderr); ++n; } }\n')
    return text[:end] + tail + text[end:], 1

if __name__ == "__main__":
    p = base / "funcs_4.c"; t = p.read_text(); t2, n = apply4(t)
    if n: p.write_text(t2)
    print("funcs_4.c live patched x%d" % n)
    p0 = base / "funcs_0.c"; t = p0.read_text(); t2, n = applypfm(t)
    if n: p0.write_text(t2)
    print("funcs_0.c live patched x%d" % n)
