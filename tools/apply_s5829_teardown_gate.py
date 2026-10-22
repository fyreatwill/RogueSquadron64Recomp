"""s5829: under ROGUESQ_LOG_HUDBIT, log npcProbeDriod's teardown gate (L_800CB7F8: lw 0x6C(desc + diff*4); blez -> silent path).
Prints id, difficulty index, gate word, descriptor words 0x6C..0x78 and NPC word +0x8 per teardown, so counted (gate>0) vs silent
(gate<=0) teardowns can be split by id. Positive control: [tdgate] #n counts every teardown reaching the gate, pos= counts gate>0.
Idempotent; mirrored into the fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5829 teardown gate"
ANC = "    ctx->r2 = MEM_W(ctx->r3, 0X6C);\n"
LOG = ('    { /* ' + TAG + ' */ static int s_e = -1; static unsigned s_n, s_p; '
       'if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
       'if (s_e) { int32_t dsc = (int32_t)MEM_W(ctx->r17, 0X34); s_n++; if ((int)ctx->r2 > 0) s_p++; '
       'fprintf(stderr, "[tdgate] #%u id=0x%X diff=%u gate=%d pos=%u w6c..78=%08X %08X %08X %08X npc8=%08X\\n", s_n, '
       '(unsigned)MEM_W(dsc, 0X78), (unsigned)MEM_W((int32_t)0x80130000, 0X7CE4), (int)ctx->r2, s_p, '
       '(unsigned)MEM_W(dsc, 0X6C), (unsigned)MEM_W(dsc, 0X70), (unsigned)MEM_W(dsc, 0X74), (unsigned)MEM_W(dsc, 0X78), '
       '(unsigned)MEM_W(ctx->r17, 0X8)); } }\n')
def apply(text, funcs=None):
    i = text.find("RECOMP_FUNC void npcProbeDriod(")
    if i < 0: return text, 0
    j = text.find(ANC + "    // 0x800CB800: blez", i)
    if j < 0 or TAG in text[j:j + 3000]: return text, 0
    k = j + len(ANC)
    return text[:k] + LOG + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_36.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_36 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if "apply_s5829_teardown_gate" in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_36.c":\n'
               '        import apply_s5829_teardown_gate as _a5829\n'
               '        text, _n5829 = _a5829.apply(text)\n'
               '        if _n5829:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5829 teardown gate x{_n5829}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5812_npc_spawn_class.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5829_teardown_gate.py",\n', 1)
        fp.write_text(f); print("fixup patched")
