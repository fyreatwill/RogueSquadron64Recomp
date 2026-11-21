"""s6031 G1c: ROGUESQ_DD_FAR=<m> scales the `far` stack arg (sp+0x14) and ROGUESQ_DD_NEAR=<m> the `near` arg (sp+0x10)
of the guPerspective call in setupCameraMatrices (0x80016D10, funcs_4.c). Default unset = retail. Idempotent; mirrored into fixup."""
import re
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
       '        if (f >= 0) { MEM_W(0X10, ctx->r17) = (uint32_t)(int32_t)(og6112[f][0] * kv * (og6112[f][0] == 640 ? 0.8 : 1.0)); MEM_W(0X18, ctx->r17) = (uint32_t)(int32_t)(og6112[f][1] * kv * (og6112[f][0] == 640 ? 0.8 : 1.0)); } } }\n')
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
old6227 = '(uint32_t)(int32_t)(og6112[f][0] * kv); MEM_W(0X18, ctx->r17) = (uint32_t)(int32_t)(og6112[f][1] * kv);'
new6227 = '(uint32_t)(int32_t)(og6112[f][0] * kv * (og6112[f][0] == 640 ? 0.8 : 1.0)); MEM_W(0X18, ctx->r17) = (uint32_t)(int32_t)(og6112[f][1] * kv * (og6112[f][0] == 640 ? 0.8 : 1.0));'
def apply4(text):
    text, n = _apply4_old(text)
    while n:  # s6863: one stage per call, so a pristine pass stopped before the s6112 VPW block
        text, m = _apply4_old(text)
        if not m: break
        n += m
    if old6227 in text:
        text = text.replace(old6227, new6227); n += 1
    # s6428 G1d: log each camera on first sight (nl6112<12 budget hid the later cams).
    o6428 = "og6112[f][1] = (int32_t)MEM_W(ctx->r17, 0X18); }\n"
    n6428 = "og6112[f][1] = (int32_t)MEM_W(ctx->r17, 0X18); fprintf(stderr, \"[vpw1] cam %08x w %d h %d cx %d cy %d\\n\", (unsigned)ctx->r17, og6112[f][0], (int)MEM_W(ctx->r17, 0X14), og6112[f][1], (int)MEM_W(ctx->r17, 0X1C)); }\n"
    if o6428 in text and "[vpw1]" not in text:
        text = text.replace(o6428, n6428, 1); n += 1
    # s6427 G1d: 320-wide cameras (attribution/N64 logo) render into an unwidened 320 fb; do not W/512-scale them.
    o6427 = "(og6112[f][0] == 640 ? 0.8 : 1.0)"; n6427 = "(og6112[f][0] == 640 ? 0.8 : og6112[f][0] == 320 ? 1.0 / kv : 1.0)"
    if o6427 in text:
        text = text.replace(o6427, n6427); n += 1
    # s6428 G1d: scale cameras by the LIVE video-state width (0x8011A838): unwidened 320/640 fbs (logo/menus) get no scale; 640-cam in a widened flight fb keeps 0.8.
    o6428b = "(og6112[f][0] == 640 ? 0.8 : og6112[f][0] == 320 ? 1.0 / kv : 1.0)"
    n6428b = "((int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000) <= 640 ? 1.0 / kv : og6112[f][0] == 640 ? 0.8 : 1.0)"
    if o6428b in text:
        text = text.replace(o6428b, n6428b); n += 1
    # s6701 G1c: guPerspective's u16 perspNorm = (u16)(131072/(near+far)) drops 2 -> 1 once the scaled far passes
    # 65536-near (lvl5 far 9728 x6.734); with perspNorm 1 the scene renders in a shrunken centre box (dd8 boxed,
    # threshold bracketed DD_FAR 6.70 clean / 6.78 boxed). Cap the scaled far at 65534-near; ROGUESQ_DD_PNORM_CAP=0 = old.
    o6701 = "        if (mf > 0.0) { ff = (float)(ff * mf); memcpy(&fu, &ff, 4); MEM_W(0X14, ctx->r29) = fu; }\n"
    n6701 = ("        if (mf > 0.0) { static int pc6701 = -1; if (pc6701 < 0) { const char* e = getenv(\"ROGUESQ_DD_PNORM_CAP\"); pc6701 = !(e && *e == '0'); }\n"
             "          float lim = 65534.0f - nf, sf = (float)(ff * mf); if (pc6701 && sf > lim) { static int nl6701; if (nl6701++ < 8) fprintf(stderr, \"[pnormcap] far %g x%g -> %g (near %g)\\n\", ff, mf, (lim > ff ? lim : ff), nf); sf = lim > ff ? lim : ff; }\n"
             "          ff = sf; memcpy(&fu, &ff, 4); MEM_W(0X14, ctx->r29) = fu; }\n")
    if o6701 in text and "pc6701" not in text:
        text = text.replace(o6701, n6701, 1); n += 1
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

def apply_s6207_drop(text):
    if "PATCH: s6207 drop" in text:
        return text, 0
    helper = (
        "/* PATCH: s6207 drop\n"
        "   The 0x100000 path ends an image at top-0x100000. On a widened flight\n"
        "   carve the n=3 pool starts below that (s6206: e8 = top - t0 - 0x6B000,\n"
        "   t1+t1+t2 = 0x10000+0x10000+0x4B000). Shift only that image down by the\n"
        "   overlap so it ends on the pool base. The upward cursor stays put, and\n"
        "   4:3 (overlap negative, or aspect not wider) keeps the retail address. */\n"
        "static int rs64_g1d_image_drop(void) {\n"
        "    static int drop = -2;\n"
        "    if (drop != -2) return drop;\n"
        "    drop = 0;\n"
        "    const char* as = getenv(\"ROGUESQ_ASPECT\");\n"
        "    const char* c = as ? as : \"\";\n"
        "    while (as && *c && *c != ':') ++c;\n"
        "    double w = (as && *c == ':') ? atof(as) : 0.0, h = (as && *c == ':') ? atof(c + 1) : 0.0;\n"
        "    if (as && w > 0.0 && h > 0.0 && w / h > 4.0 / 3.0 + 1e-3) {\n"
        "        int fbw = 0; const char* fe = getenv(\"ROGUESQ_FB_WIDTH\"); if (fe && *fe) fbw = atoi(fe);\n"
        "        if (fbw <= 0) { fbw = (int)(448.0 * w / h + 0.5); if (fbw > 1024) fbw = 1024; }\n"
        "        uint32_t t0 = ((uint32_t)fbw * 448u * 2u + 0x3fu) & ~0x3fu;\n"
        "        int32_t ov = (int32_t)t0 + 0x6B000 - 0x100000;\n"
        "        if (ov > 0) drop = (int)ov;\n"
        "        { const char* ex = getenv(\"ROGUESQ_G1D_DROP_EXTRA\"); if (ov > 0 && ex && *ex) drop += (int)strtoul(ex, 0, 0); }\n"
        "        fprintf(stderr, \"[g1d-drop] aspect=%s fbw=%d t0=0x%X drop=0x%X\\n\", as, fbw, t0, (unsigned)drop);\n"
        "    } else fprintf(stderr, \"[g1d-drop] aspect=%s drop=0\\n\", as ? as : \"<unset>\");\n"
        "    fflush(stderr);\n"
        "    return drop;\n"
        "}\n"
    )
    anchor = "RECOMP_FUNC void partitionFramebufferMemory("
    site = (
        "    // 0x80000F14: subu        $v0, $a0, $v0\n"
        "    ctx->r2 = SUB32(ctx->r4, ctx->r2);\n"
    )
    site_new = (
        site +
        "    { /* PATCH: s6207 drop */ int d = rs64_g1d_image_drop(); if (d > 0) ctx->r2 = SUB32(ctx->r2, d); }\n"
    )
    if text.count(anchor) != 1 or text.count(site) != 1:
        return text, 0
    text = text.replace(anchor, helper + anchor, 1)
    return text.replace(site, site_new, 1), 1

