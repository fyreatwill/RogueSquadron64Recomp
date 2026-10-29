"""s6063 G1c: ROGUESQ_HEAPLOG=1 -> live-bytes / high-water accounting for the guest rs_malloc heap.
Wraps rs_malloc (captures a0 request before the inner call) and rs_free (hook shared with s5041 census).
Logs every request >= 0x4000, and on a NULL result dumps live total, peak and the 8 largest live blocks. Unset = silent.
Idempotent; funcs_0.c only. C++ side lives in src/main/upstream_compat.cpp (rs64_s6063_*)."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "RECOMP_FUNC void rs_malloc(uint8_t* rdram, recomp_context* ctx) { rs_malloc_s5041_inner(rdram, ctx); rs64_s5041_malloc(U32(ctx->r2)); } /* PATCH: s5041 malloc wrap */\n"
NEW = "RECOMP_FUNC void rs_malloc(uint8_t* rdram, recomp_context* ctx) { uint32_t _rq = U32(ctx->r4), _ra = U32(ctx->r31); rs64_s6127_fl(U32(ctx->r5)); rs_malloc_s5041_inner(rdram, ctx); rs64_s5041_malloc(U32(ctx->r2)); rs64_s6063_malloc(_rq, U32(ctx->r2), _ra); } /* PATCH: s5041 malloc wrap */ /* PATCH: s6063 heaplog */\n"
FREE_OLD = "    rs64_s5041_free(U32(ctx->r4), U32(ctx->r31)); /* PATCH: s5041 free census */\n"
FREE_NEW = FREE_OLD + "    rs64_s6063_free(U32(ctx->r4)); /* PATCH: s6063 heaplog free */\n"
DECL = "extern void rs64_s6063_malloc(uint32_t, uint32_t, uint32_t);\nextern void rs64_s6063_free(uint32_t);\nextern void rs64_s6127_fl(uint32_t);\n"
def apply_heap0(text):
    if "PATCH: s6063 heaplog" in text or OLD not in text: return text, 0
    text = text.replace(OLD, NEW, 1)
    assert text.count(FREE_OLD) == 1
    text = text.replace(FREE_OLD, FREE_NEW, 1)
    a = "extern void rs64_s5041_malloc(uint32_t);\n"
    assert a in text
    text = text.replace(a, a + DECL, 1)
    return text, 1
def apply0(text):
    text, n = apply_heap0(text)
    marker = '/* PATCH: s6630 free ownership entry */'
    if marker not in text:
        anchor = 'RECOMP_FUNC void rs_free(uint8_t* rdram, recomp_context* ctx) {\n'
        assert text.count(anchor) == 1
        text = text.replace(anchor, anchor + '    extern void rs64_floor_ownership(const char*, uint32_t, uint32_t, uint32_t);\n    rs64_floor_ownership("free-entry", U32(ctx->r4), 0, U32(ctx->r31)); ' + marker + '\n', 1)
        n += 1
    return text, n

if __name__ == "__main__":
    p = base / "funcs_0.c"; t = p.read_text(); t2, n = apply0(t)
    if n: p.write_text(t2)
    print("funcs_0.c live patched x%d" % n)
