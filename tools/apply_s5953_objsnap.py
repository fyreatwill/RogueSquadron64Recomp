"""s5953: with ROGUESQ_LOG_HUDBIT=1, every get/set/increaseObjectiveCount call diffs ALL 15 objective-counter slots
(base 0x80138060) against the last snapshot and logs each changed slot as [objsnap] id=N old->new (budget 400), so
G1(d) sees counter movement whichever accessor touched it (s5787 only logged per-id gets, objcount_max was 0/empty
on lvl1/2/3/5). Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5953 objsnap"
BLOCK = ('    { static int s_e = -1, s_k = 0; static uint32_t s_p[16]; static int s_init = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
         'if (s_e && s_k < 400) { for (int q = 0; q < 15; q++) { uint32_t v_ = (uint32_t)MEM_W((int32_t)(q * 4), S32((int32_t)0x80138060)); '
         'if (!s_init) { s_p[q] = v_; } else if (v_ != s_p[q]) { s_k++; fprintf(stderr, "[objsnap] id=%d %u->%u ra=0x%08X\\n", q + 1, s_p[q], v_, (unsigned)ctx->r31); s_p[q] = v_; } } s_init = 1; } } /* ' + TAG + ' */\n')
FUNCS = ("setObjectiveCount", "increaseObjectiveCount", "getObjectiveCount")
_fe = lambda t, i: (lambda e: len(t) if e < 0 else e)(t.find("RECOMP_FUNC ", i + 12))   # s7422: whole-function idempotence
def apply(text):
    n = 0
    for f in FUNCS:
        i = text.find("RECOMP_FUNC void %s(" % f)
        if i < 0: continue
        j = text.find("    int c1cs = 0;\n", i); assert 0 < j - i < 300
        k = j + len("    int c1cs = 0;\n")
        if TAG in text[i:_fe(text, i)]: continue
        text = text[:k] + BLOCK + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_35.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_35 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5953_objsnap" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_35.c":\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5953_objsnap as _a5953\n'
               '        text, _n5953 = _a5953.apply(text)\n'
               '        if _n5953:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5953 objsnap x{_n5953}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5787_objcount_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5953_objsnap.py",\n', 1)
        fp.write_text(f); print("fixup patched")
