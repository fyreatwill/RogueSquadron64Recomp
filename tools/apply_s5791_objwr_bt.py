"""s5791: in datItemSetObjectiveBooleanCount (under ROGUESQ_LOG_HUDBIT) log a3 and the stacked 2nd (counter,add) pair for every call
and a host backtrace for the first 10 calls with a2==2, naming the NPC-update caller whose DAT descriptor (+0x70..+0x84) adds to
objective counter 2. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5791 objwr bt"
ANCH = "/* PATCH: s5790 inline writer log */\n"
BLOCK = ('    { static int s_e = -1, s_b = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
         'if (s_e && (U32(ctx->r6) == 2 || MEM_W(ctx->r29, 0x10) == 2) && s_b < 10) { s_b++; '
         'fprintf(stderr, "[objwr2] a0=%u a1=%u a2=%u a3=%d st10=%u st14=%d c2=%u\\n", (unsigned)ctx->r4, (unsigned)ctx->r5, (unsigned)ctx->r6, (int)ctx->r7, '
         '(unsigned)MEM_W(ctx->r29, 0x10), (int)MEM_W(ctx->r29, 0x14), (unsigned)MEM_W(0, S32((int32_t)0x80138064))); '
         'extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); void* bt[24]; int nb = backtrace(bt, 24); backtrace_symbols_fd(bt, nb, 2); } } /* ' + TAG + ' */\n')
def apply(text, funcs=None):
    i = text.find("RECOMP_FUNC void datItemSetObjectiveBooleanCount(")
    if i < 0: return text, 0
    j = text.find(ANCH, i)
    if j < 0 or j - i > 3000: return text, 0
    k = j + len(ANCH)
    if TAG in text[k:text.find("RECOMP_FUNC ", k) if "RECOMP_FUNC " in text[k:] else len(text)]: return text, 0  # s7421: whole body, not a window
    return text[:k] + BLOCK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_15.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_15 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5791_objwr_bt" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_15.c":\n'
               '        import apply_s5791_objwr_bt as _a5791\n'
               '        text, _n5791 = _a5791.apply(text)\n'
               '        if _n5791:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5791 objwr bt x{_n5791}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5790_inline_writer_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5791_objwr_bt.py",\n', 1)
        fp.write_text(f); print("fixup patched")
