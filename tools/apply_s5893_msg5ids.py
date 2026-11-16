"""s5893: under ROGUESQ_LOG_HUDBIT, npcProbeDriod entry tallies messages (type 1..6) per class-1 descriptor id (desc=*(npc+0x34),
cls=desc+0x70, id=desc+0x78). Every msg 5 logs [m5id] with id, slot +0x10/+0x14 and the id's running msg3/msg4/msg5 counts;
every 4096th msg prints the whole per-id table ([m5tab]). Control: msg3/msg4 per-id counts must be large for the same ids.
Question: are the 8-9 class-1 msg5 events 8-9 distinct ids (one-shot-per-kind) or repeats? Idempotent; mirrored into the fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5893 msg5 per-id"
BLK = ('    { /* ' + TAG + ' */ static int s_e = -1; static unsigned s_c[256][8], s_n, s_m5; '
       'if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
       'if (s_e) { uint32_t o = U32(ctx->r17), d = o >= 0x80000400u && o < 0x80800000u ? (uint32_t)MEM_W(ctx->r17, 0X34) : 0; '
       'if (d >= 0x80000400u && d < 0x80800000u && MEM_W((int64_t)(int32_t)d, 0X70) == 1) { '
       'unsigned id = (unsigned)MEM_W((int64_t)(int32_t)d, 0X78) & 255u, m = (uint32_t)ctx->r5 < 8 ? (uint32_t)ctx->r5 : 0; s_c[id][m]++; s_n++; '
       'if (m == 5) { s_m5++; fprintf(stderr, "[m5id] #%u id=0x%X desc=0x%08X s10=%08X s14=%08X cnt m2=%u m3=%u m4=%u m5=%u\\n", s_m5, id, d, (unsigned)MEM_W(ctx->r21, 0X10), (unsigned)MEM_W(ctx->r21, 0X14), s_c[id][2], s_c[id][3], s_c[id][4], s_c[id][5]); } '
       'if ((s_n & 0xFFFF) == 0) { fprintf(stderr, "[m5tab] n=%u m5=%u", s_n, s_m5); for (unsigned q = 0; q < 256; q++) if (s_c[q][2] + s_c[q][3] + s_c[q][4] + s_c[q][5]) fprintf(stderr, " %02X:%u/%u/%u/%u", q, s_c[q][2], s_c[q][3], s_c[q][4], s_c[q][5]); fprintf(stderr, "\\n"); } } } }\n')
_fe = lambda t, i: (lambda e: len(t) if e < 0 else e)(t.find("RECOMP_FUNC ", i + 12))   # s7422: whole-function idempotence
def apply(text, funcs=None):
    i = text.find("RECOMP_FUNC void npcProbeDriod(")
    if i < 0: return text, 0
    anc = "    ctx->r17 = MEM_W(ctx->r21, 0X4);\n"
    j = text.find(anc, i); assert 0 < j - i < 12000
    if TAG in text[i:_fe(text, i)]: return text, 0
    k = j + len(anc)
    # skip the s5813 msg line if present, keep ours after it
    nl = text.find("PATCH: s5813 msg", k)
    if 0 <= nl - k < 4: k = text.find("\n", nl) + 1
    return text[:k] + BLK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_36.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_36 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5893_msg5ids" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_36.c":\n'
               '        import apply_s5893_msg5ids as _a5893\n'
               '        text, _n5893 = _a5893.apply(text)\n'
               '        if _n5893:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5893 msg5 per-id x{_n5893}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5887_spawn_nonclass1.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5893_msg5ids.py",\n', 1)
        fp.write_text(f); print("fixup patched")
