"""s5622: env-gated (ROGUESQ_LOG_HUDBIT=1) entry log for setObjectiveBoolean (0x800C7540): id=a0 value=a1 ra.
Logs ALL ids for the first 20 calls (positive control), then only ids 0x64/0x6D (cap 200). Idempotent on the LIVE tree;
mirrored into fixup_game_funcs_vendored.py and its replay list."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "[objbool]"
BLOCK = ('    { static int s_n = 0, s_m = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
         'if (s_e) { extern long time(long*); uint32_t id_ = U32(ctx->r4); s_n++; if (s_n <= 400) '
         'fprintf(stderr, "[objbool] call#%d id=0x%X val=%u t=%ld\\n", s_n, id_, U32(ctx->r5), (long)time(0)); } } /* PATCH: s5622 objbool log */\n')
def apply(text):
    if TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void setObjectiveBoolean(")
    assert i >= 0
    a = "    int c1cs = 0;\n"
    j = text.find(a, i); assert 0 < j - i < 300
    k = j + len(a)
    return text[:k] + BLOCK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_35.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_35 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "s5622 objbool log" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_35.c" and "PATCH: s5622 objbool log" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5622_objbool_log as _a5622\n'
               '        text, _n5622 = _a5622.apply(text)\n'
               '        if _n5622:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5622 objbool log x{_n5622}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5618_hudbit_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5622_objbool_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