def apply_s6201_carve(text):
    if "PATCH: s6201 carve" in text:
        return text, 0
    a = text.find("RECOMP_FUNC void partitionFramebufferMemory(")
    b = text.find("RECOMP_FUNC void thread3_video_handle(", a)
    if a < 0 or b < 0:
        return text, 0
    body = text[a:b]
    body = body.replace(
        "    // 0x80000DD4: addu        $t5, $a0, $zero\n",  # s6864: s6718 sits between the s6115 block and this comment
        "    uint32_t g1d_top = 0, g1d_a3 = 0, g1d_t0 = 0, g1d_t1 = 0, g1d_t2 = 0, g1d_t3 = 0, g1d_t4 = 0, g1d_ptr = 0, g1d_pc = 0;\n"
        "    int g1d_outw = (int)ctx->r6; /* PATCH: s6201 carve */\n"
        "    // 0x80000DD4: addu        $t5, $a0, $zero\n",
        1)
    body = body.replace(
        "L_80000EC8:\n    // 0x80000EC8: lui         $v0, 0x8011\n",
        "L_80000EC8:\n"
        "    g1d_top = U32(ctx->r4); g1d_a3 = U32(ctx->r7); g1d_t0 = U32(ctx->r8); g1d_t1 = U32(ctx->r9); g1d_t2 = U32(ctx->r10); g1d_t3 = U32(ctx->r11); g1d_t4 = U32(ctx->r12); /* PATCH: s6201 carve snap */\n"
        "    // 0x80000EC8: lui         $v0, 0x8011\n",
        1)
    body = body.replace(
        "{ MEM_W(0X63E8, ctx->r1) = ctx->r4; RS64_S5798_ST(0x80000FFCu, 0X63E8, ctx->r1, 4); }\n",
        "{ MEM_W(0X63E8, ctx->r1) = ctx->r4; RS64_S5798_ST(0x80000FFCu, 0X63E8, ctx->r1, 4); }\n"
        "    g1d_ptr = U32(ctx->r4); g1d_pc = 0x80000FFCu; /* PATCH: s6201 carve ptr */\n",
        1)
    body = body.replace(
        "{ MEM_W(0X63E8, ctx->r1) = ctx->r3; RS64_S5798_ST(0x80001010u, 0X63E8, ctx->r1, 4); }\n",
        "{ MEM_W(0X63E8, ctx->r1) = ctx->r3; RS64_S5798_ST(0x80001010u, 0X63E8, ctx->r1, 4); }\n"
        "    g1d_ptr = U32(ctx->r3); g1d_pc = 0x80001010u; /* PATCH: s6201 carve ptr */\n",
        1)
    ret = "    return;\n    // 0x80001084: nop\n"
    log = (
        "    { /* PATCH: s6201 carve */ static int en = -1, n; if (en < 0) { const char* e = getenv(\"ROGUESQ_LOG_G1D_TASK\"); en = (e && *e && *e != '0') ? 1 : 0; }\n"
        "      if (en && n < 24) { fprintf(stderr, \"[g1d-carve] n=%d pc=0x%08X ra=0x%08X in=%dx%d outw=%d top=0x%08X a3=0x%X t0=0x%X t1=0x%X t2=0x%X t3=0x%X t4=0x%X ptr=0x%08X e4=0x%08X d8=0x%08X dc=0x%08X e0=0x%08X e8=0x%08X f0=0x%08X f4=0x%08X f8=0x%08X ec=0x%08X\\n\",\n"
        "        n, g1d_pc, U32(ctx->r31), ow, oh, g1d_outw, g1d_top, g1d_a3, g1d_t0, g1d_t1, g1d_t2, g1d_t3, g1d_t4, g1d_ptr,\n"
        "        U32(MEM_W(S32(0x8011 << 16), 0x63E4)), U32(MEM_W(S32(0x8011 << 16), 0x63D8)), U32(MEM_W(S32(0x8011 << 16), 0x63DC)), U32(MEM_W(S32(0x8011 << 16), 0x63E0)), U32(MEM_W(S32(0x8011 << 16), 0x63E8)), U32(MEM_W(S32(0x8011 << 16), 0x63F0)), U32(MEM_W(S32(0x8011 << 16), 0x63F4)), U32(MEM_W(S32(0x8011 << 16), 0x63F8)), U32(MEM_W(S32(0x8011 << 16), 0x63EC))); fflush(stderr); ++n; } }\n"
    )
    if body.count(ret) != 1 or "s6201 carve snap" not in body or body.count("s6201 carve ptr") != 2:
        return text, 0
    body = body.replace(ret, log + ret, 1)
    return text[:a] + body + text[b:], 1

