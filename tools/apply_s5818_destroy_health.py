"""s5818: health of the object at destroyNpcSlotByIndex entry, bucketed per caller (the caller key comes from rs5817_cur, set by the s5817 entry hook).
Calls the generated getNpcCurrentHealth(slot) on a scratch ctx copy (pure read). Log under ROGUESQ_LOG_HUDBIT:
 [b3hp] caller=<fn> slot=.. upd=.. depth=.. fl=.. hp=<raw hex> hpf=<as float> vi=..   (first 6 per caller)
 [b3hpsum] per-caller counts: hp==0 / hp>0(int) / hp<0(int) / total   (every 256 events and on first 3)
Control: callers that legitimately kill (msg 5 chain) must show hp<=0; a non-NPC caller (effects) shows junk/0.
Requires s5817 helpers in the same file (rs5817_cur, rs5817_nm, rs5817_k)."""
H = r'''/* PATCH: s5818 helpers */
extern void getNpcCurrentHealth(uint8_t* rdram, recomp_context* ctx);
static struct { unsigned z, pos, neg, n; } rs5818_b[32]; static unsigned rs5818_tot;
static void rs5818_sum(void) { for (unsigned i = 0; i < 32 && i < rs5817_nra; i++) if (rs5818_b[i].n) fprintf(stderr, "[b3hpsum] caller=%s n=%u hp0=%u hppos=%u hpneg=%u\n", rs5817_nm[i], rs5818_b[i].n, rs5818_b[i].z, rs5818_b[i].pos, rs5818_b[i].neg); }
static void rs5818_log(uint8_t* rdram, recomp_context* ctx, uint32_t slot) {
    if (!rs5817_en() || slot < 0x80000000u || slot >= 0x80800000u) return;
    if (rs5818_tot >= 300) return; /* s5820: endMissionCleanup (~vi 23000+) hands this stale slots -> getNpcCurrentHealth faults (si_addr 0x37fffd040); sample in-mission only */
    recomp_context t = *ctx; t.r4 = (int32_t)slot; getNpcCurrentHealth(rdram, &t);
    uint32_t hp = (uint32_t)t.r2; float f; memcpy(&f, &hp, 4); int k = rs5817_k(rs5817_cur);
    rs5818_b[k].n++; if (hp == 0) rs5818_b[k].z++; else if ((int32_t)hp > 0) rs5818_b[k].pos++; else rs5818_b[k].neg++; rs5818_tot++;
    if (rs5818_b[k].n <= 6) fprintf(stderr, "[b3hp] caller=%s slot=%08X upd=%08X depth=%u fl=%04X hp=%08X hpf=%g cls=%08X vi=%u\n", rs5817_nm[k], slot, (uint32_t)MEM_W((int32_t)slot, 0), (unsigned)MEM_BU((int32_t)slot, 0X1A), (unsigned)MEM_HU((int32_t)slot, 0X14), hp, f, (uint32_t)MEM_W((int32_t)slot, 0X70), rs64_vi_n_g);
    if (rs5818_tot <= 3 || (rs5818_tot & 255) == 0) rs5818_sum(); }
'''
def apply8(text):
    n = 0
    if "RECOMP_FUNC void destroyNpcSlotByIndex(" not in text or "PATCH: s5817 helpers" not in text: return text, 0
    if "PATCH: s5818 helpers" not in text:
        i = text.find("RECOMP_FUNC void destroyNpcSlotByIndex("); text = text[:i] + H + text[i:]; n += 1
    A = "    // 0x8003EDA4: lbu         $v0, 0x1A($s0)\n"
    if "PATCH: s5818 hp" not in text:
        assert text.count(A) == 1
        text = text.replace(A, '    { /* PATCH: s5818 hp */ rs5818_log(rdram, ctx, U32(ctx->r16)); }\n' + A); n += 1
    return text, n

# ---- part 2: npcGroundTroopUpdate self-destroy label L_800E80B4 (4 entry gotos) ----
H39 = r'''/* PATCH: s5818 gt helpers */
extern volatile uint32_t rs64_vi_n_g;
extern void getNpcCurrentHealth(uint8_t* rdram, recomp_context* ctx);
static int rs5818_via; static unsigned rs5818_gn;
static void rs5818_gt(uint8_t* rdram, recomp_context* ctx) {
    static int e = -1; if (e < 0) { const char* v = getenv("ROGUESQ_LOG_HUDBIT"); e = (v && v[0]) ? 1 : 0; } if (!e) return;
    int32_t s1 = (int32_t)ctx->r17; int32_t d = MEM_W(s1, 0X34); uint32_t f60 = 0, f64 = 0, f68 = 0, bb = 0xFF, cnt = 0xFFFFFFFFu;
    if (d) { f60 = MEM_W(d, 0X60); f64 = MEM_W(d, 0X64); f68 = MEM_W(d, 0X68);
        if (f60) bb = MEM_BU((int32_t)0x8013889F + (int32_t)f60, 0); if (f64) cnt = (uint32_t)MEM_W((int32_t)0x8013805C + (int32_t)(f64 << 2), 0); }
    recomp_context t = *ctx; t.r4 = MEM_W(s1, 0X38); getNpcCurrentHealth(rdram, &t); rs5818_gn++;
    if (rs5818_gn <= 80) fprintf(stderr, "[gtdest] n=%u via=%d f60=%u bool=%u f64=%u cnt=%d f68=%d hp=%d vi=%u\n", rs5818_gn, rs5818_via, f60, bb, f64, (int32_t)cnt, (int32_t)f68, (int32_t)t.r2, rs64_vi_n_g); }
'''
def apply39(text):
    n = 0
    if "RECOMP_FUNC void npcGroundTroopUpdate(" not in text: return text, 0
    if "PATCH: s5818 gt helpers" not in text:
        i = text.find("RECOMP_FUNC void npcGroundTroopUpdate("); text = text[:i] + H39 + text[i:]; n += 1
    if "PATCH: s5818 gt label" not in text:
        i = text.find("RECOMP_FUNC void npcGroundTroopUpdate("); j = text.find("\nRECOMP_FUNC void", i + 10)
        body = text[i:j]
        assert body.count("goto L_800E80B4;") == 4
        k = [0]
        def rep(m):
            k[0] += 1; return "{ rs5818_via = %d; goto L_800E80B4; }" % k[0]
        import re
        body = re.sub(r"goto L_800E80B4;", rep, body)
        L = "L_800E80B4:\n"; assert body.count(L) == 1
        body = body.replace(L, L + "    { /* PATCH: s5818 gt label */ rs5818_gt(rdram, ctx); }\n")
        text = text[:i] + body + text[j:]; n += 1
    return text, n

