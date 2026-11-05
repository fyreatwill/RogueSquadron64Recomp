#!/usr/bin/env python3
"""s6898 G5b: black block in in-mission letterboxed cutscenes at wide aspects (s6897). ORIGIN: setupMissionTransitionScreenOverlay
(0x800FB2F8) passes setScreenColorOverlay a window whose right edge a3 is getBootConfigField12 (0x8006B3D0, boot config width at
0x80037572, 512, never widened). emitColorFillRect fills outside the window, so the right band runs from 512 to the real frame
width 0x8011A838: RDP FILL 512..796 y 54..393 colour 0001 at 16:9 (scratch/s6898 r1.bin). At retail W = 512 the band is empty.
The value is legitimate for retail; only our widening makes it wrong. Fix: at this one call site a3 = W on a widened frame.
The other 21 getter callers are not touched. ROGUESQ_G1D_LETTERBOX=0 = old. Usage: apply_s6898_letterbox.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6898 letterbox"
f = D / "funcs_42.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
HEAD = "RECOMP_FUNC void setupMissionTransitionScreenOverlay(uint8_t* rdram, recomp_context* ctx) {"
A = "    // 0x800FB420: addu        $a3, $s1, $zero\n    ctx->r7 = ADD32(ctx->r17, 0);\n"
assert t.count(A) == 1 and t.count(HEAD) == 1
t = t.replace(A, A + "    ctx->r7 = (gpr)(int32_t)rs64_s6898_ovl_x1(U32(ctx->r7), (uint32_t)(int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000)); /* %s */\n" % TAG, 1)
t = t.replace(HEAD, "/* %s */ extern uint32_t rs64_s6898_ovl_x1(uint32_t, uint32_t);\n" % TAG + HEAD, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
