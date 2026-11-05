#!/usr/bin/env python3
"""s6892 G5a: owner crash, Liberation of Gerrard V, about half way (2026-11-04, 3 crashes, dd2 FPS60 16:9).
cinematicSplineWalkerNpcHandler op 4 did a0 = *(s2+0x18) + 0x28 with *(s2+0x18) = 0x26282B2B and SIGBUSed
in initVec4TripletFromArgs. +0x18 is the mesh pointer op 1 stores at 0x8005BE2C and op 2 releases at 0x8005C340.
This records the good pointer at init and checks it at both op 4 reads and at release. A junk value is logged
(rs64_s6892.log) and repaired from the record; with no record the op 4 reads take the game's own null path.
Which check fires also separates "corrupted between frames" (0x8005C38C) from "corrupted inside this tick"
(0x8005C528). Mitigation and instrument, NOT the root cause: the writer is still unknown.
ROGUESQ_S6892=0 turns checks off. Runs last in RS64_REPLAY.  Usage: apply_s6892_walker_guard.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6892 walker guard"
HEAD = "RECOMP_FUNC void cinematicSplineWalkerNpcHandler(uint8_t* rdram, recomp_context* ctx) {"
DECL = ('/* %s */ extern void rs64_s6892_note(uint32_t, uint32_t); '
        'extern uint32_t rs64_s6892_check(uint8_t*, uint32_t, uint32_t, uint32_t);\n' % TAG)
NOTE_A = "{ MEM_W(0X18, ctx->r18) = ctx->r2; RS64_S5798_ST(0x8005BE2Cu, 0X18, ctx->r18, 4); }\n"
NOTE = NOTE_A + "    rs64_s6892_note(U32(ctx->r18), U32(ctx->r2)); /* %s */\n" % TAG
TICK_A = "    // 0x8005C38C: lw          $v0, 0x18($s2)\n    ctx->r2 = MEM_W(ctx->r18, 0X18);\n"
TICK = TICK_A + "    ctx->r2 = (gpr)(int32_t)rs64_s6892_check(rdram, U32(ctx->r18), U32(ctx->r2), 0x8005C38Cu); /* %s */\n" % TAG
LATE_A = "    // 0x8005C528: lw          $s1, 0x18($s2)\n    ctx->r17 = MEM_W(ctx->r18, 0X18);\n"
LATE = LATE_A + ("    ctx->r17 = (gpr)(int32_t)rs64_s6892_check(rdram, U32(ctx->r18), U32(ctx->r17), 0x8005C528u); /* %s */\n"
                 "    if (ctx->r17 == 0) goto L_8005C59C;\n" % TAG)
FREE_A = "    // 0x8005C340: lw          $a0, 0x18($s2)\n    ctx->r4 = MEM_W(ctx->r18, 0X18);\n"
FREE = FREE_A + "    ctx->r4 = (gpr)(int32_t)rs64_s6892_check(rdram, U32(ctx->r18), U32(ctx->r4), 0x8005C340u); /* %s */\n" % TAG

for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text(errors="surrogateescape")
    if HEAD not in t: continue
    if TAG in t: print("already applied", p.name); sys.exit(0)
    for a, b in ((NOTE_A, NOTE), (TICK_A, TICK), (LATE_A, LATE), (FREE_A, FREE)):
        assert t.count(a) >= 1, a  # delay-slot text is emitted twice; the first copy is the one that runs
        t = t.replace(a, b, 1)
    t = t.replace(HEAD, DECL + HEAD, 1)
    p.write_text(t, errors="surrogateescape"); print("applied", p.name); sys.exit(0)
sys.exit("handler not found")
