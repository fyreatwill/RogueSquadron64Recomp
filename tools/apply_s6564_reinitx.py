"""s6564: ROGUESQ_DD_REINITX=<k> -- after buildAndRegisterDefaultMaterial (0x80017B88) relinks its fixed DL-chunk pool and stores the
head at 0x80018094, prepend round((k-1)*poolchunks) extra 0x108-byte chunks from rs64_s6099_alloc (bump arena ending 0x81000000, size
ROGUESQ_DLPOOLX_MB<=4) so the flight-scene pool scales with the draw-distance demand. Tests H-D2 (pool fixed at 2909 while px2 demand ~2x).
Logs [reinitx] with the chunk count before/after (positive control: len after = 2909 + extra). Only the flight-scene reinit (walked len >= 2000) is scaled: run 1 scaled the 1357-chunk boot reinit and crashed at begin 1 even at px1 (head >= 0x80800000 breaks boot). Unset = retail. Idempotent."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
ANCH = ("rs64_f5_store_shadow_post('W', 0x80018094u, U32(ADD32(ctx->r1, 0X63B0))); } /* PATCH: s6336 F5 post-store shadow */\nL_80018098:\n")
HOOK = r'''    { /* PATCH: s6564 reinitx */ static double _k = -1.0; if (_k < 0) { const char* _e = getenv("ROGUESQ_DD_REINITX"); _k = (_e && *_e) ? atof(_e) : 0.0; }
      if (_k > 1.0) { extern uint32_t rs64_s6099_alloc(uint32_t); uint32_t _h = U32(MEM_W(0X63B0, ctx->r1)), _n0 = 0, _w = _h; while (_w >= 0x80000000u && _w < 0x81000000u && _n0 < 200000u) { ++_n0; _w = U32(MEM_W(0, (gpr)(int32_t)_w)); }
        uint32_t _want = _n0 >= 2000u ? (uint32_t)((_k - 1.0) * _n0) : 0u, _add = 0;
        for (uint32_t _g = 0; _g < _want; _g += 128u) { uint32_t _c = rs64_s6099_alloc(U32(ctx->r31)); if (!_c) break; for (uint32_t _q = 0; _q < 128u; ++_q, _c += 0x108u) { MEM_W(0, (gpr)(int32_t)_c) = (int32_t)_h; MEM_W(4, (gpr)(int32_t)_c) = 0; if (_h) MEM_W(4, (gpr)(int32_t)_h) = (int32_t)_c; _h = _c; ++_add; } }
        MEM_W(0X63B0, ctx->r1) = (int32_t)_h;
        fprintf(stderr, "[reinitx] k=%.2f len %u -> %u (+%u) head=%08X\n", _k, _n0, _n0 + _add, _add, _h); } }
'''
if __name__ == "__main__":
    T = P.read_text()
    if "PATCH: s6564 reinitx" in T: print("already"); raise SystemExit
    assert T.count(ANCH) == 1, T.count(ANCH)
    i = T.index(ANCH) + len(ANCH) - len("L_80018098:\n")
    P.write_text(T[:i] + HOOK + T[i:]); print("ok")
