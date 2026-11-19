#!/usr/bin/env python3
"""s7674 G6c held stand-in culls: inside addNpcToVisibilityBucket (0x80057C8C, funcs_12.c) record, while rs64_bk_on is set, the exit
PC (rs64_vt_pc, tools/apply_s7625_viewtest_reason.py) and v0 of the LAST transformVec3ToNpcLocalWithScale call this bucket call made,
and how many it made (0 = the bucket rejected before the view test). Reset at entry; read by rs64_bk_ret (real objects) and by the
stand-in submit (our own call) in src/main/rs64_standins.cpp. Off = predicted-false tests. Measurement only.
Idempotent; RS64_REPLAY after apply_s7672_bucket_handoff.py. Usage: apply_s7674_bucket_vt.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7674 bucket vt"
f = D / "funcs_12.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
head = "RECOMP_FUNC void addNpcToVisibilityBucket(uint8_t* rdram, recomp_context* ctx) {"
s = t.index(head); e = t.index("\nRECOMP_FUNC ", s + 1)
body = t[s:e]
anchor = "    const uint32_t rs64_bk_a2 = (uint32_t)ctx->r6; /* PATCH: s7672 bucket handoff */\n"
assert body.count(anchor) == 1, "s7672 patch must be applied first"
body = body.replace(anchor, anchor + "    if (__builtin_expect(rs64_bk_on, 0)) { rs64_bk_vt_n = 0; rs64_bk_vt_pc = 0; rs64_bk_vt_v0 = 0; } /* %s */\n" % TAG)
call = "    transformVec3ToNpcLocalWithScale(rdram, ctx);\n"
n = body.count(call)
assert n == 3, n
body = body.replace(call, call + "    if (__builtin_expect(rs64_bk_on, 0)) { ++rs64_bk_vt_n; rs64_bk_vt_pc = rs64_vt_pc; rs64_bk_vt_v0 = (uint32_t)ctx->r2; } /* %s */\n" % TAG)
decl = ("/* %s decls */\nextern int rs64_bk_on; extern uint32_t rs64_vt_pc, rs64_bk_vt_n, rs64_bk_vt_pc, rs64_bk_vt_v0;\n" % TAG)
t = t[:s] + decl + body + t[e:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG, "calls", n)
