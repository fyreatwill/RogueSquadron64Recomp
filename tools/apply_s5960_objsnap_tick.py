"""s5960: the s5953 [objsnap] diff only ran inside the three objective accessors, so lvl6 (writes that bypass them)
showed no movement. Run the same 15-slot diff (base 0x80138060) every call of tickMissionObjectives (per-frame
mission tick, funcs_42.c) under ROGUESQ_LOG_HUDBIT, logged as [objsnap-t] with its own snapshot and 400-line budget.
Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5960 objsnap tick"
BLOCK = ('    { static int s_e = -1, s_k = 0; static uint32_t s_p[16]; static int s_init = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
         'if (s_e && s_k < 400) { for (int q = 0; q < 15; q++) { uint32_t v_ = (uint32_t)MEM_W((int32_t)(q * 4), S32((int32_t)0x80138060)); '
         'if (!s_init) { s_p[q] = v_; } else if (v_ != s_p[q]) { s_k++; fprintf(stderr, "[objsnap-t] id=%d %u->%u\\n", q + 1, s_p[q], v_); s_p[q] = v_; } } s_init = 1; } } /* ' + TAG + ' */\n')
def apply(text):
    i = text.find("RECOMP_FUNC void tickMissionObjectives(")
    if i < 0: return text, 0
    j = text.find("    int c1cs = 0;\n", i); assert 0 < j - i < 300
    k = j + len("    int c1cs = 0;\n")
    if TAG in text[k:k + 40 + len(BLOCK) + 200]: return text, 0
    return text[:k] + BLOCK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_42.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_42 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5960_objsnap_tick" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_42.c":\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5960_objsnap_tick as _a5960\n'
               '        text, _n5960 = _a5960.apply(text)\n'
               '        if _n5960:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5960 objsnap tick x{_n5960}")\n\n')
        anc = '    if p.name == "funcs_35.c":\n        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n        import apply_s5953_objsnap'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5953_objsnap.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5960_objsnap_tick.py",\n', 1)
        fp.write_text(f); print("fixup patched")
