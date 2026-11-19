#!/usr/bin/env python3
"""s7623 G6c step 2: far-object stand-ins (docs/G6C-STANDINS-PLAN.md). Inserts rs64_standins_submit(rdram, ctx) right after the
`L_800FAC68:` label in runInMissionFrame (funcs_42.c), i.e. after the slotDispatcherIter(a1=4 render) broadcast and on its beq skip path,
exactly where upstream's before_vram=0x800FAC68 toml hook runs. The host function (src/main/rs64_standins.cpp) returns at once unless
ROGUESQ_STANDINS=1|tog and ROGUESQ_DRAW_DISTANCE > 1, so dd1 / unset is one cached test. Usage: apply_s7623_standins.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7623 standins"
f = D / "funcs_42.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "L_800FAC68:\n    // 0x800FAC68: jal         0x80055B8C\n"
assert t.count(A) == 1, t.count(A)
t = t.replace(A, "L_800FAC68:\n    { extern void rs64_standins_submit(uint8_t*, recomp_context*); rs64_standins_submit(rdram, ctx); } /* " + TAG + " */\n"
              "    // 0x800FAC68: jal         0x80055B8C\n", 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