def apply_s6202_retarget(text):
    if "PATCH: s6202 retarget" in text:
        return text, 0
    old = (
        "{ MEM_W(0X63E8, ctx->r1) = ctx->r3; RS64_S5798_ST(0x80001010u, 0X63E8, ctx->r1, 4); }\n"
        "    g1d_ptr = U32(ctx->r3); g1d_pc = 0x80001010u; /* PATCH: s6201 carve ptr */\n"
    )
    new = (
        "{ MEM_W(0X63E8, ctx->r1) = ctx->r3; RS64_S5798_ST(0x80001010u, 0X63E8, ctx->r1, 4); }\n"
        "    { /* PATCH: s6202 retarget */ static int n6202; uint32_t cur = U32(ctx->r3);\n"
        "      if (g1d_outw != 512 && ow == 512) {\n"
        "        uint32_t t2 = U32(ctx->r10), t3 = U32(ctx->r11), t4 = U32(ctx->r12), a1 = U32(ctx->r5);\n"
        "        int down = (t3 >= a1 && t4 >= a1); uint32_t ec = cur - t3 - t4; uint32_t base = ec - t2;\n"
        "        uint32_t hhead = 0, hend = 0; int crossed = 0, hok = 0;\n"
        "        if (down && t2 >= 0x10u && (base & 0xFu) == 0u && base >= 0x80000000u && base < ec) {\n"
        "          hhead = U32(MEM_W(S32(0x8010 << 16), 0xFF18));\n"
        "          if (hhead >= 0x80000000u && hhead < 0x81000000u) {\n"
        "            uint32_t a = hhead; int g = 0;\n"
        "            while (g++ < 200000) {\n"
        "              uint32_t w0 = U32(MEM_W(S32(a), 0)), sz = U32(MEM_W(S32(a), 4)), fl = w0 >> 16;\n"
        "              if (g == 1 && (fl & 0xBu) == 0u) break;\n"
        "              hend = a; hok = 1; if (a > base) crossed = 1;\n"
        "              if (fl & 8u) break;\n"
        "              if (sz == 0u || sz > 0x1000000u) break;\n"
        "              uint32_t nxa = a + 0x10u + sz; if (nxa <= a || nxa >= 0x81000000u) break; a = nxa; } }\n"
        "          if (crossed) { if (n6202 < 8) fprintf(stderr, \"[g1d-retarget] reject heap_end=0x%08X heap_head=0x%08X base=0x%08X span_end=0x%08X t2=0x%X cur=0x%08X hok=%d\\n\", hend, hhead, base, ec, t2, cur, hok); }\n"
        "          else { MEM_W(0X63E8, ctx->r1) = (int32_t)base; if (n6202 < 8) fprintf(stderr, \"[g1d-retarget] ok base=0x%08X span_end=0x%08X t2=0x%X cur=0x%08X heap_end=0x%08X heap_head=0x%08X hok=%d\\n\", base, ec, t2, cur, hend, hhead, hok); }\n"
        "        } else if (n6202 < 8) fprintf(stderr, \"[g1d-retarget] reject path down=%d base=0x%08X ec=0x%08X t2=0x%X t3=0x%X t4=0x%X a1=0x%X cur=0x%08X\\n\", down, base, ec, t2, t3, t4, a1, cur);\n"
        "        ++n6202; fflush(stderr);\n"
        "      } else if (n6202 < 8) { fprintf(stderr, \"[g1d-retarget] skip outw=%d ow=%d cur=0x%08X\\n\", g1d_outw, ow, cur); fflush(stderr); ++n6202; } }\n"
        "    g1d_ptr = U32(MEM_W(0X63E8, ctx->r1)); g1d_pc = 0x80001010u; /* PATCH: s6201 carve ptr */\n"
    )
    if text.count(old) != 1:
        return text, 0
    return text.replace(old, new, 1), 1

# s7482: the s6202 retarget puts the wide frame pool at base = ec - t2, BELOW the lowest descending block, but the routine
# still returns $v1 = ec as the bottom of its reserved span (*(t5) / *(t6) -> heap init 0x80002150 a3 / hole), so the heap
# owns [base, ec) and the live pool sits in a free heap block (s7481 loc_S). Lower $v1 to base before the out stores so the
# game's own reservation covers the pool. ROGUESQ_RETARGET_RESERVE=0 restores the old (unreserved) span.
# g_rs64_s7482_base/_ec publish the live pool span to the host rs_malloc collision detector (upstream_compat.cpp s7482).
S7482_DECL = (
    "extern volatile uint32_t g_rs64_s7482_base, g_rs64_s7482_ec; /* PATCH: s7482 reserve */\n"
    "static int rs64_s7482_pend; static uint32_t rs64_s7482_b, rs64_s7482_e;\n"
    "static int rs64_s7482_on(void) { static int on = -1; if (on < 0) { const char* e = getenv(\"ROGUESQ_RETARGET_RESERVE\"); on = !(e && *e == '0'); } return on; }\n"
)
def apply_s7482_reserve(text):
    if "PATCH: s7482 reserve" in text:
        return text, 0
    anchor = "RECOMP_FUNC void partitionFramebufferMemory("
    ok = "          else { MEM_W(0X63E8, ctx->r1) = (int32_t)base; "
    tail = "L_80001060:\n    // 0x80001060: bne         $a0, $zero, L_80001074\n"
    if text.count(anchor) != 1 or text.count(ok) != 1 or text.count(tail) != 1:
        return text, 0
    text = text.replace(anchor, S7482_DECL + anchor, 1)
    text = text.replace(ok, ok + "rs64_s7482_pend = 1; rs64_s7482_b = base; rs64_s7482_e = ec; /* PATCH: s7482 reserve ok */ ", 1)
    tail_new = (
        "L_80001060:\n"
        "    { /* PATCH: s7482 reserve tail */ static int n7482; uint32_t v1 = U32(ctx->r3);\n"
        "      if (rs64_s7482_pend) { int res = rs64_s7482_on() && v1 == rs64_s7482_e;\n"
        "        if (res) ctx->r3 = (gpr)(int64_t)(int32_t)rs64_s7482_b;\n"
        "        g_rs64_s7482_base = rs64_s7482_b; g_rs64_s7482_ec = rs64_s7482_e;\n"
        "        if (n7482 < 16) { fprintf(stderr, \"[s7482] reserve %s v1=0x%08X -> 0x%08X pool=0x%08X..0x%08X a0=0x%08X on=%d\\n\", res ? \"applied\" : \"skipped\", v1, U32(ctx->r3), rs64_s7482_b, rs64_s7482_e, U32(ctx->r4), rs64_s7482_on()); fflush(stderr); ++n7482; }\n"
        "      } else { g_rs64_s7482_base = 0; g_rs64_s7482_ec = 0; }\n"
        "      rs64_s7482_pend = 0; }\n"
        "    // 0x80001060: bne         $a0, $zero, L_80001074\n"
    )
    text = text.replace(tail, tail_new, 1)
    return text, 1

def apply_s6203_heapclass(text):
    if "PATCH: s6203 heapclass" in text:
        return text, 0
    old = (
        "    { /* PATCH: s6202 retarget */ static int n6202; uint32_t cur = U32(ctx->r3);\n"
        "      if (g1d_outw != 512 && ow == 512) {\n"
    )
    new = (
        "    { /* PATCH: s6202 retarget */ static int n6202; uint32_t cur = U32(ctx->r3);\n"
        "      if (ow == 512) { /* PATCH: s6203 heapclass */ static int en6203 = -1, n6203;\n"
        "        if (en6203 < 0) { const char* e = getenv(\"ROGUESQ_LOG_G1D_TASK\"); en6203 = (e && *e && *e != '0') ? 1 : 0; }\n"
        "        if (en6203 && n6203 < 8) {\n"
        "          uint32_t want0 = 0x80B25000u, want1 = 0x8096D600u;\n"
        "          uint32_t b0 = 0, f0 = 0, tg0 = 0, s0 = 0, b1 = 0, f1 = 0, tg1 = 0, s1 = 0, hhead = 0, last = 0;\n"
        "          int hit0 = 0, hit1 = 0, nblk = 0;\n"
        "          hhead = U32(MEM_W(S32(0x8010 << 16), 0xFF18));\n"
        "          if (hhead >= 0x80000000u && hhead < 0x81000000u) {\n"
        "            uint32_t a = hhead; int g = 0;\n"
        "            while (g++ < 200000) {\n"
        "              uint32_t w0 = U32(MEM_W(S32(a), 0)), sz = U32(MEM_W(S32(a), 4)), fl = w0 >> 16;\n"
        "              if (g == 1 && (fl & 0xBu) == 0u) break;\n"
        "              ++nblk; last = a;\n"
        "              if (sz <= 0x1000000u) {\n"
        "                uint32_t span = a + 0x10u + sz;\n"
        "                if (span > a) {\n"
        "                  if (!hit0 && a <= want0 && want0 < span) { hit0 = 1; b0 = a; f0 = fl; tg0 = w0 & 0xFFFFu; s0 = sz; }\n"
        "                  if (!hit1 && a <= want1 && want1 < span) { hit1 = 1; b1 = a; f1 = fl; tg1 = w0 & 0xFFFFu; s1 = sz; }\n"
        "                } }\n"
        "              if ((hit0 && hit1) || (fl & 8u)) break;\n"
        "              if (sz == 0u || sz > 0x1000000u) break;\n"
        "              uint32_t nxa = a + 0x10u + sz; if (nxa <= a || nxa >= 0x81000000u) break; a = nxa; } }\n"
        "          fprintf(stderr, \"[g1d-hblk] cur=0x%08X ow=%d outw=%d head=0x%08X last=0x%08X nblk=%d same=%d ctl_addr=0x%08X ctl_fl=%04X ctl_tag=%04X ctl_sz=0x%X ctl_hit=%d cand_addr=0x%08X cand_fl=%04X cand_tag=%04X cand_sz=0x%X cand_hit=%d\\n\",\n"
        "            cur, ow, g1d_outw, hhead, last, nblk, (hit0 && hit1 && b0 == b1) ? 1 : 0, b0, (unsigned)f0, (unsigned)tg0, s0, hit0, b1, (unsigned)f1, (unsigned)tg1, s1, hit1);\n"
        "          fflush(stderr); ++n6203; } }\n"
        "      if (g1d_outw != 512 && ow == 512) {\n"
    )
    if text.count(old) != 1:
        return text, 0
    return text.replace(old, new, 1), 1

