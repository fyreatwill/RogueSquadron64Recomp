"""s6569 G1c phase 2: ROGUESQ_MALLOC_SPILL=1 -> when the 8 MB guest heap's rs_malloc returns NULL, serve the request from a bump
arena at 0x80800000..0x80C00000 (mapped behind rdram; needs ROGUESQ_RAMTOP_MB=16 so the RS64_RAM_TOP guards accept it). rs_free ignores
spill pointers. Unset = retail.
ORIGIN: s6568 heaplog: px3 load_level_hmp malloc(0x192CC) -> NULL with 5.4 MB live (heap0 full), pool fn then stores at NULL+2 (the
crash). The NULL is legitimate heap exhaustion, not corruption; the lever supplies more memory, it does not mask a wild value. Idempotent.
C++ side: src/main/upstream_compat.cpp (rs64_s6569_*)."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
M_OLD = "rs_malloc_s5041_inner(rdram, ctx); rs64_s5041_malloc(U32(ctx->r2));"
M_NEW = "rs_malloc_s5041_inner(rdram, ctx); if (!U32(ctx->r2)) { uint32_t _sp = rs64_s6569_spill(_rq); if (_sp) ctx->r2 = (int64_t)(int32_t)_sp; } /* PATCH: s6569 spill */ rs64_s5041_malloc(U32(ctx->r2));"
F_OLD = "    rs64_s5041_free(U32(ctx->r4), U32(ctx->r31)); /* PATCH: s5041 free census */\n"
F_NEW = "    if (rs64_s6569_isspill(U32(ctx->r4))) return; /* PATCH: s6569 spill free */\n" + F_OLD
DECL = "extern uint32_t rs64_s6569_spill(uint32_t);\nextern int rs64_s6569_isspill(uint32_t);\n"
def apply0(text):
    if "PATCH: s6569 spill" in text or M_OLD not in text: return text, 0
    assert text.count(F_OLD) == 1 and text.count(M_OLD) == 1
    text = text.replace(M_OLD, M_NEW, 1).replace(F_OLD, F_NEW, 1)
    a = "extern void rs64_s5041_malloc(uint32_t);\n"
    assert a in text
    return text.replace(a, a + DECL, 1), 1
if __name__ == "__main__":
    p = base / "funcs_0.c"; t = p.read_text(); t2, n = apply0(t)
    if n: p.write_text(t2)
    print("funcs_0.c live patched x%d" % n)
