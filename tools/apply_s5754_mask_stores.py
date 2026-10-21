"""s5754: ROGUESQ_LOG_MTM=1 logs EVERY store to the pending-event mask word 0x8010C9E0 (MEM_W(-0X3620, rN) = rM) in all
funcs_*.c: [mtmst] pc=<store pc> val=<new mask> ra. The s5753 sampler sat after the dispatch and so saw only 0 (set-and-
consumed within a frame). Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib, re
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5754 mask store log"
PC = re.compile(r"^\s*// (0x[0-9A-F]{8}):")
ST = re.compile(r"^(\s*)MEM_W\(-0X3620, ctx->r(\d+)\) = ctx->r(\d+);\s*$")
def apply(text):
    if TAG in text: return text, 0
    out, pc, n = [], "0", 0
    for ln in text.split("\n"):
        m = PC.match(ln)
        if m: pc = m.group(1)
        out.append(ln)
        s = ST.match(ln)
        if s:
            out.append('%s{ static int s_e = -1, s_n = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_MTM"); s_e = (e && e[0]) ? 1 : 0; } '
                       'if (s_e && s_n < 300) { s_n++; fprintf(stderr, "[mtmst] pc=%s val=0x%%08X ra=0x%%X\\n", (unsigned)MEM_W(-0X3620, ctx->r%s), U32(ctx->r31)); } } /* %s */'
                       % (s.group(1), pc, s.group(2), TAG))
            n += 1
    return "\n".join(out), n
if __name__ == "__main__":
    tot = 0
    for p in sorted(base.glob("funcs_*.c")):
        t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2); tot += n
    print("live patched %d store sites" % tot)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if TAG in f: print("fixup already")
    else:
        blk = ('    if p.name.startswith("funcs_") and "PATCH: s5754 mask store log" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5754_mask_stores as _a5754\n'
               '        text, _n5754 = _a5754.apply(text)\n'
               '        if _n5754:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5754 mask store log x{_n5754}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5753_mtm_mask.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5754_mask_stores.py",\n', 1)
        fp.write_text(f); print("fixup patched")
