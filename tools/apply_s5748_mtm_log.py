"""s5748: ROGUESQ_LOG_MTM=1 logs every requestMissionTransitionMode (0x800FB190, funcs_42.c) entry:
arg a0, ra, gate word 0x8010CA20(-0x35E0), bool[7], bool[0x64], bool[0x65], bool[0x6D]. Names the real caller of the
observed mission fail (arg 2). Every call logs (that is the positive control). Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5748 mtm log"
BLOCK = ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_MTM"); s_e = (e && e[0]) ? 1 : 0; } if (s_e) { s_n++; if (s_n <= 200) '
         'fprintf(stderr, "[mtm] n=%d a0=%u ra=0x%X gate=%d b7=%u b64=%u b65=%u b6D=%u\\n", s_n, U32(ctx->r4), U32(ctx->r31), (int)MEM_W(-0X35E0, 0xFFFFFFFF80110000ull), '
         '(unsigned)MEM_BU(0x889F + 7, 0xFFFFFFFF80130000ull), (unsigned)MEM_BU(0x889F + 0x64, 0xFFFFFFFF80130000ull), (unsigned)MEM_BU(0x889F + 0x65, 0xFFFFFFFF80130000ull), (unsigned)MEM_BU(0x889F + 0x6D, 0xFFFFFFFF80130000ull)); } } /* ' + TAG + ' */\n')
def apply(text):
    if TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void requestMissionTransitionMode(uint8_t* rdram")
    assert i >= 0
    a = "    int c1cs = 0;\n"
    j = text.find(a, i); assert 0 < j - i < 200
    k = j + len(a)
    return text[:k] + BLOCK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_42.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_42 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if TAG in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_42.c" and "PATCH: s5748 mtm log" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5748_mtm_log as _a5748\n'
               '        text, _n5748 = _a5748.apply(text)\n'
               '        if _n5748:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5748 mtm log x{_n5748}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5728_boolsuppress.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5748_mtm_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
