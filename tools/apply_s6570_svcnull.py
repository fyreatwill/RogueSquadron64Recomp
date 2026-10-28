"""s6570: diagnostic (ROGUESQ_SVCNULL=1): log sendServiceMessage(queue,msg==0) with caller ra, and recvServiceMessage returning 0,
to name who posts the NULL message that hudDisplayUpdateWorker (0x80049644 lw v0,0x14(s0)) dereferences at dd6 px3 + MALLOC_SPILL.
Capped 60 lines. Idempotent. C++ side: src/main/upstream_compat.cpp (rs64_s6570_svcnull)."""
import pathlib
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c")
DECL = "extern void rs64_s6570_svcnull(char, uint32_t, uint32_t, uint32_t);\nextern void rs64_s6571_svc(char, uint32_t, uint32_t, uint32_t, uint32_t);\n"
R_OLD = "    ctx->r2 = MEM_W(ctx->r16, 0X1E8);\n    // 0x80006F68:"
R_NEW = "    ctx->r2 = MEM_W(ctx->r16, 0X1E8);\n    if (!U32(ctx->r2)) rs64_s6570_svcnull('R', U32(ctx->r16), 0u, U32(ctx->r16 ? MEM_W(ctx->r16, 0) : 0)); /* PATCH: s6570 svcnull */\n    // 0x80006F68:"
S_OLD = "    // 0x80006F78: addiu       $sp, $sp, -0x20\n"
S_NEW = "    if (!U32(ctx->r5)) rs64_s6570_svcnull('S', U32(ctx->r4), U32(ctx->r31), U32(ctx->r6)); /* PATCH: s6570 svcnull */\n" + S_OLD
# s6571: log osRecvMesg retval + queue state on every empty-slot recv; log signalServiceWorkerStop; log sends to key 0xC services
A_OLD = "    after_0:\n    // 0x80006F64: lw          $v0, 0x1E8($s0)\n"
A_NEW = "    after_0:\n    rs64_s6571_svc('r', U32(ctx->r16), U32(ctx->r2), U32(MEM_W(ctx->r16, 0X1E8)), U32(MEM_W(ctx->r16, 0X1D8))); rs64_s6571_svc('q', U32(ctx->r16), U32(MEM_W(ctx->r16, 0X1DC)) | (U32(MEM_W(ctx->r16, 0X1E0)) << 16), U32(MEM_W(ctx->r16, 0X1E4)), U32(MEM_W(ctx->r16, 0X1E4) ? MEM_W(MEM_W(ctx->r16, 0X1E4), 0) : 0)); /* PATCH: s6571 svc */\n    // 0x80006F64: lw          $v0, 0x1E8($s0)\n"
T_OLD = "    // 0x80007044: lbu         $v0, 0x4($a0)\n"
T_NEW = "    rs64_s6571_svc('T', U32(ctx->r4), U32(ctx->r31), U32(MEM_BU(ctx->r4, 0X4)), U32(MEM_W(ctx->r4, 0X8))); /* PATCH: s6571 svc */\n" + T_OLD
def apply1(t):
    if "PATCH: s6571" in t: return t, 0
    if t.count(A_OLD) != 1 or t.count(T_OLD) != 1: return t, 0
    t = t.replace(A_OLD, A_NEW, 1).replace(T_OLD, T_NEW, 1)
    i = t.index("RECOMP_FUNC void recvServiceMessage(")
    return t[:i] + "extern void rs64_s6571_svc(char, uint32_t, uint32_t, uint32_t, uint32_t);\n" + t[i:], 1
def apply0(t):
    if "PATCH: s6570" in t:
        return apply1(t)
    if "void recvServiceMessage(" not in t: return t, 0
    assert t.count(R_OLD) == 1 and t.count(S_OLD) == 1
    t = t.replace(R_OLD, R_NEW, 1).replace(S_OLD, S_NEW, 1)
    i = t.index("RECOMP_FUNC void recvServiceMessage(")
    t = t[:i] + DECL + t[i:]
    t, _ = apply1(t)
    return t, 1
if __name__ == "__main__":
    t = p.read_text(); t2, n = apply0(t)
    if n: p.write_text(t2)
    print("funcs_2.c live patched x%d" % n)
