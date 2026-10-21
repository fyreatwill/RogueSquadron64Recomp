"""s5757: ROGUESQ_LOG_MTM=1 logs the context of the ONLY writer of pending-event bit1 (pc 0x800B1140, funcs_30,
computeOrientedTransformFromQuat-labelled): at 0x800B10F4 logs terrain value f2 (sp+0x24, from 0x80067D90), s1+8, s1 ptr,
flags s1+0x180, byte s1+0xBB, gate word 0x8010CA20. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5757 bit1 ctx log"
ANC = "    ctx->f2.u32l = MEM_W(ctx->r29, 0X24);\n    // 0x800B10F8:"
def apply(text):
    if TAG in text or ANC not in text: return text, 0
    log = ('    { static int s_e = -1, s_n = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_MTM"); s_e = (e && e[0]) ? 1 : 0; } '
           'if (s_e && s_n < 200) { s_n++; union { uint32_t u; float f; } th, y; th.u = MEM_W(ctx->r29, 0X24); y.u = MEM_W(ctx->r17, 0X8); '
           'fprintf(stderr, "[bit1ctx] s1=0x%08X terrain=%g y=%g flags180=0x%04X b_BB=%u gate_CA20=%u\\n", U32(ctx->r17), th.f, y.f, '
           '(unsigned)MEM_HU(ctx->r17, 0X180), (unsigned)MEM_BU(ctx->r17, 0XBB), (unsigned)MEM_W(-0X35E0, S32(0X8011 << 16))); } } /* ' + TAG + ' */\n')
    return text.replace(ANC, "    ctx->f2.u32l = MEM_W(ctx->r29, 0X24);\n" + log + "    // 0x800B10F8:", 1), 1
if __name__ == "__main__":
    p = base / "funcs_30.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live patched", n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"; f = fp.read_text()
    if TAG in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_30.c" and "PATCH: s5757 bit1 ctx log" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5757_bit1_ctx as _a5757\n'
               '        text, _n5757 = _a5757.apply(text)\n'
               '        if _n5757:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5757 bit1 ctx log")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5754_mask_stores.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5757_bit1_ctx.py",\n', 1)
        fp.write_text(f); print("fixup patched")