# ---- part 3 (s5819): isPointXzWithinRangeOfRef inputs ----
H10 = r'''/* PATCH: s5819 range helpers */
extern volatile uint32_t rs64_vi_n_g;
extern void getCraftRecordByIdx(uint8_t* rdram, recomp_context* ctx);
static struct { uint32_t ra; unsigned in, out, shown[2]; } rs5819_b[8]; static unsigned rs5819_n;
static void rs5819_rng(uint8_t* rdram, recomp_context* ctx) {
    static int e = -1; if (e < 0) { const char* v = getenv("ROGUESQ_LOG_HUDBIT"); e = (v && v[0]) ? 1 : 0; } if (!e) return;
    uint32_t ra = (uint32_t)ctx->r31, ref = (uint32_t)ctx->r4, pt = (uint32_t)ctx->r5;
    if (ref < 0x80000000u || ref >= 0x80800000u || pt < 0x80000000u || pt >= 0x80800000u) return;
    float rx, rz, px, pz, sc, th; uint32_t w;
    w = MEM_W((int32_t)ref, 0); memcpy(&rx, &w, 4); w = MEM_W((int32_t)ref, 8); memcpy(&rz, &w, 4);
    w = MEM_W((int32_t)pt, 0); memcpy(&px, &w, 4); w = MEM_W((int32_t)pt, 8); memcpy(&pz, &w, 4);
    w = MEM_W((int32_t)0x8003A7D4, 0); memcpy(&sc, &w, 4); w = MEM_W((int32_t)0x8003A7D8, 0); memcpy(&th, &w, 4);
    float dx = (rx - px) * sc, dz = (rz - pz) * sc; float d2 = dx * dx + dz * dz; int res = !(th < d2);
    int k = -1; for (int i = 0; i < 8; i++) { if (rs5819_b[i].ra == ra) { k = i; break; } if (!rs5819_b[i].ra) { rs5819_b[i].ra = ra; k = i; break; } }
    if (k < 0) k = 7; if (res) rs5819_b[k].in++; else rs5819_b[k].out++; rs5819_n++;
    if (rs5819_b[k].shown[res] < 20) { rs5819_b[k].shown[res]++;
        recomp_context t = *ctx; t.r4 = 0; getCraftRecordByIdx(rdram, &t); uint32_t pl = (uint32_t)t.r2; float ux = 0, uz = 0;
        if (pl >= 0x80000000u && pl < 0x80800000u) { w = MEM_W((int32_t)pl, 0); memcpy(&ux, &w, 4); w = MEM_W((int32_t)pl, 8); memcpy(&uz, &w, 4); }
        fprintf(stderr, "[rng] ra=%08X res=%d ref=%08X refxz=(%g,%g) pt=%08X ptxz=(%g,%g) scale=%g thr=%g d2=%g player=%08X plxz=(%g,%g) b39=%u mode=%08X vi=%u\n",
            ra, res, ref, rx, rz, pt, px, pz, sc, th, d2, pl, ux, uz, (unsigned)MEM_BU((int32_t)0x80130B39, 0), (uint32_t)MEM_W((int32_t)0x8010CA1C, 0), rs64_vi_n_g); }
    if (rs5819_n <= 2 || (rs5819_n & 4095) == 0) for (int i = 0; i < 8; i++) if (rs5819_b[i].ra) fprintf(stderr, "[rngsum] ra=%08X in=%u out=%u\n", rs5819_b[i].ra, rs5819_b[i].in, rs5819_b[i].out); }
'''
def apply10(text):
    n = 0
    F = "RECOMP_FUNC void isPointXzWithinRangeOfRef("
    if F not in text: return text, 0
    if "PATCH: s5819 range helpers" not in text:
        i = text.find(F); text = text[:i] + H10 + text[i:]; n += 1
    if "s5819 range */ rs5819_rng" not in text:
        i = text.find(F); A = "    // 0x80047DAC: lwc1        $f2, 0x0($a0)\n"; j = text.find(A, i); assert j > 0
        text = text[:j] + "    { /* PATCH: s5819 range */ rs5819_rng(rdram, ctx); }\n" + text[j:]; n += 1
    return text, n
