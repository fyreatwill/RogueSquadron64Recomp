"""s6098 G1c ph2: ROGUESQ_DLPOOLLOG=1 -> log the DL-chunk cache (*0x801163B0, 0x108-byte chunks, linked via +0)
length at every beginFrameDLChunk (0x8000A8A0) and reclaimDisplayListChunk (0x80007CDC) entry, so dd1 vs dd3 show
the pool's initial length, whether anything refills it, and its minimum before the finder-zero crash.
Walk is inline (MEM_W) because the C++ raw-rdram reader was wrong (s6095). Unset = silent, walk skipped.
Idempotent; funcs_3.c only. C++ side: rs64_s6098_* in src/main/upstream_compat.cpp."""
EXT = ("extern int rs64_s6098_en(void);\nextern void rs64_s6098(int, uint32_t, uint32_t, uint32_t);\n")
def _hook(kind):
    return ("    if (rs64_s6098_en()) { uint32_t _n = U32(ctx->r4), _l = 0; while (_n >= 0x80000000u && _n < 0x80800000u && _l < 200000u) { ++_l; _n = U32(MEM_W((gpr)(int32_t)_n, 0)); } "
            "rs64_s6098(%d, _l, _n, U32(ctx->r31)); } /* PATCH: s6098 dlpool */\n" % kind)
GROW = ("    if (rs64_s6099_en() && ({ uint32_t _w = U32(ctx->r4), _q = 0; while (_w >= 0x80000000u && _w < 0x81000000u && _q < 256u) { ++_q; _w = U32(MEM_W((gpr)(int32_t)_w, 0)); } _q < 256u; })) { /* PATCH: s6099 dlpoolx -- grow the fixed 1356-chunk pool from a 0x80F00000 arena */\n"
        "        uint32_t _h = U32(MEM_W(0, (gpr)(int32_t)0x801163B0u)); uint32_t _c = rs64_s6099_alloc(U32(ctx->r31));\n"
        "        for (uint32_t _k = 0; _c && _k < 128u; ++_k, _c += 0x108u) { MEM_W(0, (gpr)(int32_t)_c) = (int32_t)_h; MEM_W(4, (gpr)(int32_t)_c) = 0; if (_h) MEM_W(4, (gpr)(int32_t)_h) = (int32_t)_c; _h = _c; MEM_W(0, (gpr)(int32_t)0x801163B0u) = (int32_t)_h; }\n"
        "        ctx->r4 = (int32_t)U32(MEM_W(0, (gpr)(int32_t)0x801163B0u)); }\n")
PRE = ("    { static int _pd; if (_pd < 2 && rs64_s6099_en()) { int _nc = rs64_s6286_pre(); if (_nc) { _pd = 2; if (_nc < 0) _nc = 0; uint32_t _h = U32(MEM_W(0, (gpr)(int32_t)0x801163B0u));\n"
       "      for (int _g = 0; _g < _nc; _g += 128) { uint32_t _c = rs64_s6099_alloc(U32(ctx->r31)); for (uint32_t _k = 0; _c && _k < 128u; ++_k, _c += 0x108u) { MEM_W(0, (gpr)(int32_t)_c) = (int32_t)_h; MEM_W(4, (gpr)(int32_t)_c) = 0; if (_h) MEM_W(4, (gpr)(int32_t)_h) = (int32_t)_c; _h = _c; } }\n"
       "      MEM_W(0, (gpr)(int32_t)0x801163B0u) = (int32_t)_h; ctx->r4 = (int32_t)_h; } } } /* PATCH: s6286 pregrow */\n")
EXT2 = "extern int rs64_s6285_en(void);\nextern int rs64_s6286_pre(void);\nextern void rs64_s6286_arm(void);\nextern int rs64_s6099_en(void);\nextern uint32_t rs64_s6099_alloc(uint32_t);\n"
ANCH4 = "    g_rs64_last_guest_pc = 0x8000B030u;\n    ctx->r4 = MEM_W(ctx->r4, 0X63B0);\n"
def _apply4(text):
    """s6285: begin pops the cache at 0x8000B030 with no empty test; a dd3 frame drains it mid-function (a0=0 -> sw 4(a0) SIGBUS at 0x8000B080)."""
    if "PATCH: s6285 b030" in text or text.count(ANCH4) != 1 or "PATCH: s6099 dlpoolx" not in text: return text, 0
    g = GROW.replace("s6099 dlpoolx", "s6285 b030").replace("rs64_s6099_en()", "rs64_s6285_en()")
    return text.replace(ANCH4, ANCH4 + g, 1), 1
import re as _re
_LD = _re.compile(r"(?P<lui>    ctx->r(?P<k>\d+) = S32\(0X8011 << 16\);\n(?:[^\n]*\n){0,3}?)(?P<ld>    ctx->r(?P=k) = MEM_W\(ctx->r(?P=k), 0X63B0\);\n)")
def _migrate6286(text):
    """s6286: already-patched files -> per-site grows use rs64_s6285_en(); add the one-shot pre-grow before the begin hook's dlpoolx GROW."""
    out, n = [], 0
    for ln in text.split("\n"):
        if ("PATCH: s6285 b030" in ln or "PATCH: s6285 topup" in ln) and "rs64_s6099_en()" in ln:
            ln = ln.replace("rs64_s6099_en()", "rs64_s6285_en()"); n += 1
        out.append(ln)
    text = "\n".join(out)
    if "PATCH: s6286 pregrow" not in text and text.count("PATCH: s6099 dlpoolx -- grow") == 1:
        i = text.find("PATCH: s6099 dlpoolx -- grow"); i = text.rfind("\n", 0, i) + 1
        text = text[:i] + PRE + text[i:]; n += 1
    if n and "extern int rs64_s6285_en(void);" not in text:
        j = text.find("RECOMP_FUNC"); text = text[:j] + EXT2 + text[j:]
    return text, n
def apply_topup(text):
    text, _m = _migrate6286(text)
    return _apply_topup(text)
def _apply_topup(text):
    """s6285: the pop-the-cache idiom (lui 0x8011; lw rK,0x63B0) is inlined at ~450 sites with no empty test; top the cache up (<256 chunks) after every such load."""
    def rep(m):
        k = m.group("k"); tail = text[m.end():m.end()+400]
        if "PATCH: s6285 topup" in tail or "PATCH: s6099 dlpoolx" in tail or "PATCH: s6285 b030" in tail: return m.group(0)
        g = GROW.replace("ctx->r4", "ctx->r" + k).replace("s6099 dlpoolx", "s6285 topup")
        g = g.replace("rs64_s6099_en()", "rs64_s6285_en()")
        return m.group(0) + g
    text2, n = _LD.subn(rep, text)
    n = text2.count("PATCH: s6285 topup") - text.count("PATCH: s6285 topup")
    if n and "extern int rs64_s6099_en(void);" not in text2:
        j = text2.find("RECOMP_FUNC"); text2 = text2[:j] + EXT2 + text2[j:]
    return text2, n

def apply3(text):
    text, _m = _migrate6286(text)
    text, n1 = _apply3(text)
    text, n2 = _apply3(text)
    text, n3 = _apply4(text)
    text, n4 = apply_topup(text)
    return text, n1 + n2 + n3 + n4
def _apply3(text):
    n = 0
    if "PATCH: s6098 dlpool" in text and "PATCH: s6099 dlpoolx" not in text:
        i = text.find("RECOMP_FUNC void beginFrameDLChunk(")
        m = "/* PATCH: s6098 dlpool */\n"
        k = text.find(m, i)
        text = text[:k+len(m)] + PRE + GROW + text[k+len(m):]
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
