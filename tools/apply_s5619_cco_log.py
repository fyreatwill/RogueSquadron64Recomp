"""s5619: entry log for every lv*_checkComplexObjectives (static jal sites never set ctx->r31, so the s5618 hudbit
ra column is always 0; the interleaved [cco] lines identify the caller by order). Idempotent; mirrored in
fixup_game_funcs_vendored.py for regen."""
import pathlib, re
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
RX = re.compile(r"RECOMP_FUNC void (lv\w+_checkComplexObjectives)\(uint8_t\* rdram, recomp_context\* ctx\) \{\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n")
SNAP = ('    { static unsigned char s_prev[0x81]; static int s_k = 0, s_en = -1; if (s_en < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_en = (e && e[0]) ? 1 : 0; } '
        'if (s_en && s_k < 300) { int ch = (s_k == 0); for (int i_ = 1; i_ <= 0x80; i_++) { unsigned char v_ = MEM_BU(0x8013889F + i_, 0); if (v_ != s_prev[i_]) { ch = 1; } } '
        'if (ch) { extern long time(long*); s_k++; fprintf(stderr, "[ccosnap] #%d t=%ld set:", s_k, (long)time(0)); '
        'for (int i_ = 1; i_ <= 0x80; i_++) { unsigned char v_ = MEM_BU(0x8013889F + i_, 0); s_prev[i_] = v_; if (v_) fprintf(stderr, " %X=%u", i_, v_); } fprintf(stderr, "\\n"); } } } /* PATCH: s5628 cco snap */\n')
def apply(text):
    if "PATCH: s5619 cco log" in text:
        if "PATCH: s5628 cco snap" in text: return text, 0
        n2 = [0]
        def sub2(m):
            n2[0] += 1
            return m.group(0) + SNAP
        return re.sub(r"[^\n]*PATCH: s5619 cco log \*/\n", sub2, text), n2[0]
    n = [0]
    def sub(m):
        n[0] += 1
        return m.group(0) + ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
                             'if (s_e && (s_n++ < 6 || s_n %% 60 == 0)) { extern long time(long*); fprintf(stderr, "[cco] %s call#%%d t=%%ld\\n", s_n, time(0)); } } /* PATCH: s5619 cco log */\n' % m.group(1))
    t2 = RX.sub(sub, text)
    t2 = re.sub(r"[^\n]*PATCH: s5619 cco log \*/\n", lambda m: m.group(0) + SNAP, t2)
    return t2, n[0]
if __name__ == "__main__":
    tot = 0
    for p in sorted(base.glob("funcs_*.c")):
        t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2); tot += n
    print("live patched x%d" % tot)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "s5619 cco log" in f: print("fixup already")
    else:
        blk = ('    if "PATCH: s5619 cco log" not in text and "_checkComplexObjectives(" in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5619_cco_log as _a5619\n'
               '        text, _n5619 = _a5619.apply(text)\n'
               '        if _n5619:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5619 cco log x{_n5619}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5618_hudbit_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5619_cco_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
