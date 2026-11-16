"""s5813: per-NPC fate of class-1 NPCs under ROGUESQ_LOG_HUDBIT. (1) npcProbeDriod spawn arm records class-1 NPC ptrs in a table
(2) npcProbeDriod entry tallies message type (a1 1..6) for messages whose target NPC (a0->+4) is a tracked class-1 NPC; control: every
entry counts total msgs and tracked-hit lookups. (3) unregisterAndFreeNpcSlot entry tallies calls by ra. Idempotent; mirrored into the fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T1 = "PATCH: s5813 track"; T2 = "PATCH: s5813 msg"; T3 = "PATCH: s5813 free"
TRK = ('    { /* ' + T1 + ' */ extern int rs5813_en(void); '
       'if (rs5813_en() && U32(ctx->r18) && MEM_W(ctx->r18, 0X70) == 1) rs5813_trk[rs5813_ntrk++ & 255] = U32(ctx->r17); }\n')
MSG = ('    { /* ' + T2 + ' */ if (rs5813_en()) rs5813_msg(U32(ctx->r17), (uint32_t)ctx->r5, MEM_W(0X80, ctx->r29)); if (rs5813_en() && ((uint32_t)ctx->r5 == 2 || (uint32_t)ctx->r5 == 5)) { extern void rs5813_stk(uint8_t*, int64_t, uint32_t); rs5813_stk(rdram, (int64_t)ctx->r29 + 0XB0, (uint32_t)ctx->r5); } }\n')
FREE = ('    { /* ' + T3 + ' */ extern void rs5813_free(uint32_t ra); rs5813_free(U32(ctx->r31)); }\n')
HELP = r'''/* PATCH: s5813 helpers */
#include <execinfo.h>
uint32_t rs5813_trk[256]; unsigned rs5813_ntrk;
static unsigned rs5813_m[7], rs5813_tm[7], rs5813_all, rs5813_hit, rs5813_nf; static uint32_t rs5813_fra[16]; static unsigned rs5813_frc[16];
int rs5813_en(void) { static int e = -1; if (e < 0) { const char* v = getenv("ROGUESQ_LOG_HUDBIT"); e = (v && v[0]) ? 1 : 0; } return e; }
void rs5813_stk(uint8_t* rdram, int64_t sp, uint32_t m) {
    static unsigned n[2]; unsigned q = m == 5; if (n[q]++ >= 6) return;
    fprintf(stderr, "[npcstk] msg=%u\n", m); { void* bt[12]; int nb = backtrace(bt, 12); backtrace_symbols_fd(bt, nb, 2); } return;
    fprintf(stderr, "[npcstk] msg=%u", m);
    for (uint32_t o = 0; o < 0x200; o += 4) { uint32_t w = U32(MEM_W(o, sp)); if (w >= 0x80000400u && w < 0x80200000u && !(w & 3)) fprintf(stderr, " +%X:%08X", o, w); }
    fprintf(stderr, "\n");
}
static uint32_t rs5813_mra[2][16]; static unsigned rs5813_mrc[2][16];
void rs5813_msg(uint32_t npc, uint32_t msg, uint32_t ra) {
    unsigned m = msg < 7 ? msg : 0; int t = 0; rs5813_all++;
    if (npc) for (unsigned i = 0; i < 256 && i < rs5813_ntrk; i++) if (rs5813_trk[i] == npc) { t = 1; break; }
    if (t && (m == 2 || m == 5)) { int q = m == 5, k = -1; for (int i = 0; i < 16; i++) { if (rs5813_mra[q][i] == ra) { k = i; break; } if (!rs5813_mra[q][i]) { rs5813_mra[q][i] = ra; k = i; break; } }
        if (k >= 0) rs5813_mrc[q][k]++;
        fprintf(stderr, "[npcsend] msg=%u npc=%08X ra=%08X all=%u ntrk=%u |", m, npc, ra, rs5813_all, rs5813_ntrk);
        for (int i = 0; i < 16 && rs5813_mra[q][i]; i++) fprintf(stderr, " %08X=%u", rs5813_mra[q][i], rs5813_mrc[q][i]);
        fprintf(stderr, "\n"); }
    rs5813_m[m]++; if (t) { rs5813_hit++; rs5813_tm[m]++; }
    if (t && (rs5813_hit <= 32 || (rs5813_hit & 63) == 0))
        fprintf(stderr, "[npcmsg] all=%u trackedmsgs=%u ntrk=%u tmsg1..6=%u,%u,%u,%u,%u,%u allmsg1..6=%u,%u,%u,%u,%u,%u\n", rs5813_all, rs5813_hit, rs5813_ntrk,
            rs5813_tm[1], rs5813_tm[2], rs5813_tm[3], rs5813_tm[4], rs5813_tm[5], rs5813_tm[6], rs5813_m[1], rs5813_m[2], rs5813_m[3], rs5813_m[4], rs5813_m[5], rs5813_m[6]);
}
void rs5813_free(uint32_t ra) {
    int k = -1; rs5813_nf++;
    if (!rs5813_en()) return;
    for (int i = 0; i < 16; i++) if (rs5813_fra[i] == ra) { k = i; break; }
    if (k < 0) for (int i = 0; i < 16; i++) if (!rs5813_fra[i]) { rs5813_fra[i] = ra; k = i; break; }
    if (k >= 0) rs5813_frc[k]++;
    if (rs5813_nf <= 32 || (rs5813_nf & 15) == 0) {
        fprintf(stderr, "[npcfree] n=%u", rs5813_nf);
        for (int i = 0; i < 16; i++) if (rs5813_fra[i]) fprintf(stderr, " ra%08X=%u", rs5813_fra[i], rs5813_frc[i]);
        fprintf(stderr, "\n");
    }
}
'''
_fe = lambda t, i: (lambda e: len(t) if e < 0 else e)(t.find("RECOMP_FUNC ", i + 12))   # s7422: whole-function idempotence
def apply(text, funcs=None):
    n = 0
    if "PATCH: s5813 helpers" not in text and "RECOMP_FUNC void npcProbeDriod(" in text:
        i = text.find("RECOMP_FUNC void npcProbeDriod("); text = text[:i] + HELP + text[i:]; n += 1
    i = text.find("RECOMP_FUNC void npcProbeDriod(")
    if i >= 0 and T1 not in text[i:_fe(text, i)]:
        a = text.find("L_800CAC40:", i); anc = "    ctx->r17 = ADD32(ctx->r2, 0);\n"
        j = text.find(anc, a); assert 0 < j - a < 3000
        k = j + len(anc); text = text[:k] + TRK + text[k:]; n += 1
    i = text.find("RECOMP_FUNC void npcProbeDriod(")
    if i >= 0 and T2 not in text[i:_fe(text, i)]:
        anc = "    ctx->r17 = MEM_W(ctx->r21, 0X4);\n"; j = text.find(anc, i); assert 0 < j - i < 12000
        k = j + len(anc)
        text = text[:k] + MSG.replace("rs5813_en_()", "rs5813_en()").replace("extern void rs5813_msg", "extern void rs5813_msg") + text[k:]; n += 1
    i = text.find("RECOMP_FUNC void unregisterAndFreeNpcSlot(")
    if i >= 0 and T3 not in text[i:_fe(text, i)]:
        anc = "    int c1cs = 0;\n"; j = text.find(anc, i); assert 0 < j - i < 300
        k = j + len(anc); text = text[:k] + FREE + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    tot = 0
    for fn in ("funcs_36.c", "funcs_8.c"):
        p = base / fn; t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        tot += n
    print("live patched x%d" % tot)
