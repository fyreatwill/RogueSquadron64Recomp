"""s6086 G1c phase 2: ROGUESQ_BIGARENA=1 diverts the scaled terrain stream-pool malloc (req == poolx_cap*184, armed by the
s6058 poolx hook) to a bump arena at 0x80800000+ (mapped behind rdram, below 0x81000000 so gfx reads stay legal), leaving the
8 MB guest heap to the other consumers. rs_free ignores >=0x80800000. Unset = retail. Idempotent; funcs_0.c + funcs_9.c.
C++ side: src/main/upstream_compat.cpp (rs64_s6086_*)."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
M_OLD = "RECOMP_FUNC void rs_malloc(uint8_t* rdram, recomp_context* ctx) { uint32_t _rq = U32(ctx->r4), _ra = U32(ctx->r31); "
M_NEW = M_OLD + "{ uint32_t _bp = rs64_s6086_divert(_rq); if (_bp) { ctx->r2 = (int64_t)(int32_t)_bp; return; } } /* PATCH: s6086 bigarena */ "
F_OLD = "    rs64_s5041_free(U32(ctx->r4), U32(ctx->r31)); /* PATCH: s5041 free census */\n"
F_NEW = "    if (U32(ctx->r4) >= 0x80800000u) return; /* PATCH: s6086 bigarena free */\n" + F_OLD
P_OLD = 'fprintf(stderr, "[poolx] cap %u -> %u\\n", o, n); }'
P_NEW = 'fprintf(stderr, "[poolx] cap %u -> %u\\n", o, n); { extern void rs64_s6086_arm(uint32_t, uint32_t); rs64_s6086_arm(o, n); } /* PATCH: s6086 arm */ }'
DECL = "extern uint32_t rs64_s6086_divert(uint32_t);\nextern void rs64_s6086_arm(uint32_t, uint32_t);\n"
def apply0(text):
    if "PATCH: s6086 bigarena" in text or M_OLD not in text: return text, 0
    assert text.count(F_OLD) == 1
    text = text.replace(M_OLD, M_NEW, 1).replace(F_OLD, F_NEW, 1)
    a = "extern void rs64_s5041_malloc(uint32_t);\n"
    assert a in text
    return text.replace(a, a + DECL, 1), 1
def apply9(text):
    if "PATCH: s6086 arm" in text or P_OLD not in text: return text, 0
    assert text.count(P_OLD) == 1
    text = text.replace(P_OLD, P_NEW, 1)
    return text, 1
if __name__ == "__main__":
    for nm, fn in (("funcs_0.c", apply0), ("funcs_9.c", apply9)):
        p = base / nm; t = p.read_text(); t2, n = fn(t)
        if n: p.write_text(t2)
        print(nm, "live patched x%d" % n)
