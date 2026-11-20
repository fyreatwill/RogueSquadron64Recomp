#!/usr/bin/env python3
"""s7681 G6c: npcShieldUpdate (sub 0x32, funcs_19.c) never calls addNpcToVisibilityBucket. Its render case (0x8007B8CC) runs the same
view test through checkAndReturnByteFlagAsU8 0x8005940C(view, inst, state = s3+8, radius) and, when it passes, links itself into the
bucket list inline (0x8007B8E8..0x8007B92C). s7679 read that as "spawned, never drawn". This reports that view test to the host
detector (rs64_bk_shield -> rs64_bk_ret, src/main/rs64_standins.cpp) exactly like an addNpcToVisibilityBucket return, while
rs64_bk_on is set; ROGUESQ_S7681_SHIELD=0 restores the old blind detector. Measurement/handoff only: no guest state is written.
Idempotent; RS64_REPLAY after apply_s7674_bucket_vt.py. Usage: apply_s7681_shield_vt.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7681 shield vt"
f = D / "funcs_19.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
head = "RECOMP_FUNC void npcShieldUpdate(uint8_t* rdram, recomp_context* ctx) {"
s = t.index(head); e = t.index("\nRECOMP_FUNC ", s + 1)
body = t[s:e]
call = "    // 0x8007B8DC: addiu       $a2, $s3, 0x8\n    ctx->r6 = ADD32(ctx->r19, 0X8);\n    checkAndReturnByteFlagAsU8(rdram, ctx);\n"
assert body.count(call) == 1, body.count(call)
body = body.replace(call, call.replace("    checkAndReturnByteFlagAsU8(rdram, ctx);\n",
    "    if (__builtin_expect(rs64_bk_on, 0)) { rs64_bk_vt_n = 0; rs64_bk_vt_pc = 0; rs64_bk_vt_v0 = 0; } /* %s */\n"
    "    checkAndReturnByteFlagAsU8(rdram, ctx);\n"
    "    if (__builtin_expect(rs64_bk_on, 0)) rs64_bk_shield(rdram, (uint32_t)ADD32(ctx->r19, 0X8), (uint32_t)ctx->r2); /* %s */\n" % (TAG, TAG)))
decl = ("/* %s decls */\nextern int rs64_bk_on; extern uint32_t rs64_bk_vt_n, rs64_bk_vt_pc, rs64_bk_vt_v0;\n"
        "void rs64_bk_shield(uint8_t*, uint32_t, uint32_t);\n" % TAG)
t = t[:s] + decl + body + t[e:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
