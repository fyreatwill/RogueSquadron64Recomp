"""s5887: under ROGUESQ_LOG_HUDBIT, npcProbeDriod's spawn arm (L_800CAC40: rs_malloc 0x11C, NPC+0x34 = descriptor r18)
tallies descriptor +0x70 class (0..3, else 'other') per spawn. Positive control: sum(classes)==total spawns, printed every spawn
(first 64 + every 16th). Class-1 spawns are logged individually with descriptor ptr. Idempotent; mirrored into the fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5887 spawn nonclass1 dump"
BLK = ('    { /* ' + TAG + ' */ static int s_e = -1; static unsigned s_n; '
       'if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
       'if (s_e) { uint32_t d = U32(ctx->r18); unsigned k = d ? (unsigned)MEM_W(ctx->r18, 0X70) : 99u; '
       'if (k != 1 && s_n < 4000) { s_n++; fprintf(stderr, "[spawnC] #%u cls=%u desc=0x%08X npc=0x%08X id=0x%X w=", s_n, k, d, U32(ctx->r17), (unsigned)MEM_W(ctx->r18, 0X78)); for (int q = 0; q < 0x90; q += 4) fprintf(stderr, "%08X ", (unsigned)MEM_W(ctx->r18, q)); fprintf(stderr, "\\n"); } } }\n')
_fe = lambda t, i: (lambda e: len(t) if e < 0 else e)(t.find("RECOMP_FUNC ", i + 12))   # s7422: whole-function idempotence
def apply(text, funcs=None):
    i = text.find("RECOMP_FUNC void npcProbeDriod(")
    if i < 0: return text, 0
    a = text.find("L_800CAC40:", i); assert a > 0
    anc = "    ctx->r17 = ADD32(ctx->r2, 0);\n"
    j = text.find(anc, a); assert 0 < j - a < 3000
    if TAG in text[i:_fe(text, i)]: return text, 0
    k = j + len(anc)
    return text[:k] + BLK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_36.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_36 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5887_spawn_nonclass1" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_36.c":\n'
               '        import apply_s5887_spawn_nonclass1 as _a5812\n'
               '        text, _n5812 = _a5812.apply(text)\n'
               '        if _n5812:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5887 spawn nonclass1 dump x{_n5812}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5811_ctr1_bt.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5887_spawn_nonclass1.py",\n', 1)
        fp.write_text(f); print("fixup patched")
