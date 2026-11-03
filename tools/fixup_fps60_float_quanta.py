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
s6827 adds (same k, same switch):
  minimalRandomNpcHandler         0x80060F38/F40  particle scale +0x20/+0x24 *= 1.1 (rodata 0x8003B364) per tick while
                                              alpha +0x44 -= 512*dt -> pow(1.1, k), so a puff's size at a given age is
                                              rate-independent (FPS60 grew it 1.1^60 per game s instead of 1.1^30)
  computeRandomizedOrientationFrame 0x800F3730  effect orientation phase +0x8C += +0x48*0.25*+0x74 per tick (to 1.0)
                                    0x800F3914  effect orientation phase +0xA4 += +0x78 per tick (to 1.0)
                                              (executeActorType1Effect wobble ran at 2x frequency at FPS60)
s6828 adds (same k, same switch): two of the five updatePlayerVehicleByControlMode (0x8004D2B0) callers pass a CONSTANT
step dt of 1/30 s (rodata 0x8003A9AC / 0x8003A9B0) as a1, which the callee multiplies into speed ramp (+0x98 +=
+0x9C*a1) and position (+0x10/14/18 += speed*a1*dir):
  releaseEffectObjectNpcSlots        0x8004EF38  mfc1 a1, f20 (f20 = 1/30)  -> a1 = 1/30 * k
  releaseEffectObjectNpcSlotsVariant 0x8004F160  mfc1 a1, f20 (f20 = 1/30)  -> a1 = 1/30 * k
