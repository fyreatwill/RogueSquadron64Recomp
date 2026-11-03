#!/usr/bin/env python3
"""s6845: drawSubtitleText -> drawTextGlyphRect argument probe.  Before each of the two drawTextGlyphRect call sites
(0x8001665C, 0x80016ABC) calls rs64_s6845_glyph(site, a1=ulx, a2=uly, a3=lrx, sp+0x10=lry, s3=text object, s1=arg,
fp=width term, sp+0x46/0x4E = base x/y) in src/main/main.cpp, which logs `[glyph]` lines while the VI counter is inside
ROGUESQ_WIPE_SCAN=<vi_lo>:<vi_hi> (plus the object's float x/y at +0x18/+0x1C, scale +0x24/+0x28, the arg's int x/y at
+0x18/+0x1C and the screen width word 0x8011A838).  Names the input behind the 21:9 abort-wipe x shift.  Diagnostic only;
zero cost when the env is unset beyond one load.  Idempotent.
Usage: apply_s6845_glyph_probe.py [RecompiledFuncs dir]
"""
import sys, pathlib, re
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
decl = "extern int rs64_s6845_on; extern void rs64_s6845_base(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t); extern void rs64_s6845_entry(uint8_t*, uint32_t, uint32_t); extern void rs64_s6845_glyph(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "PATCH: s6845 glyph probe" in s or "PATCH: s6845 entry probe" in s:
        continue
    hit = False
    for site in ("0x8001665C", "0x80016ABC"):
        pat = re.compile(r"(    // " + site + r": jal         0x80015708\n(?:.*\n)*?)(    drawTextGlyphRect\(rdram, ctx\);\n)")
        m = pat.search(s)
        if not m:
            continue
        probe = ("    if (__builtin_expect(rs64_s6845_on, 0)) rs64_s6845_glyph(rdram, %su, ctx->r5, ctx->r6, ctx->r7, MEM_W(0X10, ctx->r29), "
                 "ctx->r19, ctx->r17, ctx->r30, MEM_HU(ctx->r29, 0X46), MEM_HU(ctx->r29, 0X4E)); /* PATCH: s6845 glyph probe */\n" % site)
        s = s[:m.start(2)] + probe + s[m.start(2):]
        hit = True
    ent = "RECOMP_FUNC void drawSubtitleText(uint8_t* rdram, recomp_context* ctx) {\n"
    if s.count(ent) == 1:  # s6845b: entry probe, arg1 (a1) = the screen struct whose +0x18 is the 2D x centre
        s = s.replace(ent, ent + "    if (__builtin_expect(rs64_s6845_on, 0)) rs64_s6845_entry(rdram, ctx->r4, ctx->r5); /* PATCH: s6845 entry probe */\n", 1)
        hit = True
    bk = "    // 0x800160E4: sh          $t2, 0x46($sp)\n"
    if s.count(bk) == 1:  # s6845c: base-x store: obj (s3), screen (s1), t2 = trunc base, f4 = (obj.x + scr.cx) * f6, f6 scale
        s = s.replace(bk, '    if (__builtin_expect(rs64_s6845_on, 0)) rs64_s6845_base(rdram, ctx->r19, ctx->r17, ctx->r10, ctx->f4.u32l, ctx->f6.u32l); /* PATCH: s6845 base probe */\n' + bk, 1)
        hit = True
    if hit:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
        p.write_text(s); n += 1
print("s6845 glyph probe: %d files" % n)
