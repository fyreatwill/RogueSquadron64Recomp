"""s5633: env-gated ROGUESQ_FORCE_OBJ3=<0..2> override of the randMod(3) draw at 0x80102158 (funcs_43.c);
always logs [objdraw] natural/forced when ROGUESQ_LOG_HUDBIT=1. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5633 objdraw force"
BLOCK = ('    { static int s_f = -2, s_l = -1; if (s_f == -2) { const char* e = getenv("ROGUESQ_FORCE_OBJ3"); s_f = (e && e[0]) ? atoi(e) : -1; '
         'const char* l = getenv("ROGUESQ_LOG_HUDBIT"); s_l = (l && l[0]) ? 1 : 0; } int nat_ = (int)(int16_t)ctx->r2; '
         'if (s_f >= 0) ctx->r2 = (uint32_t)s_f; if (s_l) fprintf(stderr, "[objdraw] natural=%d used=%d forced=%d\\n", nat_, (int)(int16_t)ctx->r2, s_f >= 0); } /* ' + TAG + ' */\n')
def apply(text):
    if TAG in text: return text, 0
    i = text.find("// 0x80102158: jal         0x800C77D0")
    assert i >= 0
    a = "    after_37:\n"
    j = text.find(a, i); assert 0 < j - i < 400
    k = j + len(a)
    return text[:k] + BLOCK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_43.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_43 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "s5633 objdraw force" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_43.c" and "PATCH: s5633 objdraw force" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5633_objdraw_force as _a5633\n'
               '        text, _n5633 = _a5633.apply(text)\n'
               '        if _n5633:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5633 objdraw force x{_n5633}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5622_objbool_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5633_objdraw_force.py",\n', 1)
        fp.write_text(f); print("fixup patched")
