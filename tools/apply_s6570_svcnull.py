"""s6570: diagnostic (ROGUESQ_SVCNULL=1): log sendServiceMessage(queue,msg==0) with caller ra, and recvServiceMessage returning 0,
to name who posts the NULL message that hudDisplayUpdateWorker (0x80049644 lw v0,0x14(s0)) dereferences at dd6 px3 + MALLOC_SPILL.
Capped 60 lines. Idempotent. C++ side: src/main/upstream_compat.cpp (rs64_s6570_svcnull)."""
import pathlib
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c")
DECL = "extern void rs64_s6570_svcnull(char, uint32_t, uint32_t, uint32_t);\n"
R_OLD = "    ctx->r2 = MEM_W(ctx->r16, 0X1E8);\n    // 0x80006F68:"
R_NEW = "    ctx->r2 = MEM_W(ctx->r16, 0X1E8);\n    if (!U32(ctx->r2)) rs64_s6570_svcnull('R', U32(ctx->r16), 0u, U32(ctx->r16 ? MEM_W(ctx->r16, 0) : 0)); /* PATCH: s6570 svcnull */\n    // 0x80006F68:"
S_OLD = "    // 0x80006F78: addiu       $sp, $sp, -0x20\n"
S_NEW = "    if (!U32(ctx->r5)) rs64_s6570_svcnull('S', U32(ctx->r4), U32(ctx->r31), U32(ctx->r6)); /* PATCH: s6570 svcnull */\n" + S_OLD
def apply0(t):
    if "PATCH: s6570" in t or "void recvServiceMessage(" not in t: return t, 0
    assert t.count(R_OLD) == 1 and t.count(S_OLD) == 1
    t = t.replace(R_OLD, R_NEW, 1).replace(S_OLD, S_NEW, 1)
    i = t.index("RECOMP_FUNC void recvServiceMessage(")
    return t[:i] + DECL + t[i:], 1
if __name__ == "__main__":
    t = p.read_text(); t2, n = apply0(t)
    if n: p.write_text(t2)
    print("funcs_2.c live patched x%d" % n)
