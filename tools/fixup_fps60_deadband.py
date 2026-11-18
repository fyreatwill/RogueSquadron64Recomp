#!/usr/bin/env python3
"""s6876 G3 FPS60: attitude dead-band test. updatePlayerCraftPhysics turns its rates +0xD8/+0xDC/+0xE0 into per-tick angles (x dt at
0x800B2438), then zeroes each one below rodata 0x800A5778 (0.1) at 0x800B3358. The threshold is per tick, so the rate it stops at is
0.1/dt: 3 deg/s at 1/30, 6 deg/s at 1/60. ROGUESQ_FPS60_DEADBAND=1 scales the threshold by dt*30, so every dt stops at the 1/30 rate.
Default off. s6876 result: this is NOT the source of the dt-dependent camera pitch (0.06316 vs 0.06055): the knob changes the later path
at 1/60 and 1/20 (2101/3796 camera rows common against a 3794/3796 repeat floor) and leaves that pitch unchanged. Idempotent.
Usage: fixup_fps60_deadband.py <RecompiledFuncs dir>"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import rs64_anchor  # s7558

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6876 fps60 deadband */"
HEAD = "RECOMP_FUNC void updatePlayerCraftPhysics(uint8_t* rdram, recomp_context* ctx) {\n"
HELPER = ("extern char* getenv(const char*); static float rs64_deadband_scale(uint32_t w) { static int on = -1; if (on < 0) { "
          "const char* s = getenv(\"ROGUESQ_FPS60_DEADBAND\"); on = s && *s && *s != '0'; } if (!on) return 1.0f; "
          "union { uint32_t u; float f; } d; d.u = w; return d.f * 30.0f; } " + TAG + "\n")
LOAD = "    ctx->f2.u32l = MEM_W(ctx->r1, 0X5778);\n"
done = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    if HEAD not in s:
        continue
    done += 1
    if TAG in s:
        continue
    i = s.index(HEAD)
    a = s.index("// 0x800B3358:", i)
    sp = rs64_anchor.span(s, LOAD, a)  # s7558: tolerate the s7484 load wrap
    if sp is None or sp[0] - a > 80:
        sys.exit("s6876 fps60 deadband: load not found at 0x800B3358")
    b = sp[1]
    s = s[:b] + "    ctx->f2.fl *= rs64_deadband_scale((uint32_t)MEM_W(0X1DC, ctx->r29)); " + TAG + "\n" + s[b:]
    s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + HELPER, 1)
    p.write_text(s)
if done != 1:
    sys.exit(f"s6876 fps60 deadband: updatePlayerCraftPhysics found in {done} files (want 1)")
print("[s6876] fps60 dead-band knob patched")
