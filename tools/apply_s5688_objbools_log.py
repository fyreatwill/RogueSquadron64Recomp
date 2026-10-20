"""s5688: env-gated (ROGUESQ_LOG_HUDBIT=1) entry log for setObjectiveBooleans (0x800C7568, plural: writes val=a1 to every id in the
zero-terminated byte list at a0). Logs list ptr, val and the ids (positive control: any call logs; cap 300). This is the only other
writer of the objective-bool array besides setObjectiveBoolean (s5688 static read of funcs_35.c). Idempotent; mirrored in
fixup_game_funcs_vendored.py for regen."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5688 objbools log"
BLOCK = ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
         'if (s_e && s_n < 300) { extern long time(long*); s_n++; fprintf(stderr, "[objbools] call#%d list=0x%X val=%u t=%ld ids:", s_n, U32(ctx->r4), U32(ctx->r5), (long)time(0)); '
         'for (int i_ = 0; i_ < 32; i_++) { unsigned b_ = MEM_BU(ctx->r4, i_); if (!b_) break; fprintf(stderr, " %X", b_); } fprintf(stderr, "\\n"); } } /* ' + TAG + ' */\n')
def apply(text):
    if TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void setObjectiveBooleans(")
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
    if "s5688 objbools log" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_35.c" and "PATCH: s5688 objbools log" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5688_objbools_log as _a5688\n'
               '        text, _n5688 = _a5688.apply(text)\n'
               '        if _n5688:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5688 objbools log x{_n5688}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5622_objbool_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5688_objbools_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
