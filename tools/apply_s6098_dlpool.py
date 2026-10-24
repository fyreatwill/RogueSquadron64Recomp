"""s6098 G1c ph2: ROGUESQ_DLPOOLLOG=1 -> log the DL-chunk cache (*0x801163B0, 0x108-byte chunks, linked via +0)
length at every beginFrameDLChunk (0x8000A8A0) and reclaimDisplayListChunk (0x80007CDC) entry, so dd1 vs dd3 show
the pool's initial length, whether anything refills it, and its minimum before the finder-zero crash.
Walk is inline (MEM_W) because the C++ raw-rdram reader was wrong (s6095). Unset = silent, walk skipped.
Idempotent; funcs_3.c only. C++ side: rs64_s6098_* in src/main/upstream_compat.cpp."""
EXT = ("extern int rs64_s6098_en(void);\nextern void rs64_s6098(int, uint32_t, uint32_t, uint32_t);\n")
def _hook(kind):
    return ("    if (rs64_s6098_en()) { uint32_t _n = U32(ctx->r4), _l = 0; while (_n >= 0x80000000u && _n < 0x80800000u && _l < 200000u) { ++_l; _n = U32(MEM_W((gpr)(int32_t)_n, 0)); } "
            "rs64_s6098(%d, _l, _n, U32(ctx->r31)); } /* PATCH: s6098 dlpool */\n" % kind)
GROW = ("    if (rs64_s6099_en() && U32(ctx->r4) == 0u) { /* PATCH: s6099 dlpoolx -- grow the fixed 1356-chunk pool from a 0x80F00000 arena */\n"
        "        uint32_t _h = U32(MEM_W(0, (gpr)(int32_t)0x801163B0u)); uint32_t _c = rs64_s6099_alloc(U32(ctx->r31));\n"
        "        for (uint32_t _k = 0; _c && _h == 0u && _k < 128u; ++_k, _c += 0x108u) { MEM_W(0, (gpr)(int32_t)_c) = (int32_t)_h; MEM_W(4, (gpr)(int32_t)_c) = 0; if (_h) MEM_W(4, (gpr)(int32_t)_h) = (int32_t)_c; _h = _c; MEM_W(0, (gpr)(int32_t)0x801163B0u) = (int32_t)_h; }\n"
        "        ctx->r4 = (int32_t)U32(MEM_W(0, (gpr)(int32_t)0x801163B0u)); }\n")
EXT2 = "extern int rs64_s6099_en(void);\nextern uint32_t rs64_s6099_alloc(uint32_t);\n"
def apply3(text):
    text, n1 = _apply3(text)
    text, n2 = _apply3(text)
    return text, n1 + n2
def _apply3(text):
    n = 0
    if "PATCH: s6098 dlpool" in text and "PATCH: s6099 dlpoolx" not in text:
        i = text.find("RECOMP_FUNC void beginFrameDLChunk(")
        m = "/* PATCH: s6098 dlpool */\n"
        k = text.find(m, i)
        text = text[:k+len(m)] + GROW + text[k+len(m):]
        j = text.find("RECOMP_FUNC")
        return text[:j] + EXT2 + text[j:], 1
    if "PATCH: s6098 dlpool" in text: return text, 0
    for fn, kind in (("beginFrameDLChunk", 0), ("reclaimDisplayListChunk", 1)):
        sig = "RECOMP_FUNC void %s(uint8_t* rdram, recomp_context* ctx) {\n" % fn
        i = text.find(sig)
        if i < 0: continue
        a = "    ctx->r4 = MEM_W(ctx->r4, 0X63B0);\n"
        k = text.find(a, i)
        if k < 0 or k - i > 1500: continue
        text = text[:k+len(a)] + _hook(kind) + text[k+len(a):]
        n += 1
    if n:
        j = text.find("RECOMP_FUNC")
        text = text[:j] + EXT + text[j:]
    return text, n
if __name__ == "__main__":
    import pathlib
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c"); t = p.read_text(); t2, n = apply3(t)
    if n: p.write_text(t2)
    print("funcs_3.c live patched x%d" % n)
