"""s5750: ROGUESQ_LOG_MTM=1 additionally dumps a host backtrace (execinfo) on the first 3 requestMissionTransitionMode
entries with a0==2, to name the real caller of the mission-end transition. Anchored after the s5748 block. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5750 mtm bt"
BLOCK = ('    { extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); static int s_b = 0; '
         'if (getenv("ROGUESQ_LOG_MTM") && U32(ctx->r4) == 2 && s_b < 3) { s_b++; void* bt[24]; int nb = backtrace(bt, 24); '
         'fprintf(stderr, "[mtm] a0==2 BACKTRACE #%d ra=0x%X\\n", s_b, U32(ctx->r31)); backtrace_symbols_fd(bt, nb, 2); } } /* ' + TAG + ' */\n')
def apply(text):
    if TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void requestMissionTransitionMode(uint8_t* rdram")
    assert i >= 0
    a = "/* PATCH: s5748 mtm log */\n"
    j = text.find(a, i); assert 0 < j - i < 2000
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
        blk = ('    if p.name == "funcs_42.c" and "PATCH: s5750 mtm bt" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5750_mtm_bt as _a5750\n'
               '        text, _n5750 = _a5750.apply(text)\n'
               '        if _n5750:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5750 mtm bt x{_n5750}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5748_mtm_log.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5750_mtm_bt.py",\n', 1)
        fp.write_text(f); print("fixup patched")
