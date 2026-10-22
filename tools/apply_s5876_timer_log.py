"""s5876: ROGUESQ_LOG_MTM=1 logs the per-object timer at funcs_30 0x800B1044 (object update, timer [obj+0x184] -= dt(f6)):
first 4 calls per object plus every 120th, with slot [obj+0xB8], [obj+0xBB], flags180, dt, timer. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5876 timer log"
ANC = "    ctx->f0.u32l = MEM_W(ctx->r17, 0X184);\n    // 0x800B1048:"
def apply(text):
    if TAG in text or ANC not in text: return text, 0
    log = ('    { static int s_e = -1, s_n = 0; static uint32_t s_o[16], s_c[16]; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_MTM"); s_e = (e && e[0]) ? 1 : 0; } '
           'if (s_e && s_n < 400) { uint32_t o = U32(ctx->r17); int k = 0; while (k < 15 && s_o[k] && s_o[k] != o) k++; if (!s_o[k]) s_o[k] = o; uint32_t c = s_c[k]++; '
           'if (c < 4 || c % 120 == 0) { s_n++; union { uint32_t u; float f; } dt, tm; dt.u = ctx->f6.u32l; tm.u = MEM_W(ctx->r17, 0X184); '
           'fprintf(stderr, "[tmr] o=0x%08X call=%u slot=%d bb=%u fl180=0x%04X dt=%g timer=%g\\n", o, c, (int)MEM_W(ctx->r17, 0XB8), (unsigned)MEM_BU(ctx->r17, 0XBB), (unsigned)MEM_HU(ctx->r17, 0X180), dt.f, tm.f); } } } /* ' + TAG + ' */\n')
    return text.replace(ANC, "    ctx->f0.u32l = MEM_W(ctx->r17, 0X184);\n" + log + "    // 0x800B1048:", 1), 1
if __name__ == "__main__":
    p = base / "funcs_30.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live patched", n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"; f = fp.read_text()
    if TAG in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_30.c" and "PATCH: s5876 timer log" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5876_timer_log as _a5757\n'
               '        text, _n5757 = _a5757.apply(text)\n'
               '        if _n5757:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5876 timer log")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5754_mask_stores.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5876_timer_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
