#!/usr/bin/env python3
"""s7495 class ET: log the game's fixed DL-chunk pool each time buildAndRegisterDefaultMaterial (0x80017B88) relinks it.
At the head store (0x80018094) $s2 = pool base and $s7 = pool bytes (chunks of 0x108, loop 0x80018044..0x8001805C).
Calls rs64_s7495_pool(base, size) (src/main/main.cpp), which logs `[s7495] pool` and checks every RDP depth image
(rs64_s7493_img kind 1) against the live pool: a depth image set inside [base, end) after the rebuild = live overlap
(H-et-zlive); depth images set BEFORE the rebuild that the new pool covers are logged as hist-overlap (same-run positive
control: retail's 640x480 Z at 0x76A000 lies inside the 640x340 pool [0x720000, 0x792780), s7495 oracle).
ROGUESQ_S7495_POOL=1 (+ROGUESQ_S7493_WBLIVE=1 for the depth sets). Measurement only. Usage: apply_s7495_poolwatch.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7495 poolwatch"
f = D / "funcs_4.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "    // 0x80018094: sw          $s2, 0x63B0($at)\n"
assert t.count(A) == 1, t.count(A)
t = t.replace(A, "    { extern void rs64_s7495_pool(uint32_t, uint32_t); rs64_s7495_pool(U32(ctx->r18), U32(ctx->r23)); } /* " + TAG + " */\n" + A, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