def apply_s6204_poolclass(text):
    if "PATCH: s6204 poolclass" in text:
        return text, 0
    old = (
        "      if (en && n < 8) { fprintf(stderr, \"[g1d-pool] n=%d pc=0x80018030 base=0x%08X bytes=0x%X arg=0x%X end=0x%08X ra=0x%08X\\n\", n, U32(ctx->r18), U32(ctx->r2), U32(ctx->r23), U32(ctx->r3), U32(ctx->r31)); fflush(stderr); ++n; } }\n"
    )
    new = (
        "      if (en && n < 8) { fprintf(stderr, \"[g1d-pool] n=%d pc=0x80018030 base=0x%08X bytes=0x%X arg=0x%X end=0x%08X ra=0x%08X\\n\", n, U32(ctx->r18), U32(ctx->r2), U32(ctx->r23), U32(ctx->r3), U32(ctx->r31));\n"
        "        if (n == 3) { /* PATCH: s6204 poolclass */\n"
        "          uint32_t want0 = 0x80B25000u, want1 = 0x8096D600u;\n"
        "          uint32_t b0 = 0, f0 = 0, tg0 = 0, s0 = 0, b1 = 0, f1 = 0, tg1 = 0, s1 = 0, hhead = 0, last = 0;\n"
        "          int hit0 = 0, hit1 = 0, nblk = 0;\n"
        "          hhead = U32(MEM_W(S32(0x8010 << 16), 0xFF18));\n"
        "          if (hhead >= 0x80000000u && hhead < 0x81000000u) {\n"
        "            uint32_t a = hhead; int g = 0;\n"
        "            while (g++ < 200000) {\n"
        "              uint32_t w0 = U32(MEM_W(S32(a), 0)), sz = U32(MEM_W(S32(a), 4)), fl = w0 >> 16;\n"
        "              if (g == 1 && (fl & 0xBu) == 0u) break;\n"
        "              ++nblk; last = a;\n"
        "              if (sz <= 0x1000000u) {\n"
        "                uint32_t span = a + 0x10u + sz;\n"
        "                if (span > a) {\n"
        "                  if (!hit0 && a <= want0 && want0 < span) { hit0 = 1; b0 = a; f0 = fl; tg0 = w0 & 0xFFFFu; s0 = sz; }\n"
        "                  if (!hit1 && a <= want1 && want1 < span) { hit1 = 1; b1 = a; f1 = fl; tg1 = w0 & 0xFFFFu; s1 = sz; }\n"
        "                } }\n"
        "              if ((hit0 && hit1) || (fl & 8u)) break;\n"
        "              if (sz == 0u || sz > 0x1000000u) break;\n"
        "              uint32_t nxa = a + 0x10u + sz; if (nxa <= a || nxa >= 0x81000000u) break; a = nxa; } }\n"
        "          fprintf(stderr, \"[g1d-hblk-pool] n=%d head=0x%08X last=0x%08X nblk=%d same=%d ctl_addr=0x%08X ctl_fl=%04X ctl_tag=%04X ctl_sz=0x%X ctl_hit=%d cand_addr=0x%08X cand_fl=%04X cand_tag=%04X cand_sz=0x%X cand_hit=%d\\n\",\n"
        "            n, hhead, last, nblk, (hit0 && hit1 && b0 == b1) ? 1 : 0, b0, (unsigned)f0, (unsigned)tg0, s0, hit0, b1, (unsigned)f1, (unsigned)tg1, s1, hit1);\n"
        "        }\n"
        "        fflush(stderr); ++n; } }\n"
    )
    if text.count(old) != 1:
        return text, 0
    return text.replace(old, new, 1), 1

def apply_s6201_pool(text):
    if "PATCH: s6201 pool" in text:
        return text, 0
    anchor = "    // 0x80018030: addu        $v1, $s2, $v0\n    ctx->r3 = ADD32(ctx->r18, ctx->r2);\n"
    if text.count(anchor) != 1:
        return text, 0
    log = (
        anchor +
        "    { /* PATCH: s6201 pool */ static int en = -1, n; if (en < 0) { const char* e = getenv(\"ROGUESQ_LOG_G1D_TASK\"); en = (e && *e && *e != '0') ? 1 : 0; }\n"
        "      if (en && n < 8) { fprintf(stderr, \"[g1d-pool] n=%d pc=0x80018030 base=0x%08X bytes=0x%X arg=0x%X end=0x%08X ra=0x%08X\\n\", n, U32(ctx->r18), U32(ctx->r2), U32(ctx->r23), U32(ctx->r3), U32(ctx->r31)); fflush(stderr); ++n; } }\n"
    )
    return text.replace(anchor, log, 1), 1

