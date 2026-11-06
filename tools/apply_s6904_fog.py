#!/usr/bin/env python3
"""s6904 G5e: setupCameraMatrices 0x80017098.. turns the level's fog distances into the ucode fog words:
s = max(*0x8011A878, D), e = max(*0x8011A87C, D), D = *0x8011A8CC, each x256 through z = A + B/d (A = *0x8011A7D4, B = *0x801163C0),
start/end = (z+1)/2, fm = 0.5/(end-start)*65536, fo = (0.5-start)/(end-start)*65536. ROGUESQ_G5E_FOGP=1 logs inputs and result.
Those distances never followed dd, while the s6418 far-cutoff scale moved the switch to the fog blender (detail chain, 0055 -> C811) out by dd.
So at dd>1 terrain past retail's ramp drew unfogged and then flipped to solid fog colour. rs64_s6904_fog scales the ramp, and
rs64_s6904_clipmul pulls the s6418 cutoff in to the ramp start, at most to (dd/2)^2, so the ramp has room to run on the fogged cells. See upstream_compat.cpp.
Runs after apply_s6903_cinegate in RS64_REPLAY.  Usage: apply_s6904_fog.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6904 fog"
f4 = D / "funcs_4.c"
u = f4.read_text(errors="surrogateescape")
A = "    // 0x8001726C: trunc.w.s   $f2, $f4\n"
if "rs64_s6904_clipmul" in (D / "funcs_9.c").read_text(errors="surrogateescape"): print("already applied"); sys.exit(0)
H = ('    { /* ' + TAG + ' */ extern void rs64_s6904_fog(uint8_t* rdram, recomp_context* ctx); rs64_s6904_fog(rdram, ctx); }\n')
if TAG not in u:
    assert u.count(A) == 1
    u = u.replace(A, H + A)
f9 = D / "funcs_9.c"; v = f9.read_text(errors="surrogateescape")
B = "v6475 = (e6475 && *e6475) ? (float)atof(e6475) : 1.0f; }"
assert v.count(B) == 1
v = v.replace(B, "v6475 = (e6475 && *e6475) ? (float)atof(e6475) : 0.0f; }")
C = "v6475; })"
assert v.count(C) == 1, v.count(C)
v = v.replace(C, "({ extern float rs64_s6904_clipmul(float); rs64_s6904_clipmul(v6475); }); }) /* " + TAG + " */")
f4.write_text(u, errors="surrogateescape"); f9.write_text(v, errors="surrogateescape"); print("applied", TAG)
