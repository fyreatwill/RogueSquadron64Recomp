#!/usr/bin/env python3
"""s6903 G5d: at dd>1 the boot cinematic (cinematicLoopBody a0=0x13, gCurrentLevel 0x80130B70 = 0x13, a 32x32 terrain map) lost picture: the carved LucasArts
logo was cut by the window clamp and the Factor 5 letters vanished while the frame rate stayed full. ORIGIN: our own dd levers, all meant for mission flight.
Retail's window on that map already runs past the area cap (29x23 on cap 400), so s6037/s6901 trim or re-place on-map cells; s6529 span bypass, s6789 sentinel fix and
the s6073 far scale each separately decide the letters (one lever off restores them on a retail window, s6903 arms g1 g3 g4).
Fix: all of these follow g_rs64_dd_scene, 1 for levels 0..18, refreshed at the s6036 hook. Sentinel levels run the retail terrain path. dd1 is unchanged.
ROGUESQ_DD_CINE_GATE=0 old, =tog 4 s blocks. Runs after apply_s6902_fwdtog in RS64_REPLAY.  Usage: apply_s6903_cinegate.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6903 cinegate"
f9 = D / "funcs_9.c"; f4 = D / "funcs_4.c"
t = f9.read_text(errors="surrogateescape"); u = f4.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
def sub(s, a, b, n=1):
    assert s.count(a) == n, (a, s.count(a))
    return s.replace(a, b)
t = sub(t, "static inline int s6523_scale(void) { /* PATCH: s6523 spanscale */\n",
        "extern volatile int g_rs64_dd_scene; int rs64_dd_scene_update(int level); /* " + TAG + " */\nstatic inline int s6523_scale(void) { /* PATCH: s6523 spanscale */\n")
t = sub(t, "      { extern volatile int g_rs64_dd_blk; g_rs64_dd_blk = (me6036 != 1.0f); }\n",
        "      g_rs64_dd_scene = rs64_dd_scene_update((int32_t)MEM_W(0, (int64_t)(int32_t)0x80130B70)); if (!g_rs64_dd_scene) me6036 = 1.0f; /* " + TAG + " */\n"
        "      { extern volatile int g_rs64_dd_blk; g_rs64_dd_blk = (me6036 != 1.0f); }\n")
t = sub(t, "  if (e != 2) return e;\n  int n = rs64_swap_n(); int ph = n > 0", "  if (e != 2) return e && g_rs64_dd_scene;\n  int n = rs64_swap_n(); int ph = n > 0")
t = sub(t, "  if (!on) return 0; if (tog <= 0) return 1;\n", "  if (!on || !g_rs64_dd_scene) return 0; if (tog <= 0) return 1;\n")
t = sub(t, "      extern double rs64_s6879_fpk; const int wide6879 = !on6037 && rs64_s6879_fpk != 1.0;\n      if ((on6037 || wide6879) && MEM_W(4,",
        "      const int dd6903 = on6037 && g_rs64_dd_scene;\n      extern double rs64_s6879_fpk; const int wide6879 = !dd6903 && rs64_s6879_fpk != 1.0;\n      if ((dd6903 || wide6879) && MEM_W(4,")
t = sub(t, "            if (on6037 && edge6874 && px1 > px0", "            if (dd6903 && edge6874 && px1 > px0")
u = sub(u, "double mf = rs6031_far(), mn = rs6031_env(\"ROGUESQ_DD_NEAR\");",
        "extern volatile int g_rs64_dd_scene; double mf = g_rs64_dd_scene ? rs6031_far() : 0.0, mn = rs6031_env(\"ROGUESQ_DD_NEAR\"); /* " + TAG + " */")
f9.write_text(t, errors="surrogateescape"); f4.write_text(u, errors="surrogateescape"); print("applied", TAG)