def apply_s6201_alloc(text):
    if "PATCH: s6201 alloc" in text:
        return text, 0
    a = text.find("RECOMP_FUNC void beginFrameDLChunk(")
    b = text.find("\nRECOMP_FUNC ", a + 10)
    if a < 0 or b < 0:
        return text, 0
    body = text[a:b]
    body = body.replace(
        "    int c1cs = 0;\n",
        "    int c1cs = 0;\n    uint32_t g1d_head = 0, g1d_next = 0; /* PATCH: s6201 alloc */\n",
        1)
    # s7736: anchor on the NEXT instruction's comment. The old anchor (the 0x8000A934 load line) stopped matching once
    # s5798/s6287/s6285 text landed around it, so a regen dropped this whole probe silently. Before 0x8000A938 = after
    # the load and anything appended to it (the s6285 block), the position the live tree has.
    head = "    // 0x8000A938: lw          $v0, 0x0($v0)\n"
    if body.count(head) != 1:
        return text, 0
    body = body.replace(head, "    g1d_head = U32(ctx->r2); /* PATCH: s6201 alloc head */\n" + head, 1)
    nxt = "    // 0x8000A93C: lui         $at, 0x8011\n"
    if body.count(nxt) != 1:
        return text, 0
    body = body.replace(nxt, "    g1d_next = U32(ctx->r2); /* PATCH: s6201 alloc next */\n" + nxt, 1)
    st = "{ MEM_W(-0X5B40, ctx->r1) = ctx->r2; RS64_S5798_ST(0x8000A9CCu, -0X5B40, ctx->r1, 4); }\n"
    if body.count(st) != 1:
        return text, 0
    post = "rs64_f5_store_shadow_post('W', 0x8000A9CCu, U32(ADD32(ctx->r1, -0X5B40))); } /* PATCH: s6336 F5 post-store shadow */\n"
    i = body.find(st) + len(st)  # s7736: keep the live order (after s6336's post-store line when it is already there)
    j = body.find("\n", i)
    if j > 0 and body[i:j + 1].endswith(post):
        st = body[body.rfind("\n", 0, body.find(st)) + 1:j + 1]
    log = (
        st +
        "    { /* PATCH: s6201 alloc */ static int en = -1, n, seen; static uint32_t last = 0xffffffffu; if (en < 0) { const char* e = getenv(\"ROGUESQ_LOG_G1D_TASK\"); en = (e && *e && *e != '0') ? 1 : 0; }\n"
        "      if (en) { uint32_t ptr = U32(ctx->r4); ++seen; if ((ptr != last || seen <= 4) && n < 2000) { last = ptr; uint32_t stride = (g1d_next > g1d_head) ? (g1d_next - g1d_head) : 0u;\n"
        "        fprintf(stderr, \"[g1d-alloc] n=%d seen=%d pc=0x8000A9CC ptr=0x%08X head=0x%08X next=0x%08X stride=0x%X slot=0x%08X ra=0x%08X\\n\", n, seen, ptr, g1d_head, g1d_next, stride, U32(ctx->r2), U32(ctx->r31)); fflush(stderr); ++n; } } }\n"
    )
    body = body.replace(st, log, 1)
    return text[:a] + body + text[b:], 1

def apply_s6631_heapcap(text):
    if "PATCH: s6631 heapcap" in text:
        return text, 0
    helper = (
        "/* PATCH: s6631 heapcap\n"
        "   The flags&4 heap (head 0x8010FEFC) is built by ensureHeapInitialized.\n"
        "   Its gap path sets the arena end to 801163E4+fbsize. After the wide\n"
        "   carve that pointer is the live depth image, so the tail free block\n"
        "   is the image. Heap 8010FF18 already ends on the depth pointer. Stop\n"
        "   8010FEFC there too, at init and again at each carve. 4:3 does not\n"
        "   write. */\n"
        "static int rs64_g1d_wide(void) {\n"
        "    static int wide = -1;\n"
        "    if (wide >= 0) return wide;\n"
        "    wide = 0;\n"
        "    const char* as = getenv(\"ROGUESQ_ASPECT\");\n"
        "    const char* c = as ? as : \"\";\n"
        "    while (as && *c && *c != ':') ++c;\n"
        "    double aw = (as && *c == ':') ? atof(as) : 0.0;\n"
        "    double ah = (as && *c == ':') ? atof(c + 1) : 0.0;\n"
        "    if (aw > 0.0 && ah > 0.0 && aw / ah > 4.0 / 3.0 + 1e-3) wide = 1;\n"
        "    return wide;\n"
        "}\n"
        "static void rs64_g1d_heapcap(uint8_t* rdram) {\n"
        "    if (!rs64_g1d_wide()) return;\n"
        "    uint32_t e4 = U32(MEM_W(S32(0x8011 << 16), 0x63E4));\n"
        "    uint32_t head = U32(MEM_W(S32(0x8011 << 16), -0x104));\n"
        "    int did = 0;\n"
        "    uint32_t cut = 0, oldsz = 0, newsz = 0, flcut = 0, seen_a = 0, seen_fl = 0, seen_sz = 0;\n"
        "    if ((e4 & 0xFu) == 0u && e4 >= 0x80000020u && e4 < 0x81000000u &&\n"
        "        head >= 0x80000000u && head < e4) {\n"
        "        uint32_t a = head, prev = 0;\n"
        "        for (int g = 0; g < 200000; ++g) {\n"
        "            uint32_t w0 = U32(MEM_W(S32(a), 0));\n"
        "            uint32_t sz = U32(MEM_W(S32(a), 4));\n"
        "            uint32_t fl = w0 >> 16;\n"
        "            seen_a = a; seen_fl = fl; seen_sz = sz;\n"
        "            if ((fl & 8u) || sz == 0u || sz > 0x1000000u) break;\n"
        "            uint32_t nxt = a + 0x10u + sz;\n"
        "            if (nxt <= a || nxt >= 0x81000000u) break;\n"
        "            /* Wide gap punch: the free tail's header is exactly e4, so the\n"
        "               image's first bytes are a heap header. Do not write there.\n"
        "               Shorten the previous block and plant the terminator at e4-0x10. */\n"
        "            if (a >= e4) {\n"
        "                if ((fl & 1u) && !(fl & 2u) && prev >= 0x80000000u && prev + 0x20u <= e4) {\n"
        "                    uint32_t nsz = e4 - prev - 0x20u;\n"
        "                    uint32_t term = e4 - 0x10u;\n"
        "                    cut = prev; oldsz = U32(MEM_W(S32(prev), 4)); flcut = fl;\n"
        "                    MEM_W(4, S32(prev)) = (int32_t)nsz;\n"
        "                    MEM_H(0, S32(term)) = 8;\n"
        "                    MEM_H(2, S32(term)) = 0;\n"
        "                    MEM_W(4, S32(term)) = 0;\n"
        "                    newsz = nsz; did = 3;\n"
        "                }\n"
        "                break;\n"
        "            }\n"
        "            if (nxt > e4) {\n"
        "                cut = a; oldsz = sz; flcut = fl;\n"
        "                if (a + 0x10u == e4) {\n"
        "                    MEM_H(0, S32(a)) = 8;\n"
        "                    MEM_H(2, S32(a)) = 0;\n"
        "                    MEM_W(4, S32(a)) = 0;\n"
        "                    newsz = 0; did = 1;\n"
        "                } else if (a + 0x20u <= e4) {\n"
        "                    uint32_t nsz = e4 - a - 0x20u;\n"
        "                    uint32_t term = e4 - 0x10u;\n"
        "                    MEM_W(4, S32(a)) = (int32_t)nsz;\n"
        "                    MEM_H(0, S32(term)) = 8;\n"
        "                    MEM_H(2, S32(term)) = 0;\n"
        "                    MEM_W(4, S32(term)) = 0;\n"
        "                    newsz = nsz; did = 2;\n"
        "                }\n"
        "                break;\n"
        "            }\n"
        "            prev = a;\n"
        "            a = nxt;\n"
        "        }\n"
        "        if (!did) { cut = seen_a; flcut = seen_fl; oldsz = seen_sz; }\n"
        "    }\n"
        "    static int quiet = 0, cuts = 0;\n"
        "    if ((did && cuts < 16) || (!did && quiet < 8)) {\n"
        "        fprintf(stderr, \"[g1d-heapcap] e4=0x%08X head=0x%08X did=%d cut=0x%08X fl=%04X oldsz=0x%X newsz=0x%X\\n\",\n"
        "            e4, head, did, cut, (unsigned)flcut, oldsz, newsz);\n"
        "        fflush(stderr);\n"
        "        if (did) ++cuts; else ++quiet;\n"
        "    }\n"
        "}\n"
    )
    anchor = "RECOMP_FUNC void partitionFramebufferMemory(uint8_t* rdram, recomp_context* ctx) {\n"
    ret = "    return;\n    // 0x80001084: nop\n"
    site = "    after_5:\nL_800019B4:\n    // 0x800019B4: lw          $ra, 0x28($sp)\n"
    if text.count(anchor) != 1 or text.count(ret) != 1 or text.count(site) != 1:
        return text, 0
    text = text.replace(anchor, helper + anchor, 1)
    text = text.replace(ret, "    rs64_g1d_heapcap(rdram); /* PATCH: s6631 heapcap carve */\n" + ret, 1)
    text = text.replace(
        site,
        "    after_5:\n    rs64_g1d_heapcap(rdram); /* PATCH: s6631 heapcap init */\n"
        "L_800019B4:\n    // 0x800019B4: lw          $ra, 0x28($sp)\n",
        1)
    return text, 1

