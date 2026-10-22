"""s5835: sphere-test probe. After transformObjectColliderCenter returns inside intersectSegmentWithObjectSphere (funcs_16.c, after_0 of 0x8006AE60),
read centre=v0 (xyz, r^2 at +0xC), seg origin=a2, seg dir=a3. Reports closest-approach^2 vs r^2 per shooter (P=player bolt, N=npc, via rs5834_who made global in funcs_13.c).
Prints first 20 P / 20 N rows (+ first 10 N rows with approach2<=r2 as positive control), per-4096 summary: min approach2, count approach2<=r2, count centre==0.
Under ROGUESQ_LOG_HITS=1. Read-only."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5835 sphere probe"
H = r'''/* PATCH: s5835 helpers */
extern unsigned rs5834_who;
static unsigned rs5835_sin[2], rs5835_sinp[2], rs5835_n[2], rs5835_in[2], rs5835_zc[2], rs5835_tot, rs5835_inprint; static float rs5835_min[2] = {1e30f, 1e30f}, rs5835_minr2[2], rs5835_minsd[2] = {1e30f, 1e30f}, rs5835_minsdr2[2]; static unsigned rs5835_mp[2]; static unsigned rs5837_tele, rs5837_en = 2, rs5837_cnt;
extern uint32_t rs5841_cand; static unsigned rs5841_cl[2][5];
static uint32_t rs5839_obj; static unsigned rs5839_cl[5], rs5839_tp, rs5839_tpc; 
static float rs5835_f(uint32_t w) { union { uint32_t u; float f; } x; x.u = w; return x.f; }
static void rs5835_probe(uint8_t* rdram, recomp_context* ctx) {
    unsigned w = 0; /* s5855: who-classifier void (s5854); all bolts counted as w=0 */
    uint32_t c = (uint32_t)ctx->r2, p = (uint32_t)ctx->r6, d = (uint32_t)ctx->r7;
    if ((c >> 24) != 0x80 || (p >> 24) != 0x80 || (d >> 24) != 0x80) return;
    float cc[4], pp[3], dd[3];
    for (int i = 0; i < 4; i++) cc[i] = rs5835_f((uint32_t)MEM_W(S32((int32_t)c), 4 * i));
    for (int i = 0; i < 3; i++) { pp[i] = rs5835_f((uint32_t)MEM_W(S32((int32_t)p), 4 * i)); dd[i] = rs5835_f((uint32_t)MEM_W(S32((int32_t)d), 4 * i)); }
    if (rs5837_en == 2) { const char* e = getenv("ROGUESQ_TELE_BOLT"); rs5837_en = (e && e[0] == '1'); }
    unsigned c1f = 0; unsigned k39 = 99; { /* s5841: class of the loop's candidate NPC via slot table *0x80130BB0 id*8 */
        uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0); uint32_t n = (uint32_t)MEM_W(S32((int32_t)(tb + (rs5841_cand & 0xFFFF) * 8)), 0);
        if ((n >> 24) == 0x80) { uint32_t d = (uint32_t)MEM_W(S32((int32_t)n), 0x34); if (d >= 0x80300000u && d < 0x80330000u) k39 = (unsigned)MEM_W(S32((int32_t)d), 0x70); }
        { static unsigned nd2[2]; if ((n >> 24) == 0x80 && nd2[w] < 24) { nd2[w]++; fprintf(stderr, "[ctx41] %s id=%x n=%08x:", w ? "N" : "P", (unsigned)(rs5841_cand & 0xFFFF), n); for (int q = 0; q < 0x80; q += 4) { uint32_t x = (uint32_t)MEM_W(S32((int32_t)n), q); if ((x >> 24) == 0x80 && x < 0x80800000u) fprintf(stderr, " +%x=%08x{70=%x}", q, x, (unsigned)MEM_W(S32((int32_t)x), 0x70)); else fprintf(stderr, " +%x=%x", q, x); } fprintf(stderr, "\n"); } }
        if ((n >> 24) == 0x80) { static uint32_t fk[2][24]; static unsigned fc[2][24], fn[2]; uint32_t f = (uint32_t)MEM_W(S32((int32_t)n), 0); unsigned z; c1f = (f == 0x800cabd4u || f == 0x800d93c0u || f == 0x800e7860u); for (z = 0; z < fn[w]; z++) if (fk[w][z] == f) break; if (z == fn[w] && z < 24) { fk[w][z] = f; fn[w]++; } if (z < 24) fc[w][z]++; if ((rs5835_tot & 4095) == 0) { fprintf(stderr, "[fn41] %s:", w ? "N" : "P"); for (z = 0; z < fn[w]; z++) fprintf(stderr, " %08x=%u", fk[w][z], fc[w][z]); fprintf(stderr, "\n"); } }
        if (k39 > 3) k39 = 4; rs5841_cl[w][k39]++; if ((rs5835_tot & 4095) == 0) fprintf(stderr, "[s5841] cand-class tally P=%u/%u/%u/%u/%u N=%u/%u/%u/%u/%u tele=%u\n", rs5841_cl[0][0], rs5841_cl[0][1], rs5841_cl[0][2], rs5841_cl[0][3], rs5841_cl[0][4], rs5841_cl[1][0], rs5841_cl[1][1], rs5841_cl[1][2], rs5841_cl[1][3], rs5841_cl[1][4], rs5839_tp); }
    { uint32_t o = rs5839_obj, dd0 = ((o >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)o), 0x34) : 0; if ((dd0 >> 24) == 0x80) k39 = (unsigned)MEM_W(S32((int32_t)dd0), 0x70); if (w == 0) rs5839_cl[k39 < 4 ? k39 : 4]++; if (w == 0 && rs5839_tpc++ < 12) fprintf(stderr, "[sph39] P obj=%08x desc=%08x cls=%u\n", o, dd0, k39); if ((rs5835_tot & 4095) == 0) fprintf(stderr, "[sph39] P class tally c0=%u c1=%u c2=%u c3=%u other=%u tele=%u\n", rs5839_cl[0], rs5839_cl[1], rs5839_cl[2], rs5839_cl[3], rs5839_cl[4], rs5839_tp); }
    { static unsigned nd[2]; if (((rs5839_obj >> 24) == 0x80) && nd[w] < 40) { nd[w]++; fprintf(stderr, "[own40] %s obj=%08x w=", w ? "N" : "P", rs5839_obj); for (int q = 0; q < 0x100; q += 4) fprintf(stderr, "%08X ", (unsigned)MEM_W(S32((int32_t)rs5839_obj), q)); fprintf(stderr, "\n"); } } /* s5840 owner dump */ /* s5841 c1f */
    if (rs5837_en && w == 0 && cc[3] > 0.0f && c1f && (rs5837_cnt++ & 3) == 0) { /* s5837: force bolt segment through shape centre */
        float nf[3] = {cc[0]-0.5f*dd[0], cc[1]-0.5f*dd[1], cc[2]-0.5f*dd[2]};
        for (int i = 0; i < 3; i++) { union { float f; uint32_t u; } x; x.f = nf[i]; MEM_W(S32((int32_t)p), 4 * i) = (int32_t)x.u; pp[i] = nf[i]; }
        rs5839_tp++; if (rs5837_tele++ < 10) fprintf(stderr, "[sph] TELE obj=%08x ctr=(%g,%g,%g) r2=%g dir=(%g,%g,%g)\n", rs5839_obj, cc[0], cc[1], cc[2], cc[3], dd[0], dd[1], dd[2]);
    }
    float v[3] = {cc[0]-pp[0], cc[1]-pp[1], cc[2]-pp[2]};
    float v2 = v[0]*v[0]+v[1]*v[1]+v[2]*v[2], dl = dd[0]*dd[0]+dd[1]*dd[1]+dd[2]*dd[2], t = v[0]*dd[0]+v[1]*dd[1]+v[2]*dd[2];
    float ap2 = (dl > 0.0f) ? v2 - t*t/dl : v2; unsigned in = (ap2 <= cc[3]);
    { float u = (dl > 0.0f) ? t/dl : 0.0f; if (u < 0.0f) u = 0.0f; if (u > 1.0f) u = 1.0f; float q0 = v[0]-u*dd[0], q1 = v[1]-u*dd[1], q2 = v[2]-u*dd[2]; float sd2 = q0*q0+q1*q1+q2*q2; unsigned sin_ = (sd2 <= cc[3]); if (sd2 < rs5835_minsd[w]) { rs5835_minsd[w] = sd2; rs5835_minsdr2[w] = cc[3]; if (rs5835_mp[w]++ < 12) fprintf(stderr, "[sph] MINSD %s sd2=%g r2=%g ratio=%g u=%g dl=%g |v|2=%g\n", w ? "N" : "P", sd2, cc[3], sd2/(cc[3] > 0.0f ? cc[3] : 1.0f), (dl > 0.0f) ? t/dl : 0.0f, dl, v2); } rs5835_sin[w] += sin_; if (sin_ && rs5835_sinp[w]++ < 10) fprintf(stderr, "[sph] SEGIN %s r2=%g |v|2=%g t=%g dl=%g sd2=%g\n", w ? "N" : "P", cc[3], v2, t, dl, sd2); }
    { /* s5855: per class-1/any id table: tests, min v2, min ap2, r2, segin */
        static struct { unsigned id, n, segin, c1; float mv2, map2, r2; } T[48]; static unsigned nT; unsigned id = rs5841_cand & 0xFFFF, z;
        for (z = 0; z < nT; z++) if (T[z].id == id) break;
        if (z == nT && z < 48) { T[z].id = id; T[z].mv2 = T[z].map2 = 1e30f; nT++; }
        if (z < 48) { T[z].n++; T[z].c1 = c1f; if (v2 < T[z].mv2) { T[z].mv2 = v2; T[z].r2 = cc[3]; } if (ap2 < T[z].map2) T[z].map2 = ap2; if (ap2 <= cc[3]) T[z].segin++; }
        static unsigned tk; if ((++tk & 1023) == 0) { fprintf(stderr, "[s5855] ids=%u:", nT); for (z = 0; z < nT; z++) fprintf(stderr, " %x{c1=%u n=%u mv2=%g map2=%g r2=%g in=%u}", T[z].id, T[z].c1, T[z].n, T[z].mv2, T[z].map2, T[z].r2, T[z].segin); fprintf(stderr, "\n"); }
    }
    if (w == 0) { /* s5853: new-minimum bolt-to-sphere separation, all NPCs (m0) and class-1 only (m1) */
        static float m0 = 1e30f, m1 = 1e30f; unsigned pr = 0; if (v2 < m0) { m0 = v2; pr |= 1; } if (c1f && v2 < m1) { m1 = v2; pr |= 2; }
        if (pr) fprintf(stderr, "[s5853] newmin%u c1=%u id=%x ctr=(%g,%g,%g) r2=%g bolt0=(%g,%g,%g) dir=(%g,%g,%g) v2=%g t=%g ap2=%g\n", pr, c1f, (unsigned)(rs5841_cand & 0xFFFF), cc[0], cc[1], cc[2], cc[3], pp[0], pp[1], pp[2], dd[0], dd[1], dd[2], v2, t, ap2);
    }
    rs5835_n[w]++; rs5835_tot++; if (in) rs5835_in[w]++; if (cc[0] == 0.0f && cc[1] == 0.0f && cc[2] == 0.0f) rs5835_zc[w]++;
    if (ap2 < rs5835_min[w]) { rs5835_min[w] = ap2; rs5835_minr2[w] = cc[3]; }
    if (rs5835_n[w] <= 20 || (w == 1 && in && rs5835_inprint++ < 10))
        fprintf(stderr, "[sph] %s ctr=(%g,%g,%g) r2=%g pt=(%g,%g,%g) dir=(%g,%g,%g) |v|2=%g t=%g ap2=%g in=%u\n", w ? "N" : "P", cc[0], cc[1], cc[2], cc[3], pp[0], pp[1], pp[2], dd[0], dd[1], dd[2], v2, t, ap2, in);
    if ((rs5835_tot & 4095) == 0) fprintf(stderr, "[sph] summary P n=%u in=%u segin=%u zeroctr=%u minap2=%g minsd2=%g(r2=%g) | N n=%u in=%u segin=%u zeroctr=%u minap2=%g minsd2=%g(r2=%g)\n", rs5835_n[0], rs5835_in[0], rs5835_sin[0], rs5835_zc[0], rs5835_min[0], rs5835_minsd[0], rs5835_minsdr2[0], rs5835_n[1], rs5835_in[1], rs5835_sin[1], rs5835_zc[1], rs5835_min[1], rs5835_minsd[1], rs5835_minsdr2[1]);
}
'''
FN = "RECOMP_FUNC void intersectSegmentWithObjectSphere("
CAP = "    transformObjectColliderCenter(rdram, ctx);\n        goto after_0;"
ANC = "    after_0:\n    // 0x8006AE68: mfc1        $t0, $f20\n"
def apply(text, name=None):
    n = 0
    if "static float rs5834_pt[3]" in text and "unsigned rs5834_who = 2;" not in text:
        a = "rs5834_sh[8]; static unsigned rs5834_who, "
        assert a in text
        text = text.replace(a, "rs5834_sh[8]; unsigned rs5834_who = 2; static unsigned ", 1)
        b = "rs5834_zero[1]);\n}\n"
        assert text.count(b) == 1
        text = text.replace(b, "rs5834_zero[1]);\n    rs5834_who = 2; /* PATCH: s5835 */\n}\n", 1); n += 1
    if "rs5841_cand = " not in text and "PATCH: s5833 proj loop" in text:
        a = "    rs5833_ev(rdram, (uint32_t)ctx->r17, 1, (uint32_t)(ctx->r16 & 0xFFFF), 1); /* PATCH: s5833 proj loop */\n"
        if a in text:
            text = text.replace(a, "    rs5841_cand = (uint32_t)(ctx->r16 & 0xFFFF); /* PATCH: s5841 */\n" + a, 1)
            f = "RECOMP_FUNC void audioCueDispatcherNpcHandler("
            i = text.find(f); text = text[:i] + "uint32_t rs5841_cand; /* PATCH: s5841 */\n" + text[i:]; n += 1
    if FN not in text: return text, n
    if "s5855: per class-1" not in text and "PATCH: s5835 helpers" in text:
        a = text.find("/* PATCH: s5835 helpers */"); b = text.find(FN)
        text = text[:a] + H + text[b:]; n += 1
    if "rs5839_obj = " not in text:
        i = text.find(FN); a = "    transformObjectColliderCenter(rdram, ctx);\n        goto after_0;"
        j = text.find(a, i)
        if j > 0: text = text[:j] + "    rs5839_obj = (uint32_t)ctx->r4; /* PATCH: s5839 */\n" + text[j:]; n += 1
    if n and T in text: return text, n
    if T in text: return text, n
    i = text.find(FN); j = text.find(ANC, i)
    if j < 0: return text, n
    text = text[:j] + "    after_0:\n    rs5835_probe(rdram, ctx); /* %s */\n    // 0x8006AE68: mfc1        $t0, $f20\n" % T + text[j+len(ANC):]
    i = text.find(FN)
    return text[:i] + H + text[i:], n + 1
if __name__ == "__main__":
    for f in ("funcs_13.c", "funcs_16.c"):
        p = base / f; t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        print(f, n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5835_sphere_probe" in s: print("fixup already")
    else:
        blk = ('    if p.name in ("funcs_13.c", "funcs_16.c"):\n'
               '        import apply_s5835_sphere_probe as _a5835\n'
               '        text, _n5835 = _a5835.apply(text)\n'
               '        if _n5835:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5835 sphere probe x{_n5835}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5834_seg_dump.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5835_sphere_probe.py",\n', 1)
        fp.write_text(s); print("fixup patched")
