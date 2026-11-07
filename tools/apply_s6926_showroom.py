#!/usr/bin/env python3
"""s6926 G5h: SHOWROOM (and any other 512x300 screen) at wide aspect was cut at 512/fbw of the window. ORIGIN: ours. The s6113/s6115 widen list
holds 512x448 and 512x340 only, so this state kept a 512 colour image while s6720 title-vi (keyed on the VI mode, not the state) widened the VI to
2*fbw. Adds h == 300 to the three lists: partitionFramebufferMemory, the video state update and the s6841 clear. ROGUESQ_G1D_SHOWROOM default on, =0 old.
Records the height for rs64_g1d_title_clear, which assumed 448 rows. Runs after apply_s6841/s6718 in RS64_REPLAY.
Usage: apply_s6926_showroom.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6926 showroom"
DECL = "extern int rs64_s6926_on(void); extern int rs64_g1d_pfm_h; /* " + TAG + " */\n"
E = [("funcs_0.c", "partitionFramebufferMemory",
      "      if (wv > 0 && ow == 512 && (oh == 448 || oh == 340)) ctx->r6 = (gpr)wv;\n",
      "      rs64_g1d_pfm_h = oh; if (wv > 0 && ow == 512 && (oh == 448 || oh == 340 || (oh == 300 && rs64_s6926_on()))) ctx->r6 = (gpr)wv;\n"),
     ("funcs_4.c", None,
      "      if (wv > 0 && (int)ctx->r4 == 512 && ((int)ctx->r5 == 448 || (int)ctx->r5 == 340)) ctx->r4 = (gpr)wv; }\n",
      "      if (wv > 0 && (int)ctx->r4 == 512 && ((int)ctx->r5 == 448 || (int)ctx->r5 == 340 || ((int)ctx->r5 == 300 && rs64_s6926_on()))) ctx->r4 = (gpr)wv; }\n"),
     ("funcs_5.c", "initVideoSubsystem",
      "      if (md && wv > 512 && w == 512 && (h == 448 || h == 340) && len == (uint32_t)(w * h * bpp)) nlen = (uint32_t)(wv * h * bpp);\n",
      "      if (md && wv > 512 && w == 512 && (h == 448 || h == 340 || (h == 300 && rs64_s6926_on())) && len == (uint32_t)(w * h * bpp)) nlen = (uint32_t)(wv * h * bpp);\n")]
for name, fn, old, new in E:
    f = D / name
    t = f.read_text(errors="surrogateescape")
    if TAG in t: print("already applied", name); continue
    assert t.count(old) == 1, (name, t.count(old))
    t = t.replace(old, new, 1)
    a = t.find("RECOMP_FUNC void %s(" % fn) if fn else t.rfind("RECOMP_FUNC", 0, t.find(new))
    assert a > 0, name
    t = t[:a] + DECL + t[a:]
    f.write_text(t, errors="surrogateescape"); print("applied", TAG, name)
