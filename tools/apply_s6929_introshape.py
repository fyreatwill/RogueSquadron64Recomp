#!/usr/bin/env python3
"""s6929 G1d: under ROGUESQ_VI_SHAPE the 640x340 mission intro widens by the wrong rule. ORIGIN: ours. s6718 sets intro_w = fbw*3/4, which assumes
fbw 1024 at 21:9 (768). VI_SHAPE moved 21:9 to fbw 856, so intro_w fell to 648, a 640.5x334 box in a 2.33 window: the s6718 side bars came back.
A 640-family column is one dot wide on 334 half-lines, so the width that keeps the flight box is fbw*1.25*334/458. 21:9 784, 16:9 594 (not widened, as
before). VI_SHAPE off is untouched. ROGUESQ_G1D_INTROSHAPE=0 = s6718 rule under VI_SHAPE.
Runs after apply_s6031_far (s6718 intro pfm) in RS64_REPLAY.
Usage: apply_s6929_introshape.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6929 introshape"
OLD = "((wv * 3 / 4 + 7) & ~7)"
NEW = "rs64_s6929_iw(wv) /* " + TAG + " */"
FN = ("static int rs64_s6929_iw(int wv) { static int on = -1; if (on < 0) { const char* v = getenv(\"ROGUESQ_VI_SHAPE\"); const char* e = getenv(\"ROGUESQ_G1D_INTROSHAPE\");"
      " on = v && *v && *v != '0' && !(e && *e == '0'); }\n"
      "  return on ? (((int)(wv * 1.25 * 334.0 / 458.0) + 4) & ~7) : ((wv * 3 / 4 + 7) & ~7); }\n")
f = D / "funcs_0.c"
t = f.read_text(errors="surrogateescape")
if TAG in t:
    print("already applied", TAG); sys.exit(0)  # one script, both halves land together
assert t.count(OLD) == 1, t.count(OLD)
t = t.replace(OLD, NEW, 1)
a = t.find("RECOMP_FUNC void partitionFramebufferMemory("); assert a > 0
a = t.rfind("extern int rs64_g1d_intro_w", 0, a) if "extern int rs64_g1d_intro_w" in t[:a] else a
t = t[:a] + FN + t[a:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)

# Second half: the "<= 640 means a 640 state" gates. s6719 keyed the 640-family rule on width <= 640, true while every widened 512 state was above 640.
# VI_SHAPE puts a 16:10 display at fbw 564: that 512-family state took the 640 rule, so only 512 columns were drawn and the rest showed RAM noise.
# A 640 state is exactly 640 (main.cpp keeps fbw off 640 under VI_SHAPE), so the gate is w <= 512 or w == 640. Inert at fbw > 640. ROGUESQ_G1D_W640=0 = old.
TAG2 = "PATCH: s6929 w640"
FN2 = ("static int rs64_s6929_w640(int w) { static int on = -1; if (on < 0) { const char* e = getenv(\"ROGUESQ_G1D_W640\"); on = !(e && *e == '0'); }\n"
       "  return on ? (w <= 512 || w == 640) : w <= 640; } /* " + TAG2 + " */\n")
f = D / "funcs_4.c"
t = f.read_text(errors="surrogateescape")
assert TAG2 not in t
o1 = "double r = (on && w <= 640) ? 1.0 : k;"
o2 = "(int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000) <= 640 ? 1.0 / kv : "
assert t.count(o1) == 1 and t.count(o2) == 2, (t.count(o1), t.count(o2))
t = t.replace(o1, "double r = (on && rs64_s6929_w640(w)) ? 1.0 : k;", 1)
t = t.replace(o2, "rs64_s6929_w640((int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000)) ? 1.0 / kv : ")
a = t.rfind("\n", 0, t.find("static double rs64_s6719_k(")) + 1; assert a > 0
t = t[:a] + FN2 + t[a:]
f.write_text(t, errors="surrogateescape")
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
o3 = "w6719 <= 640 ? 1.0 : kx6144;"
assert t.count(o3) == 1
t = t.replace(o3, "rs64_s6929_w640(w6719) ? 1.0 : kx6144;", 1)
a = t.rfind("RECOMP_FUNC void ", 0, t.find("rs64_s6929_w640(w6719)")); assert a > 0
t = t[:a] + FN2 + t[a:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG2)
