"""s5838: effect of msg-5 hit SENDs. At the SEND hook (0x8005D35C, audioCueDispatcherNpcHandler, funcs_13.c) snapshot 64 words of the victim
node and of its descriptor (node+0x34); at a tick (hook before 0x8005D238, each candidate) >=150 ms and >=1000 ms later re-read and print changed word
offsets (old->new). who = P (projectile shooter == player) / N. Under ROGUESQ_LOG_HITS=1. Control = N sends. Read-only."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5838 send effect"
H = r'''/* PATCH: s5838 helpers */
#include <time.h>
struct rs5838_p { uint32_t n, d, w; double t; uint32_t sn[64], sd[64]; unsigned stage; unsigned who; };
static struct rs5838_p rs5838_q[24]; static unsigned rs5838_qn, rs5838_sent[2], rs5838_en = 2;
static double rs5838_now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6; }
static int rs5838_ok(uint32_t p) { return (p >> 24) == 0x80; }
static void rs5838_snap(uint8_t* rdram, uint32_t n, uint32_t d, uint32_t* sn, uint32_t* sd) {
    for (int i = 0; i < 64; i++) { sn[i] = rs5838_ok(n) ? (uint32_t)MEM_W(S32((int32_t)n), 4 * i) : 0; sd[i] = rs5838_ok(d) ? (uint32_t)MEM_W(S32((int32_t)d), 4 * i) : 0; }
}
static void rs5838_tick(uint8_t* rdram) {
    if (rs5838_en == 2) { const char* e = getenv("ROGUESQ_LOG_HITS"); rs5838_en = (e && e[0] == '1'); }
    if (!rs5838_en || !rs5838_qn) return;
    double now = rs5838_now();
    for (unsigned k = 0; k < rs5838_qn; k++) {
        struct rs5838_p* q = &rs5838_q[k];
        double lim = q->stage == 0 ? 150.0 : 1000.0;
        if (q->stage > 1 || now - q->t < lim) continue;
        uint32_t cn[64], cd[64]; rs5838_snap(rdram, q->n, q->d, cn, cd);
        fprintf(stderr, "[eff] %s victim=%04x n=%08x d=%08x dt=%.0fms w=%u changed:", q->who ? "N" : "P", q->w, q->n, q->d, now - q->t, q->stage);
        unsigned c = 0;
        for (int i = 0; i < 64 && c < 14; i++) if (cn[i] != q->sn[i]) { fprintf(stderr, " n+%x:%08x>%08x", 4 * i, q->sn[i], cn[i]); c++; }
        for (int i = 0; i < 64 && c < 28; i++) if (cd[i] != q->sd[i]) { fprintf(stderr, " d+%x:%08x>%08x", 4 * i, q->sd[i], cd[i]); c++; }
        fprintf(stderr, "\n");
        q->stage++;
        if (q->stage > 1) { *q = rs5838_q[--rs5838_qn]; k--; }
    }
}
static void rs5838_send(uint8_t* rdram, uint32_t proj, uint32_t cand) {
    if (rs5838_en == 2) { const char* e = getenv("ROGUESQ_LOG_HITS"); rs5838_en = (e && e[0] == '1'); }
    if (!rs5838_en) return;
    unsigned who = ((uint32_t)MEM_HU(S32((int32_t)proj), 0XF8) == (uint32_t)MEM_HU(S32((int32_t)0x80137DBAu), 0)) ? 0 : 1;
    uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0); uint32_t n = (uint32_t)MEM_W(S32((int32_t)(tb + (cand & 0xFFFF) * 8)), 0);
    if (!rs5838_ok(n)) return;
    uint32_t o = (uint32_t)MEM_W(S32((int32_t)n), 4); uint32_t d = rs5838_ok(o) ? (uint32_t)MEM_W(S32((int32_t)o), 0X34) : 0; /* s5886: NPC obj is slot+4 */
    if (rs5838_sent[who] <= 4000) fprintf(stderr, "[eff2] SEND %s victim=%04x n=%08x d=%08x cls=%u shooter=%04x\n", who ? "N" : "P", cand & 0xFFFF, n, d, rs5838_ok(d) ? (unsigned)MEM_W(S32((int32_t)d), 0X70) : 99u, (unsigned)MEM_HU(S32((int32_t)proj), 0XF8));
    if (rs5838_sent[who]++ >= 12 || rs5838_qn >= 24) return;
    struct rs5838_p* q = &rs5838_q[rs5838_qn++]; q->n = n; q->d = d; q->w = cand & 0xFFFF; q->t = rs5838_now(); q->stage = 0; q->who = who;
    rs5838_snap(rdram, n, d, q->sn, q->sd);
    fprintf(stderr, "[eff] SEND %s victim=%04x n=%08x d=%08x dmg=%08x\n", who ? "N" : "P", q->w, n, d, (uint32_t)MEM_W(S32((int32_t)proj), 0XFC));
}
'''
FN = "RECOMP_FUNC void audioCueDispatcherNpcHandler("
TICK = "    rs5838_tick(rdram); /* %s */\n" % T
SEND = "    rs5838_send(rdram, (uint32_t)ctx->r17, (uint32_t)(ctx->r4 & 0xFFFF)); /* %s */\n" % T
HOOKS = [("    // 0x8005D238: beq         $a0, $zero, L_8005D270\n", TICK),
         ("    // 0x8005D35C: jal         0x8003E8DC\n", SEND)]
def apply(text, name=None):
    if T in text: return text, 0
    i = text.find(FN)
    if i < 0: return text, 0
    n = 0
    for a, h in HOOKS:
        j = text.find(a, i)
        if j < 0: return text, 0
        # insert before earlier s5833 hook lines directly preceding the anchor is unnecessary; plain insert is fine
        text = text[:j] + h + text[j:]; n += 1
    i = text.find(FN)
    return text[:i] + H + text[i:], n + 1
if __name__ == "__main__":
    p = base / "funcs_13.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_13.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5838_send_effect" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_13.c":\n'
               '        import apply_s5838_send_effect as _a5838\n'
               '        text, _n5838 = _a5838.apply(text)\n'
               '        if _n5838:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5838 send effect x{_n5838}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5835_sphere_probe.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5838_send_effect.py",\n', 1)
        fp.write_text(s); print("fixup patched")
