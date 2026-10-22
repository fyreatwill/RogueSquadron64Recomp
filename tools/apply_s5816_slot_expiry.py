"""s5816: slotDispatcherIter lifetime-countdown witness (under ROGUESQ_LOG_HUDBIT). At the pre-call point records, per flag-8 slot
(+0x14&8; byte +0x1A is decremented once per visit), first-seen VI / initial +0x1A / visit count; logs at expiry (+0x1A==1 before the decrement):
VI frames elapsed, visits, visits/VI. Control: global visits per VI (all slots, flag8 or not) logged every 128 VIs. Idempotent; mirrored into fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5816 slot expiry"
HELP = r'''/* PATCH: s5816 helpers */
extern volatile uint32_t rs64_vi_n_g;
static struct { uint32_t slot, vi0, age0, visits, fl, last, nchg; } rs5816_t[64]; static unsigned rs5816_nt, rs5816_ev;
static unsigned rs5816_tot, rs5816_all, rs5816_lastvi, rs5816_lastlog, rs5816_f8;
static int rs5816_en(void) { static int e = -1; if (e < 0) { const char* v = getenv("ROGUESQ_LOG_HUDBIT"); e = (v && v[0]) ? 1 : 0; } return e; }
static void rs5816_visit(uint32_t slot, uint32_t fl, uint32_t age, uint32_t w0) {
    uint32_t vi = rs64_vi_n_g; rs5816_tot++; rs5816_all++;
    if (fl & 8) rs5816_f8++;
    if (vi - rs5816_lastlog >= 128) { fprintf(stderr, "[slotvi] vi=%u dvi=%u visits=%u flag8visits=%u visits/vi=%.2f tracked=%u\n", vi, vi - rs5816_lastlog, rs5816_tot, rs5816_f8, (double)rs5816_tot / (vi - rs5816_lastlog), rs5816_nt);
        rs5816_tot = 0; rs5816_f8 = 0; rs5816_lastlog = vi; }
    if (!(fl & 8)) return;
    int k = -1; for (unsigned i = 0; i < rs5816_nt && i < 64; i++) if (rs5816_t[i].slot == slot) { k = i; break; }
    if (k < 0) { k = rs5816_nt++ & 63; rs5816_t[k].slot = slot; rs5816_t[k].vi0 = vi; rs5816_t[k].age0 = age; rs5816_t[k].visits = 0; rs5816_t[k].fl = fl; rs5816_t[k].last = age; rs5816_t[k].nchg = 0; }
    if (age != rs5816_t[k].last && rs5816_t[k].nchg++ < 8) { uint32_t d = vi - rs5816_t[k].vi0; fprintf(stderr, "[slotchg] slot=%08X upd=%08X fl=%04X age %u->%u vi0=%u vi=%u dvi=%u visits=%u\n", slot, w0, fl, rs5816_t[k].last, age, rs5816_t[k].vi0, vi, d, rs5816_t[k].visits); }
    rs5816_t[k].last = age;
    rs5816_t[k].visits++;
    if ((age & 0xFF) == 1 && rs5816_ev++ < 200) { uint32_t d = vi - rs5816_t[k].vi0; fprintf(stderr, "[slotexp] slot=%08X upd=%08X fl=%04X age0=%u vi0=%u vi=%u dvi=%u visits=%u visits/vi=%.2f\n", slot, w0, fl, rs5816_t[k].age0, rs5816_t[k].vi0, vi, d, rs5816_t[k].visits, d ? (double)rs5816_t[k].visits / d : -1.0); rs5816_t[k].slot = 0; }
}
'''
HOOK = ('    { /* ' + TAG + ' */ if (rs5816_en() && U32(ctx->r17) >= 0x80000000u && U32(ctx->r17) < 0x80800000u) '
        'rs5816_visit(U32(ctx->r17), (uint32_t)MEM_HU(ctx->r17, 0X14), (uint32_t)MEM_BU(ctx->r17, 0X1A), U32(MEM_W(ctx->r17, 0X0))); }\n')
ANC = "    // 0x8003E944: lbu         $v0, 0x1A($s1)\n"
HELP2 = r'''/* PATCH: s5816 post helpers */
static unsigned rs5816_ph[6], rs5816_pf8, rs5816_pn, rs5816_pz;
static void rs5816_post(uint32_t slot, uint32_t fl, uint32_t age) {
    uint32_t vi = rs64_vi_n_g; uint32_t b = age < 4 ? age : (age == 0xFF ? 5 : 4); rs5816_ph[b]++; rs5816_pn++; if (fl & 8) rs5816_pf8++;
    if (age == 1) { rs5816_pz++; if (rs5816_pz <= 64) fprintf(stderr, "[slotpost] slot=%08X upd=%08X fl=%04X age_post=1 (->0) flag8=%d vi=%u\\n", slot, U32(0), fl, (fl & 8) ? 1 : 0, vi); }
    if ((rs5816_pn & 0x3FFFF) == 0) fprintf(stderr, "[slotpost-hist] n=%u age0=%u age1=%u age2=%u age3=%u age4+=%u age255=%u flag8=%u hit1=%u\\n", rs5816_pn, rs5816_ph[0], rs5816_ph[1], rs5816_ph[2], rs5816_ph[3], rs5816_ph[4], rs5816_ph[5], rs5816_pf8, rs5816_pz);
}
'''
POST = ('    { /* PATCH: s5816 slot post */ if (rs5816_en() && U32(ctx->r17) >= 0x80000000u && U32(ctx->r17) < 0x80800000u) '
        'rs5816_post(U32(ctx->r17), (uint32_t)MEM_HU(ctx->r17, 0X14), (uint32_t)MEM_BU(ctx->r17, 0X1A)); }\n')
ANC2 = "L_8003E9D0:\n"
def apply(text):
    n = 0
    if "RECOMP_FUNC void slotDispatcherIter(" not in text: return text, 0
    if "PATCH: s5816 helpers" not in text:
        i = text.find("RECOMP_FUNC void slotDispatcherIter("); text = text[:i] + HELP + text[i:]; n += 1
    if TAG not in text:
        assert text.count(ANC) == 1
        text = text.replace(ANC, HOOK + ANC); n += 1
    if "PATCH: s5816 post helpers" not in text:
        i = text.find("RECOMP_FUNC void slotDispatcherIter("); text = text[:i] + HELP2 + text[i:]; n += 1
    if "PATCH: s5816 slot post" not in text:
        i = text.find("RECOMP_FUNC void slotDispatcherIter("); j = text.find(ANC2, i); assert 0 < j - i < 40000
        k = j + len(ANC2); text = text[:k] + POST + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_8.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live patched x%d" % n)
