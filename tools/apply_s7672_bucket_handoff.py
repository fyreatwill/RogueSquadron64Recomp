#!/usr/bin/env python3
"""s7672 G6c handoff: report every return of addNpcToVisibilityBucket (0x80057C8C, funcs_12.c) to the host as (state = a2 at entry,
v0) while rs64_bk_on is set (src/main/rs64_standins.cpp sets it only under ROGUESQ_STANDINS_LOG=1), so the host can line up the frame
a spawned object is first accepted into the view list against the last frame its stand-in was. Off = one predicted-false test at the
single return. Measurement only. Idempotent; RS64_REPLAY after apply_s7626_sg_probe.py. Usage: apply_s7672_bucket_handoff.py [dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7672 bucket handoff"
f = D / "funcs_12.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
head = "RECOMP_FUNC void addNpcToVisibilityBucket(uint8_t* rdram, recomp_context* ctx) {"
s = t.index(head); e = t.index("\nRECOMP_FUNC ", s + 1)
body = t[s:e]
first = "    uint64_t hi = 0, lo = 0, result = 0;\n"
assert body.count(first) == 1
body = body.replace(first, first + "    const uint32_t rs64_bk_a2 = (uint32_t)ctx->r6; /* %s */\n" % TAG)
ret = "    ctx->r29 = ADD32(ctx->r29, 0X38);\n    return;\n"
assert body.count(ret) == 1, body.count(ret)
body = body.replace(ret, ret.replace("    return;\n",
    "    if (__builtin_expect(rs64_bk_on, 0)) rs64_bk_ret(rdram, rs64_bk_a2, (uint32_t)ctx->r2); /* %s */\n    return;\n" % TAG))
decl = "/* %s decls */\nextern int rs64_bk_on; void rs64_bk_ret(uint8_t*, uint32_t, uint32_t);\n" % TAG
t = t[:s] + decl + body + t[e:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
