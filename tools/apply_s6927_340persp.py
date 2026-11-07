#!/usr/bin/env python3
"""s6927 G1d: at wide aspect the 3D in the 512x340 hangar screens (SELECT LEVEL cam 0x800CDC80, SELECT YOUR CRAFT cam 0x800CD670) was 26% narrow
against 4:3. ORIGIN: ours. s6104 multiplies the guPerspective aspect by fbw/512 in every widened state, which keeps a 3D object's width in columns.
That holds for 512x448 states, whose rows fill the window height at 4:3 too. A 340-row state is letterboxed at 4:3 (picture box 1.534) but fills the
window height at wide, so rows grow while columns do not. Rule: factor = fbw/687.2 (= (fbw/448)/1.534) when the camera viewport is 340 rows in a
widened state. 16:9 1.158, 21:9 1.490. The 640x340 intro state keeps its own rule. ROGUESQ_G1D_340PERSP default on, =0 old. 4:3 never reaches it.
Runs after apply_s6031_far (s6719 persp640) in RS64_REPLAY.
Usage: apply_s6927_340persp.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6927 340persp"
OLD = "rs64_s6719_k(k6104, (int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000))"
NEW = "rs64_s6927_k(" + OLD + ", (int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000), (int32_t)MEM_W(0X14, ctx->r17)) /* " + TAG + " */"
FN = ("static double rs64_s6927_k(double k, int w, int h) { static int on = -1; static double lr = -1.0; if (on < 0) { const char* e = getenv(\"ROGUESQ_G1D_340PERSP\"); on = !(e && *e == '0'); }\n"
      "  double r = (on && k > 1.0 && w > 640 && h == 340) ? w / 687.2 : k; if (r != lr) { lr = r; fprintf(stderr, \"[g1d-340p] fbw %d h %d persp x%g (on %d)\\n\", w, h, r, on); } return r; } /* " + TAG + " */\n")
f = D / "funcs_4.c"
t = f.read_text(errors="surrogateescape")
if TAG in t:
    print("already applied", TAG); sys.exit(0)
assert t.count(OLD) == 1, t.count(OLD)
t = t.replace(OLD, NEW, 1)
a = t.find("RECOMP_FUNC void setupCameraMatrices("); assert a > 0
t = t[:a] + FN + t[a:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
