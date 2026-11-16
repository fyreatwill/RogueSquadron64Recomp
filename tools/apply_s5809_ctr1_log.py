"""s5809: under ROGUESQ_LOG_HUDBIT, (a) datItemSetObjectiveBooleanCount logs every call whose a2==1 or sp+0x10==1 (bool id, val, a3, 2nd pair,
counters 1..3, byte 0x80130B39), budget 4000; (b) applyDatObjectiveTriggerEffect logs descriptor type and +0x28/+0x2C/+0x30 plus counters (budget 4000).
Separates H-supply / H-gate / H-port-skip for objective counter 1. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5809 ctr1 log"
CTR = ('(unsigned)MEM_W(0, S32((int32_t)0x80138060)), (unsigned)MEM_W(0, S32((int32_t)0x80138064)), (unsigned)MEM_W(0, S32((int32_t)0x80138068))')
PRE = '    { static int s_e = -1, s_k = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
BLOCKS = {
 "datItemSetObjectiveBooleanCount": PRE + 'if (s_e && (U32(ctx->r6) == 1 || MEM_W(ctx->r29, 0x10) == 1) && s_k < 4000) { s_k++; '
   'fprintf(stderr, "[ctr1] set #%d id=0x%X val=%u a2=%u a3=%d st10=%u st14=%d c=%u,%u,%u b39=%u ra=0x%08X\\n", s_k, (unsigned)ctx->r4, (unsigned)ctx->r5, (unsigned)ctx->r6, (int)ctx->r7, '
   '(unsigned)MEM_W(ctx->r29, 0x10), (int)MEM_W(ctx->r29, 0x14), ' + CTR + ', (unsigned)MEM_BU(0, S32((int32_t)0x80130B39)), (unsigned)ctx->r31); } } /* ' + TAG + ' */\n',
 "applyDatObjectiveTriggerEffect": PRE + 'if (s_e && s_k < 4000) { s_k++; '
   'fprintf(stderr, "[ctr1] trig #%d d=0x%08X type=0x%X +28=%u +2C=%u +30=%u +38=%u +48=%u c=%u,%u,%u ra=0x%08X\\n", s_k, (unsigned)ctx->r4, (unsigned)MEM_HU(ctx->r4, 0), '
   '(unsigned)MEM_W(ctx->r4, 0x28), (unsigned)MEM_W(ctx->r4, 0x2C), (unsigned)MEM_W(ctx->r4, 0x30), (unsigned)MEM_W(ctx->r4, 0x38), (unsigned)MEM_W(ctx->r4, 0x48), ' + CTR + ', (unsigned)ctx->r31); } } /* ' + TAG + ' */\n',
}
def apply(text, funcs=None):
    n = 0
    for f, blk in BLOCKS.items():
        i = text.find("RECOMP_FUNC void %s(" % f)
        if i < 0: continue
        j = text.find("    int c1cs = 0;\n", i); assert 0 < j - i < 300
        k = j + len("    int c1cs = 0;\n")
        if TAG in text[k:text.find("RECOMP_FUNC ", k) if "RECOMP_FUNC " in text[k:] else len(text)]: continue  # s7421: whole body, not a window
        text = text[:k] + blk + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_15.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_15 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5809_ctr1_log" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_15.c":\n'
               '        import apply_s5809_ctr1_log as _a5809\n'
               '        text, _n5809 = _a5809.apply(text)\n'
               '        if _n5809:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5809 ctr1 log x{_n5809}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5806_npc_invuln.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5809_ctr1_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
