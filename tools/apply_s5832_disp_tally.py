"""s5832: tally every message passing slotDispatcherIter's indirect update call by (descriptor class +0x70 of obj a0->+0x34, msg id), under ROGUESQ_LOG_HITS=1.
Also keyed by update-fn address (top 6 fns by count printed). Positive control: all msgs/classes counted; compare cls0/2/3 magnitudes with s5831's updateDestructionDebrisNpc tally.
 [dsum] cls=.. m1..m11     [dfn] fn=.. cls=.. m5=.. total=..    (every 8192 events). Read-only."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5832 disp tally"
ANC = "    // 0x8003E974: jalr        $v0\n"
H = r'''/* PATCH: s5832 helpers */
static unsigned rs5832_c[5][12], rs5832_tot, rs5832_en = 2;
static struct { uint32_t fn; unsigned cls, m5, tot; } rs5832_f[48]; static unsigned rs5832_nf;
static void rs5832_ev(uint8_t* rdram, uint32_t obj, uint32_t msg, uint32_t fn) {
    if (rs5832_en == 2) { const char* e = getenv("ROGUESQ_LOG_HITS"); rs5832_en = (e && e[0] == '1'); }
    if (!rs5832_en) return;
    if (msg > 11) return;
    unsigned c = 4;
    if ((obj >> 24) == 0x80) { uint32_t d = (uint32_t)MEM_W(S32((int32_t)obj), 0X34); if (d >= 0x80300000u && d < 0x80330000u) { c = (unsigned)MEM_W(S32((int32_t)d), 0X70); if (c > 3) c = 3; } }
    rs5832_c[c][msg]++; rs5832_tot++;
    unsigned k = 0; for (; k < rs5832_nf; k++) if (rs5832_f[k].fn == fn && rs5832_f[k].cls == c) break;
    if (k == rs5832_nf && rs5832_nf < 48) { rs5832_f[k].fn = fn; rs5832_f[k].cls = c; rs5832_nf++; }
    if (k < 48) { rs5832_f[k].tot++; if (msg == 5) rs5832_f[k].m5++; }
    if (rs5832_tot <= 2 || (rs5832_tot & 8191) == 0) {
        for (unsigned i = 0; i < 5; i++) { fprintf(stderr, "[dsum] cls=%u", i); for (unsigned j = 1; j < 12; j++) fprintf(stderr, " m%u=%u", j, rs5832_c[i][j]); fprintf(stderr, "\n"); }
        for (unsigned i = 0; i < rs5832_nf; i++) if (rs5832_f[i].m5) fprintf(stderr, "[dfn] fn=%08x cls=%u m5=%u total=%u\n", rs5832_f[i].fn, rs5832_f[i].cls, rs5832_f[i].m5, rs5832_f[i].tot);
    }
}
'''
HOOK = "    rs5832_ev(rdram, (uint32_t)ctx->r4, (uint32_t)(ctx->r5 & 0xFFFF), (uint32_t)ctx->r2); /* " + T + " */\n"
def apply(text, name=None):
    i = text.find("RECOMP_FUNC void slotDispatcherIter(")
    if i < 0 or T in text or "PATCH: s5832 helpers" in text: return text, 0
    text = text[:i] + H + text[i:]
    i = text.find("RECOMP_FUNC void slotDispatcherIter(")
    j = text.find(ANC, i)
    if j < 0: return text, 1
    text = text[:j] + HOOK + text[j:]
    return text, 2
if __name__ == "__main__":
    p = base / "funcs_8.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_8.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5832_disp_tally" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_8.c":\n'
               '        import apply_s5832_disp_tally as _a5832\n'
               '        text, _n5832 = _a5832.apply(text)\n'
               '        if _n5832:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5832 disp tally x{_n5832}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5831_hit_tally.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5832_disp_tally.py",\n', 1)
        fp.write_text(s); print("fixup patched")
