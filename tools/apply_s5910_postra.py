"""s5910: slotDispatcherIter ENTRY witness (ROGUESQ_LOG_HUDBIT). At function entry ctx->r31 is the true poster ra. Tallies (ra, msg&0xFFFF) for every
broadcast (table of 64 pairs) and prints '[postra]' on first sight of a pair and on every 512th call; msg==5 additionally logs the first 60 events with
selector (a0) and ra. Control: msg 3/4 and every other msg pair must appear in the same table. Idempotent; mirrored into fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5910 postra"
ANC = "    // 0x8003E8DC: addiu       $sp, $sp, -0x38\n"
HOOK = ('    { /* ' + TAG + ' */ static int s_e = -1; static uintptr_t s_ra[64]; static uint32_t s_m[64]; static unsigned s_c[64], s_k, s_all, s_5; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; }\n'
        '      if (s_e) { extern int backtrace(void**, int); extern char** backtrace_symbols(void* const*, int); void* bt[4] = {0}; backtrace(bt, 4); uintptr_t ra = (uintptr_t)bt[1]; uint32_t m = (uint32_t)ctx->r5 & 0xFFFFu; unsigned k; int nw = 0; s_all++;\n'
        '        for (k = 0; k < s_k; k++) if (s_ra[k] == ra && s_m[k] == m) break;\n'
        '        if (k == s_k && s_k < 64) { s_ra[k] = ra; s_m[k] = m; s_k++; nw = 1; }\n'
        '        if (k < 64) s_c[k]++;\n'
        '        if (nw) { char** sy = backtrace_symbols(bt + 1, 1); fprintf(stderr, "[postra-new] m%u caller=%s\\n", m, sy ? sy[0] : "?"); }\n'
        '        if (nw || (s_all & 8191) == 0) { fprintf(stderr, "[postra] all=%u |", s_all); for (unsigned i = 0; i < s_k; i++) fprintf(stderr, " #%u/m%u=%u", i, s_m[i], s_c[i]); fprintf(stderr, "\\n"); } } }\n')
def apply(text):
    if "RECOMP_FUNC void slotDispatcherIter(" not in text or TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void slotDispatcherIter(")
    j = text.find(ANC, i)
    assert 0 < j - i < 40000
    return text[:j] + HOOK + text[j:], 1
if __name__ == "__main__":
    p = base / "funcs_8.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5910_postra" in s: print("fixup already")
    else:
        anc = '    if p.name == "funcs_36.c":\n        import apply_s5829_teardown_gate'
        assert s.count(anc) == 1
        blk = ('    if p.name == "funcs_8.c":\n        import apply_s5910_postra as _a5910\n        text, _n5910 = _a5910.apply(text)\n'
               '        if _n5910:\n            changed = True\n            report.append(f"{p.name}: s5910 postra x{_n5910}")\n\n')
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5886_m5post.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5910_postra.py",\n', 1)
        fp.write_text(s); print("fixup patched")