The other three (destroyEffectObjectTypeNpcSlots 0x8004F990/FA54/FB24) pass their caller's f12 dt and are left alone.
Classified, left alone: timeSnapshotFiller 0x8000BD88 (0x8012A8F4 += 1 is the sample count of a running average whose
sum is accumulated per call too = benign).
s6829 adds (same switch): hangarVehicleDisplayNpcHandler (0x800C68A0) ship tilt angles +0x8 / +0xC (fed to 0x800193E8 as
rotation angles with +0x10): per call += stick*c (0x800C6BD0 x, 0x800C6C34 y), clamped, then decayed toward 0 by a
constant (0x800C6CBC/CD4 +0x8, 0x800C6D0C/D24 +0xC). The handler gets a pointer to its frame dt in a2 (s3; +0x14 -= *s3
at 0x800C6D40), outside the mission tick, so k here = (*s3)*30, not rs64_tick_dt.
s6830 adds (same k, same switch): updateSplineCraftTransform (0x800B0A88) speed +0x140 += 2.0 (0x800B0EF4, rodata
0x800A565C, clamp 180) or -= 2.0 (0x800B0F14, 0x800A5664, clamp -180) per tick, position += speed*dt; scale +0xE8 *=
1.01 per tick (0x800B0BB0, rodata 0x800A5640) -> pow(1.01, k).
ROGUESQ_FPS60_FQUANTA=0 restores. Retail (no FPS60) unchanged. Idempotent; run after fixup_fps60_despawn.py.
Usage: fixup_fps60_float_quanta.py <RecompiledFuncs dir>"""
import pathlib, sys

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6826 fps60 float quanta */"
HELPER = ("extern char* getenv(const char*); extern float powf(float, float); extern float rs64_tick_dt; static float rs64_fq_kd(float dt) { static int on = -1; "
          "if (on < 0) { const char* f = getenv(\"ROGUESQ_FPS60\"); const char* q = getenv(\"ROGUESQ_FPS60_FQUANTA\"); "
          "on = f && *f && *f != '0' && !(q && *q == '0'); } "
          "return (on && dt > 0.0f && dt < (1.0f / 30.0f)) ? dt * 30.0f : 1.0f; } static float rs64_fq_k(void) { return rs64_fq_kd(rs64_tick_dt); } "
          "static float rs64_fq_kp(uint8_t* rdram, gpr p) { uint32_t u = MEM_W(0, p); float f; __builtin_memcpy(&f, &u, 4); return rs64_fq_kd(f); } "
          + TAG + "\n")
SITES = [  # (comment line, old C, new C)
    ("    // 0x8005F3D4: add.s       $f0, $f0, $f2\n", "    ctx->f0.fl = ctx->f0.fl + ctx->f2.fl;\n",
     "    ctx->f0.fl = ctx->f0.fl + ctx->f2.fl * rs64_fq_k(); " + TAG + "\n"),
    ("    // 0x8005F3E0: add.s       $f2, $f2, $f0\n", "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_k(); " + TAG + "\n"),
    ("    // 0x8005F624: add.s       $f2, $f2, $f0\n", "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_k(); " + TAG + "\n"),
    ("    // 0x80060F38: mul.s       $f4, $f4, $f0\n", "    ctx->f4.fl = MUL_S(ctx->f4.fl, ctx->f0.fl);\n",
     "    ctx->f4.fl = MUL_S(ctx->f4.fl, powf(ctx->f0.fl, rs64_fq_k())); " + TAG + "\n"),
    ("    // 0x80060F40: mul.s       $f2, $f2, $f0\n", "    ctx->f2.fl = MUL_S(ctx->f2.fl, ctx->f0.fl);\n",
     "    ctx->f2.fl = MUL_S(ctx->f2.fl, powf(ctx->f0.fl, rs64_fq_k())); " + TAG + "\n"),
    ("    // 0x800F3730: add.s       $f2, $f2, $f0\n", "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_k(); " + TAG + "\n"),
    ("    // 0x800F3914: add.s       $f2, $f2, $f0\n", "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_k(); " + TAG + "\n"),
    ("    // 0x8004EF38: mfc1        $a1, $f20\n", "    ctx->r5 = (int32_t)ctx->f20.u32l;\n",
     "    { float a1 = ctx->f20.fl * rs64_fq_k(); uint32_t u; __builtin_memcpy(&u, &a1, 4); ctx->r5 = (int32_t)u; } " + TAG + "\n"),
    ("    // 0x8004F160: mfc1        $a1, $f20\n", "    ctx->r5 = (int32_t)ctx->f20.u32l;\n",
     "    { float a1 = ctx->f20.fl * rs64_fq_k(); uint32_t u; __builtin_memcpy(&u, &a1, 4); ctx->r5 = (int32_t)u; } " + TAG + "\n"),    # s6829 hangar tilt: k from the handler's own dt pointer (s3 = a2)
    ("    // 0x800C6BD0: add.s       $f2, $f2, $f0\n", "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_kp(rdram, ctx->r19); " + TAG + "\n"),
    ("    // 0x800C6C34: add.s       $f2, $f2, $f0\n", "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f2.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_kp(rdram, ctx->r19); " + TAG + "\n"),
    ("    // 0x800C6CBC: sub.s       $f0, $f4, $f0\n", "    ctx->f0.fl = ctx->f4.fl - ctx->f0.fl;\n",
     "    ctx->f0.fl = ctx->f4.fl - ctx->f0.fl * rs64_fq_kp(rdram, ctx->r19); " + TAG + "\n"),
    ("    // 0x800C6CD4: add.s       $f0, $f4, $f0\n", "    ctx->f0.fl = ctx->f4.fl + ctx->f0.fl;\n",
     "    ctx->f0.fl = ctx->f4.fl + ctx->f0.fl * rs64_fq_kp(rdram, ctx->r19); " + TAG + "\n"),
    ("    // 0x800C6D0C: sub.s       $f0, $f2, $f0\n", "    ctx->f0.fl = ctx->f2.fl - ctx->f0.fl;\n",
     "    ctx->f0.fl = ctx->f2.fl - ctx->f0.fl * rs64_fq_kp(rdram, ctx->r19); " + TAG + "\n"),
    ("    // 0x800C6D24: add.s       $f0, $f2, $f0\n", "    ctx->f0.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f0.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_kp(rdram, ctx->r19); " + TAG + "\n"),
    # s6830 spline craft: speed ramp and scale growth per tick (k from the mission tick dt; f20 is reloaded on 2 paths)
    ("    // 0x800B0BB0: mul.s       $f0, $f0, $f2\n", "    ctx->f0.fl = MUL_S(ctx->f0.fl, ctx->f2.fl);\n",
     "    ctx->f0.fl = MUL_S(ctx->f0.fl, powf(ctx->f2.fl, rs64_fq_k())); " + TAG + "\n"),
    ("    // 0x800B0EF4: add.s       $f0, $f2, $f0\n", "    ctx->f0.fl = ctx->f2.fl + ctx->f0.fl;\n",
     "    ctx->f0.fl = ctx->f2.fl + ctx->f0.fl * rs64_fq_k(); " + TAG + "\n"),
    ("    // 0x800B0F14: sub.s       $f0, $f2, $f0\n", "    ctx->f0.fl = ctx->f2.fl - ctx->f0.fl;\n",
     "    ctx->f0.fl = ctx->f2.fl - ctx->f0.fl * rs64_fq_k(); " + TAG + "\n"),
]
done = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    here = [t for t in SITES if t[0] in s]
    if not here:
        continue
    for com, old, new in here:
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
        s = "".join(l for l in s.splitlines(True) if not ("static float rs64_fq_k" in l and l.endswith(TAG + "\n")))
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + HELPER, 1)
    p.write_text(s)
    done += len(here)
if done != len(SITES):
    sys.exit(f"s6826 fps60 float quanta: {done}/{len(SITES)} sites found")
print(f"[s6826] fps60 float quanta: {len(SITES)} per-tick increments scaled by dt*30 (pow for growth) under ROGUESQ_FPS60")
