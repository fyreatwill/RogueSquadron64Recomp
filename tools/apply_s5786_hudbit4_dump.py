"""s5786: with ROGUESQ_LOG_HUDBIT=1, every setHudEnableBit4 entry additionally dumps the nonzero objective booleans
(array 0x801388A0 + id-1, ids 1..0x70), the objective timers 0..7 (floats at 0x8010C9F8) and, for the first 4 calls,
a host backtrace, so the script frame that fails the mission can be named. Anchored after the s5618 block. Idempotent;
mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5786 hudbit4 dump"
BLOCK = ('    { static int s_e = -1, s_k = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
         'if (s_e && s_k++ < 40) { char b_[512]; int o_ = 0; for (int i_ = 1; i_ <= 0x70; i_++) { unsigned v_ = (unsigned)MEM_BU(i_ - 1, S32((int32_t)0x801388A0)); if (v_ && o_ < 480) o_ += snprintf(b_ + o_, 512 - o_, "%X=%u ", i_, v_); } b_[o_] = 0; '
         'float t_[8]; for (int i_ = 0; i_ < 8; i_++) { uint32_t w_ = (uint32_t)MEM_W(i_ * 4, S32((int32_t)0x8010C9F8)); memcpy(&t_[i_], &w_, 4); } '
         'fprintf(stderr, "[hudbit4dump] #%d bools: %s| timers: %g %g %g %g %g %g %g %g\\n", s_k, b_, t_[0], t_[1], t_[2], t_[3], t_[4], t_[5], t_[6], t_[7]); '
         'if (s_k <= 4) { extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); void* bt[24]; int nb = backtrace(bt, 24); backtrace_symbols_fd(bt, nb, 2); } } } /* ' + TAG + ' */\n')
def apply(text):
    if TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void setHudEnableBit4(")
    assert i >= 0
    a = "/* PATCH: s5618 hudbit log */\n"
    j = text.find(a, i); assert 0 < j - i < 1500
    k = j + len(a)
    return text[:k] + BLOCK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_35.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_35 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if TAG in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_35.c" and "PATCH: s5786 hudbit4 dump" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5786_hudbit4_dump as _a5786\n'
               '        text, _n5786 = _a5786.apply(text)\n'
               '        if _n5786:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5786 hudbit4 dump x{_n5786}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5754_mask_stores.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5786_hudbit4_dump.py",\n', 1)
        fp.write_text(f); print("fixup patched")
