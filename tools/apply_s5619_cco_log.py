"""s5619: entry log for every lv*_checkComplexObjectives (static jal sites never set ctx->r31, so the s5618 hudbit
ra column is always 0; the interleaved [cco] lines identify the caller by order). Idempotent; mirrored in
fixup_game_funcs_vendored.py for regen."""
import pathlib, re
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
RX = re.compile(r"RECOMP_FUNC void (lv\w+_checkComplexObjectives)\(uint8_t\* rdram, recomp_context\* ctx\) \{\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n")
def apply(text):
    if "PATCH: s5619 cco log" in text: return text, 0
    n = [0]
    def sub(m):
        n[0] += 1
        return m.group(0) + ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
                             'if (s_e && s_n++ < 6) fprintf(stderr, "[cco] %s call#%%d\\n", s_n); } /* PATCH: s5619 cco log */\n' % m.group(1))
    return RX.sub(sub, text), n[0]
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