def apply_s6689_heapslot(text):
    """s6689: ensureHeapInitialized's gap path builds the flags&4 heap over
    [slot, *801163E4 + fbsize) with the gap punched, i.e. it also takes the
    buffer at 801163E4. Retail 4:3 has gap 0 and never does. The wide carve
    makes 801163E4 the live depth image, so the game put a free block on the
    depth buffer and RT64's depth write-back overwrote its header (21:9 hangar
    SIGBUS 0x7FFF0002, s6688/s6689). Wider than 4:3, take the retail gap==0
    branch: heap = [slot, slot + fbsize). Needs apply_s6631_heapcap first
    (rs64_g1d_wide)."""
    # s6691: ROGUESQ_G1D_HEAPSLOT=0 restores the gap branch at wide aspect,
    # for a same-binary A/B of the 21:9 level-select tear.
    v1 = "    if (ctx->r3 != 0 && !rs64_g1d_wide()) { /* PATCH: s6689 heapslot */\n"
    v2 = ("    if (ctx->r3 != 0 && !(rs64_g1d_wide() && !(getenv(\"ROGUESQ_G1D_HEAPSLOT\") && "
          "getenv(\"ROGUESQ_G1D_HEAPSLOT\")[0] == '0'))) { /* PATCH: s6689 heapslot s6691 env */\n")
    if v2 in text:
        return text, 0
    if v1 in text:
        return text.replace(v1, v2, 1), 1
    old = ("    // 0x80001944: bne         $v1, $zero, L_8000197C\n"
           "    if (ctx->r3 != 0) {\n")
    new = "    // 0x80001944: bne         $v1, $zero, L_8000197C\n" + v2
    if text.count(old) != 1 or "static int rs64_g1d_wide(void)" not in text:
        return text, 0
    if text.index("static int rs64_g1d_wide(void)") > text.index(old):
        return text, 0
    return text.replace(old, new, 1), 1

# s6694 G1d: setupCameraMatrices builds G_SETSCISSOR lrx as (int)(w*4) & 0xFFF at two sites: 0x80017370
# (full-fb scissor from the video-state width 0x8011A838, set before the depth clear) and 0x80017814 (camera
# viewport scissor). The RDP field is 12-bit 10.2, so a 1024-wide fb (21:9) gives 0x1000 -> 0: the scissor is
# zero-wide, the depth-clear fill is clipped to nothing and the depth fb is never cleared (level-select floor
# tear). Clamp to 0xFFF (1023.75, the hardware maximum; covers pixel 1023). Retail widths (<=640) never reach it.
S6694_SITES = ("0x80017370", "0x80017814")
def apply_s6694_scissor(text):
    n = 0
    for pc in S6694_SITES:
        tag = "PATCH: s6694 scissor lrx clamp %s" % pc
        old = ("    // %s: andi        $v0, $v0, 0xFFF\n"
               "    ctx->r2 = ctx->r2 & 0XFFF;\n") % pc
        if tag in text or text.count(old) != 1:
            continue
        new = ("    // %s: andi        $v0, $v0, 0xFFF\n"
               "    if (SIGNED(ctx->r2) > 0xFFF) ctx->r2 = 0xFFF; /* %s */\n"
               "    ctx->r2 = ctx->r2 & 0XFFF;\n") % (pc, tag)
        text = text.replace(old, new, 1); n += 1
    return text, n

# s6718 G1d: the mission-intro flyover renders a 640x340 video state that FB_WIDTH never widened, so at 21:9 RT64
# pillarboxes it (227 px/side of 2720, s6717) and guPerspective's xASPECT_SCALE squeezes it horizontally. Widen the
# 640x340 state to intro_w = fbw*3/4 (768 at fbw 1024: the s6717 drawn 2266/2720 px -> 640/0.833) across pfm alloc,
# the video-state width, the 640 VI mode (upstream_compat.cpp), the 640 camera viewport and the perspective aspect
# (intro_w/640 instead of fbw/512). fbw*3/4 <= 640 (16:9) leaves the fb at 640 but still drops the perspective
# squeeze to 1.0. ROGUESQ_G1D_INTRO=0 restores the pre-s6718 path.
S6718_DECL = "extern int rs64_g1d_intro_w, rs64_g1d_vs_intro;\nstatic int rs64_s6718_on(void) { static int on = -1; if (on < 0) { const char* e = getenv(\"ROGUESQ_G1D_INTRO\"); on = !(e && *e == '0'); } return on; }\n"
def _decl(text, fn):
    if "rs64_s6718_on(void)" in text: return text
    a = text.find("RECOMP_FUNC void %s(" % fn); assert a > 0, fn
    return text[:a] + S6718_DECL + text[a:]
def apply_s6718_intro0(text):
    if "PATCH: s6718 intro pfm" in text: return text, 0
    old = '      if (wv > 0 && ow == 512 && (oh == 448 || oh == 340)) ctx->r6 = (gpr)wv; }\n'
    if text.count(old) != 1: return text, 0
    new = ('      if (wv > 0 && ow == 512 && (oh == 448 || oh == 340)) ctx->r6 = (gpr)wv;\n'
           '      { /* PATCH: s6718 intro pfm */ int wi = (wv > 0 && ow == 640 && oh == 340 && rs64_s6718_on()) ? ((wv * 3 / 4 + 7) & ~7) : 0; if (wi <= 640) wi = 0;\n'
           '        if (wi) ctx->r6 = (gpr)wi;\n'
           '        if (wi != rs64_g1d_intro_w) fprintf(stderr, "[g1d-intro] pfm %dx%d intro_w %d->%d\\n", ow, oh, rs64_g1d_intro_w, wi); rs64_g1d_intro_w = wi; } }\n')
    text = text.replace(old, new, 1)
    return _decl(text, "partitionFramebufferMemory"), 1
