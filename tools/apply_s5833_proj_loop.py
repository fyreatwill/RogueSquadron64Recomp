"""s5833: projectile hit-loop stage tally in audioCueDispatcherNpcHandler (funcs_13.c), under ROGUESQ_LOG_HITS=1.
Stages per (shooter==player0 ? P : N) x candidate class(+0x34->+0x70, 4=unknown):
 0 ENTER (before findActiveNpcInSlotChain, 0x8005D1F8; cls=4)  1 CAND (each chain NPC, 0x8005D238 before ctx test)
 2 SHAPE (ctx->+0xC nonzero)  3 HIT (findSegmentObjectSphereHit nonzero, 0x8005D24C)  4 SEND (hit-send 0x8005D35C, victim class)
Printed as [pl] lines first 2 events and every 2048 events. Player id = MEM_HU(0x80137DBA). Positive control: N row must be nonzero in every stage. Read-only."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5833 proj loop"
H = r'''/* PATCH: s5833 helpers */
static unsigned rs5833_c[2][5][5], rs5833_tot, rs5833_en = 2;
static void rs5833_ev(uint8_t* rdram, uint32_t proj, uint32_t stage, uint32_t cand, uint32_t extra) {
    if (rs5833_en == 2) { const char* e = getenv("ROGUESQ_LOG_HITS"); rs5833_en = (e && e[0] == '1'); }
    if (!rs5833_en) return;
    unsigned who = ((uint32_t)MEM_HU(S32((int32_t)proj), 0XF8) == (uint32_t)MEM_HU(S32((int32_t)0x80137DBAu), 0)) ? 0 : 1;
    unsigned c = 4;
    if (stage >= 1 && cand != 0xFFFF) {
        uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0); uint32_t n = (uint32_t)MEM_W(S32((int32_t)(tb + (cand & 0xFFFF) * 8)), 0);
        if ((n >> 24) == 0x80) { uint32_t d = (uint32_t)MEM_W(S32((int32_t)n), 0X34); if (d >= 0x80300000u && d < 0x80330000u) { c = (unsigned)MEM_W(S32((int32_t)d), 0X70); if (c > 3) c = 3; } }
    }
    if (stage == 2 && !extra) return;
    if (stage == 3 && !extra) return;
    rs5833_c[who][stage][c]++; rs5833_tot++;
    if (rs5833_tot <= 2 || (rs5833_tot & 2047) == 0 || (stage == 4 && who == 0)) {
        for (unsigned w = 0; w < 2; w++) { fprintf(stderr, "[pl] %s", w ? "N" : "P"); for (unsigned s = 0; s < 5; s++) { fprintf(stderr, " s%u=", s); for (unsigned k = 0; k < 5; k++) fprintf(stderr, "%u%s", rs5833_c[w][s][k], k < 4 ? "/" : ""); } fprintf(stderr, " pid=%04x\n", (unsigned)MEM_HU(S32((int32_t)0x80137DBAu), 0)); }
    }
}
'''
FN = "RECOMP_FUNC void audioCueDispatcherNpcHandler("
def hk(stage, cand, extra): return "    rs5833_ev(rdram, (uint32_t)ctx->r17, %d, %s, %s); /* %s */\n" % (stage, cand, extra, T)
HOOKS = [("    // 0x8005D1F8: jal         0x8003FC28\n", hk(0, "0xFFFF", "1")),
         ("    // 0x8005D238: beq         $a0, $zero, L_8005D270\n", hk(1, "(uint32_t)(ctx->r16 & 0xFFFF)", "1") + hk(2, "(uint32_t)(ctx->r16 & 0xFFFF)", "(uint32_t)ctx->r4")),
         ("    // 0x8005D24C: beq         $v0, $zero, L_8005D270\n", hk(3, "(uint32_t)(ctx->r16 & 0xFFFF)", "(uint32_t)ctx->r2")),
         ("    // 0x8005D35C: jal         0x8003E8DC\n", hk(4, "(uint32_t)(ctx->r4 & 0xFFFF)", "1"))]
def apply(text, name=None):
    if T in text: return text, 0
    i = text.find(FN)
    if i < 0: return text, 0
    n = 0
    for a, h in HOOKS:
        j = text.find(a, i)
        if j < 0: return text, 0
        text = text[:j] + h + text[j:]; n += 1
    i = text.find(FN)
    text = text[:i] + H + text[i:]
    return text, n + 1
if __name__ == "__main__":
    p = base / "funcs_13.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_13.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5833_proj_loop" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_13.c":\n'
               '        import apply_s5833_proj_loop as _a5833\n'
               '        text, _n5833 = _a5833.apply(text)\n'
               '        if _n5833:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5833 proj loop x{_n5833}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5832_disp_tally.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5833_proj_loop.py",\n', 1)
        fp.write_text(s); print("fixup patched")
