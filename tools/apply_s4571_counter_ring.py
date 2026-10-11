#!/usr/bin/env python3
"""s4571: the bad voice index in musyxMixActiveVoices is NOT the s0 loop index; it is the halfword at s1 = 0x80149710 + 2*buf
(lhu 0x80090ED8), incremented per rendered voice (sh at 0x80090F24) and zeroed per buffer only at 0x8009135C; the buf byte at
0x80149702 flips at 0x800917C4. H-counter-overrun: the counter is not reset between mix calls (reset skipped, or mix runs twice
per buffer). One instrument, ring of the last 96 events: E mix entry (ra, buf, ctr0, ctr1, count, a0), J render jal (s1, idx,
count, s0, a3, t0), R reset store (buf, old ctr), S buf swap (old, new). On the first J with idx >= count the ring is dumped.
Positive control: the first J overall prints kind ctl. Env ROGUESQ_LOG_S4571=1, only when vi_w>=512. Diagnostic only. Idempotent."""
from pathlib import Path
p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4571_ev" in s:
    print("already applied"); raise SystemExit(0)
HELP = r'''
extern uint32_t rs64_vi_committed_width(void);
typedef struct { char k; uint32_t a, b, c, d, e, f; } rs64_s4571_e;
static rs64_s4571_e rs64_s4571_ring[96];
static unsigned rs64_s4571_n = 0, rs64_s4571_dumped = 0, rs64_s4571_jctl = 0, rs64_s4571_mixes[2] = {0, 0}, rs64_s4571_jals[2] = {0, 0};
static int rs64_s4571_en = -1;
static int rs64_s4571_on(void) {
    if (rs64_s4571_en < 0) { const char* e = getenv("ROGUESQ_LOG_S4571"); rs64_s4571_en = (e && e[0] && e[0] != '0') ? 1 : 0; }
    return rs64_s4571_en && rs64_vi_committed_width() >= 512u;
}
static void rs64_s4571_dump(uint8_t* rdram) {
    unsigned n = rs64_s4571_n; unsigned from = n > 96 ? n - 96 : 0;
    fprintf(stderr, "[s4571-dump] events=%u mixes_since_reset=%u,%u jals_since_reset=%u,%u\n", n, rs64_s4571_mixes[0], rs64_s4571_mixes[1], rs64_s4571_jals[0], rs64_s4571_jals[1]);
    for (unsigned i = from; i < n; i++) { const rs64_s4571_e* e = &rs64_s4571_ring[i % 96];
        fprintf(stderr, "[s4571-ev] #%u %c a=0x%08X b=0x%08X c=0x%08X d=0x%08X e=0x%08X f=0x%08X\n", i, e->k, e->a, e->b, e->c, e->d, e->e, e->f); }
    fprintf(stderr, "[s4571-state] buf=%u ctr0=%u ctr1=%u count=%u tbl0=0x%08X tbl1=0x%08X voicebase=0x%08X\n",
        (unsigned)MEM_BU(-0x68FE, S32(0x8015 << 16)), (unsigned)MEM_HU(-0x68F0, S32(0x8015 << 16)), (unsigned)MEM_HU(-0x68EE, S32(0x8015 << 16)),
        (unsigned)MEM_HU(-0x6900, S32(0x8015 << 16)), (unsigned)MEM_W(-0x68F8, S32(0x8015 << 16)), (unsigned)MEM_W(-0x68F4, S32(0x8015 << 16)), (unsigned)MEM_W(-0x6908, S32(0x8015 << 16)));
    fflush(stderr);
}
static void rs64_s4571_ev(uint8_t* rdram, char k, uint32_t a, uint32_t b, uint32_t c, uint32_t d, uint32_t e, uint32_t f) {
    if (!rs64_s4571_on()) return;
    unsigned buf = (unsigned)MEM_BU(-0x68FE, S32(0x8015 << 16)) & 1u;
    if (k == 'E') rs64_s4571_mixes[buf]++;
    if (k == 'J') rs64_s4571_jals[buf]++;
    if (k == 'R') { rs64_s4571_mixes[a & 1u] = 0; rs64_s4571_jals[a & 1u] = 0; }
    { rs64_s4571_e* r = &rs64_s4571_ring[rs64_s4571_n % 96]; r->k = k; r->a = a; r->b = b; r->c = c; r->d = d; r->e = e; r->f = f; rs64_s4571_n++; }
    if (k == 'J') {
        if (rs64_s4571_jctl++ == 0) fprintf(stderr, "[s4571-ctl] first J idx=%u count=%u s0=%u s1=0x%08X vi_w=%u\n", b, c, d, a, rs64_vi_committed_width());
        if (b >= c && rs64_s4571_dumped < 2) { rs64_s4571_dumped++; fprintf(stderr, "[s4571-BAD] idx=%u >= count=%u s0=%u s1=0x%08X\n", b, c, d, a); rs64_s4571_dump(rdram); }
    }
}
'''
sig = "\nRECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n    rs64_s4455_tick(0);\n"
assert s.count(sig) == 1
s = s.replace(sig, HELP + sig + "    rs64_s4571_ev(rdram, 'E', (uint32_t)ctx->r31, (uint32_t)MEM_BU(-0x68FE, S32(0x8015 << 16)), (uint32_t)MEM_HU(-0x68F0, S32(0x8015 << 16)), (uint32_t)MEM_HU(-0x68EE, S32(0x8015 << 16)), (uint32_t)MEM_HU(-0x6900, S32(0x8015 << 16)), (uint32_t)ctx->r4); /* PATCH: s4571 */\n")
j = "    rs64_s4540_call(rdram, ctx); /* PATCH: s4541 */\n"
assert s.count(j) == 1
s = s.replace(j, j + "    rs64_s4571_ev(rdram, 'J', (uint32_t)ctx->r17, (uint32_t)ctx->r3, (uint32_t)MEM_HU(-0x6900, S32(0x8015 << 16)), (uint32_t)ctx->r16 & 0xFFFFu, (uint32_t)ctx->r7, (uint32_t)ctx->r8); /* PATCH: s4571 */\n")
r = "    MEM_H(-0X68F0, ctx->r1) = 0;\n"
assert s.count(r) == 1
s = s.replace(r, "    rs64_s4571_ev(rdram, 'R', (uint32_t)MEM_BU(-0x68FE, S32(0x8015 << 16)), (uint32_t)MEM_HU(-0x68F0, ctx->r1), 0, 0, 0, 0); /* PATCH: s4571 */\n" + r)
w = "    MEM_B(-0X68FE, ctx->r1) = ctx->r2;\n"
assert s.count(w) == 1
s = s.replace(w, "    rs64_s4571_ev(rdram, 'S', (uint32_t)MEM_BU(-0x68FE, S32(0x8015 << 16)), (uint32_t)ctx->r2, 0, 0, 0, 0); /* PATCH: s4571 */\n" + w)
p.write_text(s); print("applied")
