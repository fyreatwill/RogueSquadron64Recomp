"""s5728: env-gated ROGUESQ_SUPPRESS_BOOL=<id>[,<id>...] makes setObjectiveBoolean (0x800C7540, funcs_35.c) a no-op
for those ids when val != 0 (clears still pass); always logs [objbool-sup] when armed. Discriminates whether the
dialogue flag bool 7 (sayWhoaHim_v0x1FC) is causal for the 0x64 fail arm. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5728 bool suppress"
BLOCK = ('    { static unsigned char s_m[256]; static int s_i = 0; if (!s_i) { s_i = 1; const char* e = getenv("ROGUESQ_SUPPRESS_BOOL"); '
         'while (e && *e) { char* q; long v = strtol(e, &q, 0); if (q == e) break; if (v > 0 && v < 256) s_m[v] = 1; e = (*q == \',\') ? q + 1 : q; if (*q != \',\') break; } } '
         'uint32_t id_ = U32(ctx->r4); if (id_ < 256 && s_m[id_] && U32(ctx->r5) != 0) { static int s_n = 0; if (++s_n <= 50) fprintf(stderr, "[objbool-sup] suppressed id=0x%X val=%u n=%d\\n", id_, U32(ctx->r5), s_n); ctx->r2 = 0; return; } } /* ' + TAG + ' */\n')
def apply(text):
    if TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void setObjectiveBoolean(uint8_t* rdram")
    assert i >= 0
    a = "    int c1cs = 0;\n"
    j = text.find(a, i); assert 0 < j - i < 200
    k = j + len(a)
    return text[:k] + BLOCK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_35.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_35 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "s5728 bool suppress" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_35.c" and "PATCH: s5728 bool suppress" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5728_boolsuppress as _a5728\n'
               '        text, _n5728 = _a5728.apply(text)\n'
               '        if _n5728:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5728 bool suppress x{_n5728}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5633_objdraw_force.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5728_boolsuppress.py",\n', 1)
        fp.write_text(f); print("fixup patched")
