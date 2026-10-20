"""s5618: env-gated (ROGUESQ_LOG_HUDBIT=1) entry log for setHudEnableBit4 (0x800C7738) / setHudEnableBit8 (0x800C776C):
ra, gate 0x8010CA20, flagword 0x8010C9E0. Idempotent on the LIVE tree; mirrored into fixup_game_funcs_vendored.py
for regen and listed in its replay list."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
SITES = [("setHudEnableBit4", "0x800C7738", "4"), ("setHudEnableBit8", "0x800C776C", "8")]
def block(tag):
    return ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
            'if (s_e && s_n++ < 200) { fprintf(stderr, "[hudbit' + tag + '] call#%d ra=0x%08X gate=0x%08X flagword=0x%08X\\n", s_n, U32(ctx->r31), '
            'U32(MEM_W(-0X35E0, S32(0X8011 << 16))), U32(MEM_W(-0X3620, S32(0X8011 << 16)))); } } /* PATCH: s5618 hudbit log */\n')
def anchor(addr):
    return "    int c1cs = 0;\n    // %s: " % addr
def apply(text):
    n = 0
    for name, addr, tag in SITES:
        if ("[hudbit%s]" % tag) in text: continue
        a = anchor(addr)
        i = text.find("RECOMP_FUNC void %s(" % name)
        assert i >= 0
        j = text.find(a, i)
        assert 0 < j - i < 300, (name, j - i)
        k = j + len("    int c1cs = 0;\n")
        text = text[:k] + block(tag) + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_35.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_35 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "s5618 hudbit log" in f:
        print("fixup already")
    else:
        blk = ('    if p.name == "funcs_35.c" and "PATCH: s5618 hudbit log" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5618_hudbit_log as _a5618\n'
               '        text, _n5618 = _a5618.apply(text)\n'
               '        if _n5618:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5618 hudbit log x{_n5618}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5523_im_ra.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5618_hudbit_log.py",\n', 1)
        fp.write_text(f); print("fixup patched")
