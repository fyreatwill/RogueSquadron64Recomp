#!/usr/bin/env python3
"""s6826 G3 FPS60: per-tick float quanta in the guided-craft motion helpers (tools/g3_float_quanta_audit.py +
g3_float_quanta_rates.py: executions per game s x2 at FPS60 with the SAME change per execution, dR 1.00, where dt-scaled
fields read 0.50).
  steerOrientationTowardTarget    0x8005F3D4  accel +0x5C += 0.4 (rodata 0x8003B220) per tick
                                  0x8005F3E0  speed +0x58 += accel per tick (then clamped to +0x6C; vel = dir*speed,
                                              position += vel*dt elsewhere, dt-exact)
  levelOrientationToReferenceAxis 0x8005F624  drop term +0x5C += const (rodata 0x8003B244) per tick, added to vel.y
At FPS60 both accumulations run twice per game second, so the speed ramp (s6816: guided missiles are the lvl14 hp source)
and the drop velocity grow about 2x/4x faster in game time. Under ROGUESQ_FPS60 the three increments are multiplied by
k = dt*30 (dt = rs64_tick_dt, the tick's game dt captured at 0x800FA90C by fixup_fps60_despawn.py; k = 1 at dt >= 1/30).
ROGUESQ_FPS60_FQUANTA=0 restores. Retail (no FPS60) unchanged. Idempotent; run after fixup_fps60_despawn.py.
Usage: fixup_fps60_float_quanta.py <RecompiledFuncs dir>"""
import pathlib, sys

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6826 fps60 float quanta */"
HELPER = ("extern char* getenv(const char*); extern float rs64_tick_dt; static float rs64_fq_k(void) { static int on = -1; "
          "if (on < 0) { const char* f = getenv(\"ROGUESQ_FPS60\"); const char* q = getenv(\"ROGUESQ_FPS60_FQUANTA\"); "
          "on = f && *f && *f != '0' && !(q && *q == '0'); } float dt = rs64_tick_dt; "
          "return (on && dt > 0.0f && dt < (1.0f / 30.0f)) ? dt * 30.0f : 1.0f; } " + TAG + "\n")
SITES = [  # (comment line, old C, new C)
    ("    // 0x8005F3D4: add.s       $f0, $f0, $f2\n", "    ctx->f0.fl = ctx->f0.fl + ctx->f2.fl;\n",
     "    ctx->f0.fl = ctx->f0.fl + ctx->f2.fl * rs64_fq_k(); " + TAG + "\n"),
    ("    // 0x8005F3E0: add.s       $f2, $f2, $f0\n", "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_k(); " + TAG + "\n"),
    ("    // 0x8005F624: add.s       $f2, $f2, $f0\n", "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_k(); " + TAG + "\n"),
]
done = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    if SITES[0][0] not in s:
        continue
    for com, old, new in SITES:
        if s.count(com) != 1:
            sys.exit(f"s6826 fps60 float quanta: {com.strip()} found {s.count(com)}x in {p.name}")
        i = s.index(com)
        j = s.index("\n    // 0x", i + len(com)) + 1
        seg = s[i:j]
        if new in seg:
            continue
        if seg.count(old) != 1:
            sys.exit(f"s6826 fps60 float quanta: unexpected C after {com.strip()} in {p.name}")
        s = s[:i] + seg.replace(old, new) + s[j:]
    if HELPER not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + HELPER, 1)
    p.write_text(s)
    done += 1
if done != 1:
    sys.exit(f"s6826 fps60 float quanta: site file found {done}x (want 1)")
print(f"[s6826] fps60 float quanta: {len(SITES)} guided-motion increments scaled by dt*30 under ROGUESQ_FPS60")
