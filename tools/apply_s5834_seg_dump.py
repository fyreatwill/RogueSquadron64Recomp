"""s5834: segment-geometry dump around findSegmentObjectSphereHit call in audioCueDispatcherNpcHandler (funcs_13.c), under ROGUESQ_LOG_HITS=1.
Pre-call (0x8005D240): stash point=r19 (3 floats), dir=sp+0x88 (3 floats), shape words at *(r4)+0x48 (8 words as floats). Post-call (0x8005D24C): print line with hit flag.
Prints first 15 P calls, first 15 N calls, first 10 N hits, plus summary per 4096 calls: dir-length zero count, min point-to-shape dist. Positive control: N hits must be printed. Read-only."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5834 seg dump"
H = r'''/* PATCH: s5834 helpers */
static float rs5834_pt[3], rs5834_dir[3], rs5834_sh[8]; static unsigned rs5834_who, rs5834_n[2], rs5834_hit[2], rs5834_zero[2], rs5834_en = 2, rs5834_tot;
static float rs5834_f(uint32_t w) { union { uint32_t u; float f; } x; x.u = w; return x.f; }
static void rs5834_pre(uint8_t* rdram, recomp_context* ctx) {
    if (rs5834_en == 2) { const char* e = getenv("ROGUESQ_LOG_HITS"); rs5834_en = (e && e[0] == '1'); }
    if (!rs5834_en) return;
    uint32_t proj = (uint32_t)ctx->r17, sp = (uint32_t)ctx->r29, pt = (uint32_t)ctx->r19, sh = (uint32_t)MEM_W(S32((int32_t)ctx->r4), 0);
    rs5834_who = ((uint32_t)MEM_HU(S32((int32_t)proj), 0XF8) == (uint32_t)MEM_HU(S32((int32_t)0x80137DBAu), 0)) ? 0 : 1;
    { /* s5853: owner-id census (is the player-id compare ever true?) */
        static uint32_t ow[8]; static unsigned oc[8], on, tot, pm, hi; static uint32_t hio; uint32_t o = (uint32_t)MEM_HU(S32((int32_t)proj), 0XF8), pl = (uint32_t)MEM_HU(S32((int32_t)0x80137DBAu), 0); unsigned k;
        if (o == pl) pm++; if (o > hio) hio = o; for (k = 0; k < on; k++) if (ow[k] == o) break; if (k == on && on < 8) { ow[on++] = o; } if (k < 8) oc[k]++;
        if ((++tot & 16383) == 1) { fprintf(stderr, "[s5853] owner census plid=%x playermatch=%u maxowner=%x:", pl, pm, hio); for (k = 0; k < on; k++) fprintf(stderr, " %x*%u", ow[k], oc[k]); fprintf(stderr, " tot=%u\n", tot); }
    }
    for (int i = 0; i < 3; i++) { rs5834_pt[i] = rs5834_f((uint32_t)MEM_W(S32((int32_t)pt), 4 * i)); rs5834_dir[i] = rs5834_f((uint32_t)MEM_W(S32((int32_t)sp), 0x88 + 4 * i)); }
    for (int i = 0; i < 8; i++) rs5834_sh[i] = ((sh >> 24) == 0x80) ? rs5834_f((uint32_t)MEM_W(S32((int32_t)sh), 0x48 + 4 * i)) : 0.0f;
}
static void rs5834_post(uint8_t* rdram, uint32_t hit) {
    if (!rs5834_en) return;
    unsigned w = rs5834_who; float dl = rs5834_dir[0]*rs5834_dir[0] + rs5834_dir[1]*rs5834_dir[1] + rs5834_dir[2]*rs5834_dir[2];
    rs5834_n[w]++; if (hit) rs5834_hit[w]++; if (dl == 0.0f) rs5834_zero[w]++; rs5834_tot++;
    if ((w == 0 && rs5834_n[0] <= 15) || (w == 1 && (rs5834_n[1] <= 15 || (hit && rs5834_hit[1] <= 10)))) {
        fprintf(stderr, "[seg] %s hit=%u pt=(%g,%g,%g) dir=(%g,%g,%g) |dir|2=%g shape48=(%g,%g,%g,%g,%g,%g,%g,%g)\n", w ? "N" : "P", hit,
            rs5834_pt[0], rs5834_pt[1], rs5834_pt[2], rs5834_dir[0], rs5834_dir[1], rs5834_dir[2], dl,
            rs5834_sh[0], rs5834_sh[1], rs5834_sh[2], rs5834_sh[3], rs5834_sh[4], rs5834_sh[5], rs5834_sh[6], rs5834_sh[7]);
    }
    if ((rs5834_tot & 4095) == 0) fprintf(stderr, "[seg] summary P n=%u hit=%u zerodir=%u | N n=%u hit=%u zerodir=%u\n", rs5834_n[0], rs5834_hit[0], rs5834_zero[0], rs5834_n[1], rs5834_hit[1], rs5834_zero[1]);
}
'''
FN = "RECOMP_FUNC void audioCueDispatcherNpcHandler("
PRE = "    // 0x8005D240: addiu       $a2, $sp, 0x88\n"
POST = "    // 0x8005D24C: beq         $v0, $zero, L_8005D270\n"
SPH = r'''/* PATCH: s5854 spawn census helper */
static void rs5854_spawn(uint8_t* rdram, recomp_context* ctx) {
    static unsigned tot, eqpl, eqs2; static uint32_t key[16]; static unsigned cnt[16], nk;
    const char* e = getenv("ROGUESQ_LOG_HITS"); if (!(e && e[0] == '1')) return;
    uint32_t v = (uint32_t)ctx->r2 & 0xFFFF, s2 = (uint32_t)ctx->r18 & 0xFFFF, pl = (uint32_t)MEM_HU(S32((int32_t)0x80137DBAu), 0), ty = (uint32_t)MEM_BU(ctx->r16, 0X17), k;
    uint32_t kk = (ty << 16) | v; tot++; if (v == pl) eqpl++; if (s2 == pl) eqs2++;
    for (k = 0; k < nk; k++) if (key[k] == kk) break; if (k == nk && nk < 16) key[nk++] = kk; if (k < 16) cnt[k]++;
    if (tot <= 6 || (tot & 255) == 0 || v == pl || s2 == pl) { static unsigned pr; if (pr++ < 80) fprintf(stderr, "[s5854] spawn#%u rec=%08x rec+17(type)=%x rec+18=%x s2=%x a1=%x plid=%x ra=%08x\n", tot, (uint32_t)ctx->r16, ty, v, s2, (uint32_t)ctx->r5 & 0xFFFF, pl, (uint32_t)ctx->r31); }
    if ((tot & 255) == 1) { fprintf(stderr, "[s5854] census tot=%u v==plid:%u s2==plid:%u plid=%x ty.v*n:", tot, eqpl, eqs2, pl); for (k = 0; k < nk; k++) fprintf(stderr, " %x.%x*%u", key[k] >> 16, key[k] & 0xFFFF, cnt[k]); fprintf(stderr, "\n"); }
}
'''
SPA = "    // 0x8005CB10: sh          $v0, 0xF8($s1)\n"
def apply_spawn(text):
    if "PATCH: s5854 spawn census helper" in text: return text, 0
    i = text.find(FN); j = text.find(SPA, i)
    if i < 0 or j < 0: return text, 0
    text = text[:j] + "    rs5854_spawn(rdram, ctx); /* PATCH: s5854 spawn census */\n" + text[j:]
    i = text.find(FN); text = text[:i] + SPH + text[i:]
    return text, 2
def apply(text, name=None):
    text, n0 = apply_spawn(text)
    if T in text: return text, n0
    i = text.find(FN)
    if i < 0: return text, 0
    j = text.find(PRE, i); k = text.find(POST, i)
    if j < 0 or k < 0 or k < j: return text, 0
    text = text[:k] + "    rs5834_post(rdram, (uint32_t)ctx->r2); /* %s */\n" % T + text[k:]
    text = text[:j] + "    rs5834_pre(rdram, ctx); /* %s */\n" % T + text[j:]
    i = text.find(FN)
    text = text[:i] + H + text[i:]
    return text, 3 + n0
if __name__ == "__main__":
    p = base / "funcs_13.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_13.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5834_seg_dump" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_13.c":\n'
               '        import apply_s5834_seg_dump as _a5834\n'
               '        text, _n5834 = _a5834.apply(text)\n'
               '        if _n5834:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5834 seg dump x{_n5834}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5833_proj_loop.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5834_seg_dump.py",\n', 1)
        fp.write_text(s); print("fixup patched")