def apply_s6718_intro4(text):
    if "PATCH: s6718 intro vsu" in text: return text, 0
    n = 0
    old = '      if (wv > 0 && (int)ctx->r4 == 512 && ((int)ctx->r5 == 448 || (int)ctx->r5 == 340)) ctx->r4 = (gpr)wv; }\n'
    assert text.count(old) == 1
    text = text.replace(old, old +
        '    { /* PATCH: s6718 intro vsu */ int vi = rs64_s6718_on() && (int)ctx->r4 == 640 && (int)ctx->r5 == 340;\n'
        '      if (vi != rs64_g1d_vs_intro) fprintf(stderr, "[g1d-intro] vsu %dx%d vs_intro %d intro_w %d\\n", (int)ctx->r4, (int)ctx->r5, vi, rs64_g1d_intro_w);\n'
        '      rs64_g1d_vs_intro = vi; if (vi && rs64_g1d_intro_w > 640) ctx->r4 = (gpr)rs64_g1d_intro_w; }\n', 1); n += 1
    o_cam = "((int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000) <= 640 ? 1.0 / kv : "
    assert text.count(o_cam) == 2
    text = text.replace(o_cam, "(rs64_g1d_vs_intro && rs64_g1d_intro_w > 640 ? rs64_g1d_intro_w / 640.0 / kv : " + o_cam[1:]); n += 1
    o_asp = "af = (float)(af * k6104);"
    assert text.count(o_asp) == 1
    text = text.replace(o_asp, "af = (float)(af * (rs64_g1d_vs_intro ? (rs64_g1d_intro_w > 640 ? rs64_g1d_intro_w / 640.0 : 1.0) : k6104)); /* PATCH: s6718 intro persp */"); n += 1
    return _decl(text, "setupCameraMatrices"), n

# s6719 G1d: the 640x480 video state (boot logos: the 3D LucasArts logo over Hoth) is never widened, yet guPerspective
# still took xASPECT_SCALE there. Measured (s6719 dense window captures, settled-logo purple bbox w/h): retail 4:3
# 1.23; 21:9 default 2.13, 16:9 default 2.17 (drawn ~1.75x too wide; at 21:9 the face-on logo never shows); with
# ROGUESQ_ASPECT_SCALE=1 1.27 (21:9) / 1.16 (16:9). The 640 camera viewport already stays unscaled when the
# video-state width at 0x8011A838 is <= 640, so give the perspective the same rule: factor 1.0 there.
# ROGUESQ_G1D_640PERSP=0 restores the old factor.
S6719_OLD = ": k6104)); /* PATCH: s6718 intro persp */"
S6719_NEW = ": rs64_s6719_k(k6104, (int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000)))); /* PATCH: s6718 intro persp */ /* PATCH: s6719 persp640 */"
S6719_FN = ("static double rs64_s6719_k(double k, int w) { static int on = -1, lw = -1; if (on < 0) { const char* e = getenv(\"ROGUESQ_G1D_640PERSP\"); on = !(e && *e == '0'); }\n"
            "  double r = (on && w <= 640) ? 1.0 : k; if (w != lw) { lw = w; fprintf(stderr, \"[g1d-640p] fbw %d persp x%g (on %d)\\n\", w, r, on); } return r; }\n")
def apply_s6719_persp640(text):
    if "PATCH: s6719 persp640" in text:
        if "rs64_s6719_k(" in text: return text, 0
        # s6719 first cut (inline, no log) -> helper with a width-change log
        text = re.sub(r'static int rs64_s6719_on\(void\)[^\n]*\n', '', text, count=1)
        text = text.replace(": (rs64_s6719_on() && (int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000) <= 640 ? 1.0 : k6104))); /* PATCH: s6718 intro persp */ /* PATCH: s6719 persp640 */", S6719_NEW, 1)
    else:
        if text.count(S6719_OLD) != 1: return text, 0
        text = text.replace(S6719_OLD, S6719_NEW, 1)
    a = text.find("RECOMP_FUNC void setupCameraMatrices("); assert a > 0
    return text[:a] + S6719_FN + text[a:], 1

# s6791 G3f: ROGUESQ_G3F_CAM=<file> logs every setupCameraMatrices call just before guPerspective (after the far/aspect/vpw
# patches, so the args are what the game really passes): wall s, call n, cam ptr, viewport w/h, fovy (a2), aspect (a3), near,
# far, scale (sp+0x10/14/18) and the 12 floats at cam+0x2C (camera rotation rows + position fed to mat3x3InverseInto). Offline:
# tools/g3f_cam_scan.py. Unset = no cost beyond one cached getenv.
S6791_TAG = "/* PATCH: s6791 g3fcam */"
S6791 = ("    { " + S6791_TAG + " static FILE* f6791; static int i6791 = -1; static unsigned n6791; if (i6791 < 0) { const char* e = getenv(\"ROGUESQ_G3F_CAM\"); i6791 = (e && *e) ? 1 : 0; if (i6791) f6791 = fopen(e, \"w\"); if (!f6791) i6791 = 0; }\n"
         "      if (i6791) { extern double rs64_elapsed_seconds(void); union { uint32_t u; float f; } a, b, c, d, e, g; int k; a.u = (uint32_t)ctx->r6; b.u = (uint32_t)ctx->r7; c.u = MEM_W(0X10, ctx->r29); d.u = MEM_W(0X14, ctx->r29); e.u = MEM_W(0X18, ctx->r29);\n"
         "        fprintf(f6791, \"%.4f %u %08x %d %d %.6g %.6g %.6g %.6g %.6g\", rs64_elapsed_seconds(), n6791++, (unsigned)ctx->r17, (int)MEM_W(ctx->r17, 0X10), (int)MEM_W(ctx->r17, 0X14), a.f, b.f, c.f, d.f, e.f);\n"
         "        for (k = 0; k < 12; k++) { g.u = MEM_W(0X2C + 4 * k, ctx->r17); fprintf(f6791, \" %.6g\", g.f); } fputc('\\n', f6791); if ((n6791 & 63) == 0) fflush(f6791); } }\n")
def apply_s6791_g3fcam(text):
    if S6791_TAG in text: return text, 0
    a = text.find("RECOMP_FUNC void setupCameraMatrices("); assert a > 0
    i = text.find(OLD, a); assert i > 0
    return text[:i] + S6791 + text[i:], 1

