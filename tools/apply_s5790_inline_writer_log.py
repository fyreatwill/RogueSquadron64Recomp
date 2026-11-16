"""s5790: with ROGUESQ_LOG_HUDBIT=1, entry of the four static candidates for the inline writer of objective counter 2
(0x80138064) logs (func, a0..a2, ra, counters 1..3 at entry; budget 120 per func), so the get-change log (s5788) can be
ordered against them: the candidate logged just before each 1->2->3 step is the writer. Idempotent; mirrored into
fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5790 inline writer log"
FILES = {"funcs_15.c": ("datItemSetObjectiveBooleanCount", "applyDatObjectiveTriggerEffect"),
         "funcs_41.c": ("updateNpcEffectIntensity", "executeActorType1Effect")}
def block(name):
    return ('    { static int s_e = -1, s_k = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
            'if (s_e && s_k < 120) { s_k++; fprintf(stderr, "[objwr] ' + name + ' #%d a0=0x%08X a1=0x%08X a2=0x%08X ra=0x%08X c=%u,%u,%u\\n", s_k, '
            '(unsigned)ctx->r4, (unsigned)ctx->r5, (unsigned)ctx->r6, (unsigned)ctx->r31, '
            '(unsigned)MEM_W(0, S32((int32_t)0x80138060)), (unsigned)MEM_W(0, S32((int32_t)0x80138064)), (unsigned)MEM_W(0, S32((int32_t)0x80138068))); } } /* ' + TAG + ' */\n')
def apply(text, funcs):
    n = 0
    for f in funcs:
        i = text.find("RECOMP_FUNC void %s(" % f)
        if i < 0: continue
        j = text.find("    int c1cs = 0;\n", i); assert 0 < j - i < 300
        k = j + len("    int c1cs = 0;\n")
        if TAG in text[k:text.find("RECOMP_FUNC ", k) if "RECOMP_FUNC " in text[k:] else len(text)]: continue  # s7421: whole body, not a window
        text = text[:k] + block(f) + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    for fn, funcs in FILES.items():
        p = base / fn; t = p.read_text(); t2, n = apply(t, funcs)
        if n: p.write_text(t2)
        print("live %s patched x%d" % (fn, n))
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5790_inline_writer_log" in f: print("fixup already")
    else:
        blk = ('    if p.name in _a5790.FILES:\n'
               '        text, _n5790 = _a5790.apply(text, _a5790.FILES[p.name])\n'
               '        if _n5790:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5790 inline writer log x{_n5790}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        imp = ('    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '    import apply_s5790_inline_writer_log as _a5790\n')
        f = f.replace(anc, imp + blk + anc, 1)
        lst = '    "apply_s5787_objcount_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5790_inline_writer_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
