"""s5831: tally every message reaching updateDestructionDebrisNpc by (descriptor class +0x70, msg id), under ROGUESQ_LOG_HITS=1.
Positive control: all classes/msgs are counted (any NPC message shows); msg 5 hit records for ALL classes log dmg (a2+6) for the first 12 per class.
 [hit] cls=<c> n=<k> dmg=<u> npc=<addr> vi=<vi>      [hitsum] cls=.. msg1..11 counts   (every 4096 events)
Read-only; no behaviour change. Mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5831 hit tally"
ANC = "    ctx->r17 = MEM_W(ctx->r21, 0X4);\n"
H = r'''/* PATCH: s5831 helpers */
extern volatile uint32_t rs64_vi_n_g;
static unsigned rs5831_c[4][12], rs5831_d[4], rs5831_tot, rs5831_en = 2;
static void rs5831_ev(uint8_t* rdram, recomp_context* ctx) {
    if (rs5831_en == 2) { const char* e = getenv("ROGUESQ_LOG_HITS"); rs5831_en = (e && e[0] == '1'); }
    if (!rs5831_en) return;
    unsigned m = (unsigned)(ctx->r5 & 0xFFFF); uint32_t npc = (uint32_t)ctx->r17;
    if ((npc >> 24) != 0x80 || m > 11) return;
    uint32_t d = (uint32_t)MEM_W(S32((int32_t)npc), 0X34);
    if (d < 0x80300000u || d >= 0x80330000u) return;
    unsigned c = (unsigned)MEM_W(S32((int32_t)d), 0X70); if (c > 3) c = 3;
    rs5831_c[c][m]++; rs5831_tot++;
    if (m == 5 && ((uint32_t)ctx->r6 >> 24) == 0x80 && rs5831_d[c]++ < 12) fprintf(stderr, "[hit] cls=%u n=%u dmg=%u npc=%08x vi=%u\n", c, rs5831_d[c], (unsigned)MEM_HU(ctx->r6, 0X6), npc, rs64_vi_n_g);
    if (rs5831_tot <= 2 || (rs5831_tot & 4095) == 0) for (unsigned i = 0; i < 4; i++) { fprintf(stderr, "[hitsum] cls=%u", i); for (unsigned j = 1; j < 12; j++) fprintf(stderr, " m%u=%u", j, rs5831_c[i][j]); fprintf(stderr, "\n"); }
}
'''
def apply(text, name=None):
    n = 0
    i = text.find("RECOMP_FUNC void updateDestructionDebrisNpc(")
    if i < 0 or T in text: return text, 0
    text = text[:i] + H + text[i:]
    i = text.find("RECOMP_FUNC void updateDestructionDebrisNpc(")
    j = text.find(ANC, i)
    if j < 0: return text, 1
    k = j + len(ANC)
    text = text[:k] + "    rs5831_ev(rdram, ctx); /* " + T + " */\n" + text[k:]
    return text, 2
if __name__ == "__main__":
    p = base / "funcs_16.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_16.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5831_hit_tally" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_16.c":\n'
               '        import apply_s5831_hit_tally as _a5831\n'
               '        text, _n5831 = _a5831.apply(text)\n'
               '        if _n5831:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5831 hit tally x{_n5831}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5806_npc_invuln.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5831_hit_tally.py",\n', 1)
        fp.write_text(s); print("fixup patched")
