"""s5861: does debris shadow troops in the projectile closest-hit loop (audioCueDispatcherNpcHandler, funcs_13.c)? Under ROGUESQ_LOG_HITS=1.
Per projectile: record every findSegmentObjectSphereHit hit (node fn, t=0x70($sp)); at the next projectile ENTER finalize:
winner = min t; kinds D=debris 0x8006cbb0, T=troop 0x800E7860, O=other. Tally bolts with any hit, winner kind, bolts where a T hit exists but winner is not T (shadowed),
and troop-vs-winner t gap. Positive control: sum(winner kinds)==bolts-with-hit; D-win count must be near the s5859 SEND victim split (455/468 debris). Read-only."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5861 shadow"
H = r'''/* PATCH: s5861 helpers */
static unsigned rs5861_en = 2, rs5861_nh, rs5861_bolts, rs5861_hitb, rs5861_win[3], rs5861_shadow, rs5861_thit, rs5861_tfirst_lt;
static struct { unsigned k; float t; } rs5861_h[64];
static float rs5861_sumgap; 
static unsigned rs5861_kind(uint8_t* rdram, uint32_t id) {
    uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0); uint32_t n = (uint32_t)MEM_W(S32((int32_t)(tb + (id & 0xFFFF) * 8)), 0);
    if ((n >> 24) != 0x80) return 2; uint32_t f = (uint32_t)MEM_W(S32((int32_t)n), 0);
    return f == 0x8006cbb0u ? 0 : ((f == 0x800E7860u || f == 0x800cabd4u || f == 0x800d93c0u) ? 1 : 2);
}
static void rs5861_fin(void) {
    if (!rs5861_nh) return;
    rs5861_hitb++; unsigned w = 0, tm = 99; float wt = 1e30f, tt = 1e30f;
    for (unsigned i = 0; i < rs5861_nh; i++) { if (rs5861_h[i].t < wt) { wt = rs5861_h[i].t; w = rs5861_h[i].k; } if (rs5861_h[i].k == 1 && rs5861_h[i].t < tt) { tt = rs5861_h[i].t; tm = 1; } }
    rs5861_win[w]++;
    if (tm == 1) { rs5861_thit++; if (w != 1) { rs5861_shadow++; rs5861_sumgap += tt - wt; } }
    rs5861_nh = 0;
}
static void rs5861_ev(uint8_t* rdram, uint32_t stage, uint32_t id, uint32_t sp) {
    if (rs5861_en == 2) { const char* e = getenv("ROGUESQ_LOG_HITS"); rs5861_en = (e && e[0] == '1'); }
    if (!rs5861_en) return;
    if (stage == 0) { rs5861_fin(); rs5861_bolts++;
        if ((rs5861_bolts & 127) == 1) fprintf(stderr, "[s5861] bolts=%u hitbolts=%u win D/T/O=%u/%u/%u troophit_bolts=%u shadowed=%u meangap=%g\n", rs5861_bolts, rs5861_hitb, rs5861_win[0], rs5861_win[1], rs5861_win[2], rs5861_thit, rs5861_shadow, rs5861_shadow ? rs5861_sumgap / rs5861_shadow : 0.0f); return; }
    union { uint32_t u; float f; } x; x.u = (uint32_t)MEM_W(S32((int32_t)sp), 0x70);
    if (rs5861_nh < 64) { rs5861_h[rs5861_nh].k = rs5861_kind(rdram, id); rs5861_h[rs5861_nh].t = x.f; rs5861_nh++; }
}
'''
FN = "RECOMP_FUNC void audioCueDispatcherNpcHandler("
A0 = "    // 0x8005D1F8: jal         0x8003FC28\n"
A3 = "    // 0x8005D24C: beq         $v0, $zero, L_8005D270\n"
def apply(text, name=None):
    if T in text: return text, 0
    i = text.find(FN)
    if i < 0: return text, 0
    j0 = text.find(A0, i); j3 = text.find(A3, i)
    if j0 < 0 or j3 < 0: return text, 0
    h3 = "    if (ctx->r2) rs5861_ev(rdram, 3, (uint32_t)(ctx->r16 & 0xFFFF), (uint32_t)ctx->r29); /* %s */\n" % T
    h0 = "    rs5861_ev(rdram, 0, 0, 0); /* %s */\n" % T
    text = text[:j3] + h3 + text[j3:]
    text = text[:j0] + h0 + text[j0:]
    i = text.find(FN)
    return text[:i] + H + text[i:], 3
if __name__ == "__main__":
    p = base / "funcs_13.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_13.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5861_shadow" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_13.c":\n'
               '        import apply_s5861_shadow as _a5861\n'
               '        text, _n5861 = _a5861.apply(text)\n'
               '        if _n5861:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5861 shadow x{_n5861}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5833_proj_loop.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5861_shadow.py",\n', 1)
        fp.write_text(s); print("fixup patched")