# s6836 G3f opt-in: ROGUESQ_HANGAR_FOV=<deg> replaces the fovy (a2) that setupCameraMatrices passes to guPerspective for the
# SELECT YOUR CRAFT camera only (cam 0x800CD670; retail fovy 45 / aspect 1.882 = ~76 deg horizontal, s6791). The owner's
# "fish-eye" while scrolling ships is that wide retail lens. The pointer is per-screen stable (s6791 + s6836: SELECT LEVEL is
# 0x800CDC80 with the same 512x340 viewport, and narrowing it crops the holo table, so the knob does NOT key on the viewport).
# ROGUESQ_HANGAR_FOV_CAM=<hex>[,<hex>] retargets (e.g. 800CD670,800CDC80 for both). Inserted before the s6791 log so
# ROGUESQ_G3F_CAM records the value used. Clamped 10..90. Unset = retail (no change).
S6836_TAG = "/* PATCH: s6836 hangar fov */"
S6836 = ("    { " + S6836_TAG + " static int i6836 = -1; static float f6836; static uint32_t c6836[2] = { 0x800CD670u, 0u }; static unsigned n6836;\n"
         "      if (i6836 < 0) { const char* e = getenv(\"ROGUESQ_HANGAR_FOV\"); const char* c = getenv(\"ROGUESQ_HANGAR_FOV_CAM\"); char* q; i6836 = 0;\n"
         "        if (c && *c) { c6836[0] = (uint32_t)strtoul(c, &q, 16); if (*q == ',') c6836[1] = (uint32_t)strtoul(q + 1, NULL, 16); }\n"
         "        if (e && *e) { double v = atof(e); if (v > 0.0) { if (v < 10.0) v = 10.0; if (v > 90.0) v = 90.0; f6836 = (float)v; i6836 = 1; fprintf(stderr, \"[hangar-fov] cam %08x %08x fovy -> %g\\n\", (unsigned)c6836[0], (unsigned)c6836[1], v); } } }\n"
         "      if (i6836 && ((uint32_t)ctx->r17 == c6836[0] || (c6836[1] && (uint32_t)ctx->r17 == c6836[1]))) { union { uint32_t u; float f; } o, n; o.u = (uint32_t)ctx->r6; n.f = f6836; ctx->r6 = (int32_t)n.u;\n"
         "        if (n6836++ == 0) fprintf(stderr, \"[hangar-fov] first hit cam %08x: fovy %g -> %g\\n\", (unsigned)ctx->r17, o.f, n.f); } }\n")
def apply_s6836_hangarfov(text):
    a = text.find("RECOMP_FUNC void setupCameraMatrices("); assert a > 0
    if S6836_TAG in text:
        i = text.find("    { " + S6836_TAG, a); j = text.find("\n", text.find("} }\n", text.find("first hit", i)))  # end of old block
        old = text[i:j + 1]
        if old == S6836: return text, 0
        text = text[:i] + text[j + 1:]
    i = text.find("    { /* PATCH: s6031 far */", a)
    if i < 0: i = text.find(OLD, a)
    assert i > 0
    return text[:i] + S6836 + text[i:], 1

# s6841 G3: initVideoSubsystem (funcs_5.c) clears each new video buffer with rs_memset(buf, 0, w*h*bpp) using the
# NATIVE width (512). Under G1d (ROGUESQ_FB_WIDTH=wv>512) the buffer is wv wide, so the clear covers only the top
# 512/wv of it: at 21:9 the hangar buffer 0xB20000 (= the flight depth image) kept the flight Z in its lower half and
# the first hangar VI showed it as magenta/yellow stripes under a black top half (s6798 w133, s6841 p21x 591/1181 rows).
# Widen the length to wv*h*bpp. ROGUESQ_IVS_WIDE_CLEAR=0 restores the native length; ROGUESQ_LOG_IVS_CLEAR=1 logs calls.
S6841_TAG = "/* PATCH: s6841 ivsclear */"
S6841_OLD = "    ctx->r6 = ADD32(ctx->r16, 0);\n    rs_memset(rdram, ctx);\n"
S6841 = ('    ctx->r6 = ADD32(ctx->r16, 0);\n'
         '    { ' + S6841_TAG + ' static int wv = -1, md = 1, lg = 0, nl; if (wv < 0) { const char* e = getenv("ROGUESQ_FB_WIDTH"); wv = (e && *e) ? atoi(e) : 0;\n'
         '        e = getenv("ROGUESQ_IVS_WIDE_CLEAR"); if (e && *e) md = atoi(e); e = getenv("ROGUESQ_LOG_IVS_CLEAR"); lg = (e && *e && *e != \'0\'); }\n'
         '      int w = (int16_t)ctx->r19, h = (int16_t)ctx->r20, bpp = ((int16_t)ctx->r22 < 0x18) ? 2 : 4; uint32_t len = U32(ctx->r6), nlen = len;\n'
         '      if (md && wv > 512 && w == 512 && (h == 448 || h == 340) && len == (uint32_t)(w * h * bpp)) nlen = (uint32_t)(wv * h * bpp);\n'
         '      if (lg && nl < 64) { fprintf(stderr, "[ivs-clear] n=%d dst=0x%08X len=0x%X -> 0x%X w=%d h=%d bpp=%d wv=%d ra=0x%08X\\n", nl, U32(ctx->r4), len, nlen, w, h, bpp, wv, U32(ctx->r31)); fflush(stderr); nl++; }\n'
         '      ctx->r6 = (gpr)(int32_t)nlen; }\n'
         '    rs_memset(rdram, ctx);\n')
def apply_s6841_ivsclear(text):
    a = text.find("RECOMP_FUNC void initVideoSubsystem("); assert a > 0
    b = text.find("RECOMP_FUNC", a + 10)
    if S6841_TAG in text[a:b]: return text, 0
    i = text.find(S6841_OLD, a); assert 0 < i < b and "0x8001A2E8" in text[i - 200:i], "s6841 anchor"
    return text[:i] + S6841 + text[i + len(S6841_OLD):], 1

if __name__ == "__main__":
    p = base / "funcs_4.c"; t = p.read_text(); t2, n = apply4(t)
    t2, m = apply_s6201_pool(t2)
    t2, q = apply_s6204_poolclass(t2)
    t2, sc = apply_s6694_scissor(t2)
    t2, ii = apply_s6718_intro4(t2); sc += ii
    t2, ii = apply_s6719_persp640(t2); sc += ii
    t2, ii = apply_s6791_g3fcam(t2); sc += ii
    t2, ii = apply_s6836_hangarfov(t2); sc += ii
    if n or m or q or sc: p.write_text(t2)
    print("funcs_4.c live patched x%d pool=%d poolclass=%d scissor=%d" % (n, m, q, sc))
    p0 = base / "funcs_0.c"; t = p0.read_text(); t2, n = applypfm(t)
    t2, c = apply_s6201_carve(t2)
    t2, r = apply_s6202_retarget(t2)
    t2, rr = apply_s7482_reserve(t2); r += rr
    t2, h = apply_s6203_heapclass(t2)
    t2, d = apply_s6207_drop(t2)
    t2, cap = apply_s6631_heapcap(t2)
    t2, hs = apply_s6689_heapslot(t2)
    t2, ip = apply_s6718_intro0(t2); hs += ip
    if n or c or r or h or d or cap or hs: p0.write_text(t2)
    print("funcs_0.c live patched x%d carve=%d retarget=%d heapclass=%d drop=%d heapcap=%d heapslot=%d" % (n, c, r, h, d, cap, hs))
    p3 = base / "funcs_3.c"; t = p3.read_text(); t2, k = apply_s6201_alloc(t)
    if k: p3.write_text(t2)
    print("funcs_3.c alloc=%d" % k)
    p5 = base / "funcs_5.c"; t = p5.read_text(); t2, k5 = apply_s6841_ivsclear(t)
    if k5: p5.write_text(t2)
    print("funcs_5.c ivsclear=%d" % k5)
