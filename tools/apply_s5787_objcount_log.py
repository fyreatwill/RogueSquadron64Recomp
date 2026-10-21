"""s5787: with ROGUESQ_LOG_HUDBIT=1, setObjectiveCount / increaseObjectiveCount log (id, arg, old value, $ra) for
every call (budget 200 per function) plus a host backtrace for the first 6 calls on id 2, so the writer of mission-fail
counter 2 is named. Counter array base 0x80138060. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5787 objcount log"
def block(name):
    return ('    { static int s_e = -1, s_k = 0, s_b = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
            'if (s_e && s_k < 200) { s_k++; uint32_t id_ = (uint32_t)ctx->r4; uint32_t old_ = id_ ? (uint32_t)MEM_W((int32_t)((id_ - 1) * 4), S32((int32_t)0x80138060)) : 0; '
            'fprintf(stderr, "[objcount] ' + name + ' #%d id=%u arg=%d old=%u ra=0x%08X\\n", s_k, id_, (int)ctx->r5, old_, (unsigned)ctx->r31); '
            'if (id_ == 2 && s_b++ < 6) { extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); void* bt[24]; int nb = backtrace(bt, 24); backtrace_symbols_fd(bt, nb, 2); } } } /* ' + TAG + ' */\n')
FUNCS = ("setObjectiveCount", "increaseObjectiveCount")
def apply(text):
    n = 0
    for f in FUNCS:
        i = text.find("RECOMP_FUNC void %s(" % f)
        if i < 0: continue
        j = text.find("    int c1cs = 0;\n", i); assert 0 < j - i < 300
        k = j + len("    int c1cs = 0;\n")
        if TAG in text[k:k + 40 + len(block(f))]: continue
        text = text[:k] + block(f) + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_35.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_35 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5787_objcount_log" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_35.c":\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5787_objcount_log as _a5787\n'
               '        text, _n5787 = _a5787.apply(text)\n'
               '        if _n5787:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5787 objcount log x{_n5787}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5786_hudbit4_dump.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5787_objcount_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
