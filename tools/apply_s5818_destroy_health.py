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
