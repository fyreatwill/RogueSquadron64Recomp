"""s5811: under ROGUESQ_LOG_HUDBIT, datItemSetObjectiveBooleanCount prints a glibc-style backtrace (recomp C frames) for the first 8 calls with a2==1.
ra is 0 in the recomp (s5809 log), so the C stack is the only caller identity. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5811 ctr1 bt"
BLK = ('    { /* ' + TAG + ' */ extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); static int s_e2 = -1, s_b = 0; '
       'if (s_e2 < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e2 = (e && e[0]) ? 1 : 0; } '
       'if (s_e2 && U32(ctx->r6) == 1 && s_b < 8) { s_b++; void* bt[16]; int nb = backtrace(bt, 16); fprintf(stderr, "[ctr1-bt] #%d id=0x%X\\n", s_b, (unsigned)ctx->r4); backtrace_symbols_fd(bt, nb, 2); } }\n')
_fe = lambda t, i: (lambda e: len(t) if e < 0 else e)(t.find("RECOMP_FUNC ", i + 12))   # s7422: whole-function idempotence
def apply(text, funcs=None):
    i = text.find("RECOMP_FUNC void datItemSetObjectiveBooleanCount(")
    if i < 0: return text, 0
    j = text.find("    int c1cs = 0;\n", i); assert 0 < j - i < 2000
    k = j + len("    int c1cs = 0;\n")
    if TAG in text[i:_fe(text, i)]: return text, 0
    return text[:k] + BLK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_15.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_15 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5811_ctr1_bt" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_15.c":\n'
               '        import apply_s5811_ctr1_bt as _a5811\n'
               '        text, _n5811 = _a5811.apply(text)\n'
               '        if _n5811:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5811 ctr1 bt x{_n5811}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5809_ctr1_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5811_ctr1_bt.py",\n', 1)
        fp.write_text(f); print("fixup patched")
