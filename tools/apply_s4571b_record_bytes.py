#!/usr/bin/env python3
"""s4571b: s4571 showed idx>=count is the normal 2nd-chunk case (mix is driven in 0xC0-sample chunks from 3 call sites, the per-buffer
counter at 0x80149710+2*buf is a record cursor reset once per buffer). So the question becomes whether the record at tbl[buf]+idx*0x88
is legitimately initialised. Adds, at each render jal: PRE words 0..7 of the record before the call and POST words after, classed
in-range (idx<count) vs chunk2+ (idx>=count); capacity (0x80149704) and per-voice factor (0x8014974E) in the header; per-class counters
of records whose pre-words 0..7 contain an ASCII-shaped word (all 4 bytes 0x20..0x7E) and of records whose post differs from pre.
Prints the first 4 rows per class, any ASCII-pre row (budget 40), and class totals every 4000 jals. Needs apply_s4571_counter_ring.py first.
Env ROGUESQ_LOG_S4571=1, vi_w>=512. Diagnostic only. Idempotent."""
from pathlib import Path
p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4571_pre" in s:
    print("already applied"); raise SystemExit(0)
HELP = r'''
static uint32_t rs64_s4571_prew[8];
static unsigned rs64_s4571_cls_n[2], rs64_s4571_cls_ascii[2], rs64_s4571_cls_chg[2], rs64_s4571_cls_rows[2], rs64_s4571_asc_rows = 0, rs64_s4571_jtot = 0;
static int rs64_s4571_ascii_word(uint32_t w) {
    for (int i = 0; i < 4; i++) { uint32_t b = (w >> (8 * i)) & 0xFFu; if (b < 0x20u || b > 0x7Eu) return 0; }
    return 1;
}
static void rs64_s4571_totals(uint8_t* rdram, const char* why) {
    fprintf(stderr, "[s4571-tot] %s jals=%u inrange n=%u ascii=%u changed=%u | chunk2+ n=%u ascii=%u changed=%u cap=%u k=%u count=%u\n", why, rs64_s4571_jtot,
        rs64_s4571_cls_n[0], rs64_s4571_cls_ascii[0], rs64_s4571_cls_chg[0], rs64_s4571_cls_n[1], rs64_s4571_cls_ascii[1], rs64_s4571_cls_chg[1],
        (unsigned)MEM_HU(-0x68FC, S32(0x8015 << 16)), (unsigned)MEM_HU(-0x68B2, S32(0x8015 << 16)), (unsigned)MEM_HU(-0x6900, S32(0x8015 << 16)));
    fflush(stderr);
}
static void rs64_s4571_pre(uint8_t* rdram, uint32_t a3, uint32_t idx, uint32_t count) {
    if (!rs64_s4571_on()) return;
    for (int i = 0; i < 8; i++) rs64_s4571_prew[i] = (uint32_t)MEM_W(i * 4, (int32_t)a3);
}
static void rs64_s4571_post(uint8_t* rdram, uint32_t a3, uint32_t idx, uint32_t count) {
    if (!rs64_s4571_on()) return;
    unsigned c = idx >= count ? 1u : 0u; unsigned asc = 0, chg = 0; uint32_t w[8];
    for (int i = 0; i < 8; i++) { w[i] = (uint32_t)MEM_W(i * 4, (int32_t)a3); if (rs64_s4571_ascii_word(rs64_s4571_prew[i])) asc = 1; if (w[i] != rs64_s4571_prew[i]) chg = 1; }
    rs64_s4571_cls_n[c]++; rs64_s4571_cls_ascii[c] += asc; rs64_s4571_cls_chg[c] += chg; rs64_s4571_jtot++;
    int row = 0;
    if (rs64_s4571_cls_rows[c] < 4) { rs64_s4571_cls_rows[c]++; row = 1; }
    else if (asc && rs64_s4571_asc_rows < 40) { rs64_s4571_asc_rows++; row = 2; }
    if (row) {
        fprintf(stderr, "[s4571-rec] %s cls=%s idx=%u count=%u a3=0x%08X pre=%08X %08X %08X %08X %08X %08X %08X %08X post=%08X %08X %08X %08X %08X %08X %08X %08X\n", row == 1 ? "first" : "ascii", c ? "chunk2+" : "inrange", idx, count, a3,
            rs64_s4571_prew[0], rs64_s4571_prew[1], rs64_s4571_prew[2], rs64_s4571_prew[3], rs64_s4571_prew[4], rs64_s4571_prew[5], rs64_s4571_prew[6], rs64_s4571_prew[7],
            w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7]);
        fflush(stderr);
    }
    if ((rs64_s4571_jtot % 4000u) == 0) rs64_s4571_totals(rdram, "periodic");
}
'''
sig = "\nRECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
assert s.count(sig) == 1
s = s.replace(sig, HELP + sig)
j = "    musyxRenderVoiceSamples(rdram, ctx);\n    rs64_s4205_rec(rdram, s4205_rec, (gpr)ctx->r17); }\n"
assert s.count(j) == 1, s.count(j)
# idx (r3) and count survive the callee only if saved: capture before the call.
pre = "    uint32_t s4571_a3 = (uint32_t)ctx->r7, s4571_idx = (uint32_t)ctx->r3, s4571_cnt = (uint32_t)MEM_HU(-0x6900, S32(0x8015 << 16)); rs64_s4571_pre(rdram, s4571_a3, s4571_idx, s4571_cnt); /* PATCH: s4571b */\n"
post = "    rs64_s4571_post(rdram, s4571_a3, s4571_idx, s4571_cnt); }\n"
j2 = j[:-len(" }\n")] + "\n"
s = s.replace(j, pre + j2 + post)
fwd = "extern uint32_t rs64_vi_committed_width(void);\ntypedef struct { char k;"
assert s.count(fwd) == 1
s = s.replace(fwd, "static void rs64_s4571_totals(uint8_t* rdram, const char* why);\n" + fwd)
# Totals when the BAD dump fires.
d = "fprintf(stderr, \"[s4571-BAD] idx=%u >= count=%u s0=%u s1=0x%08X\\n\", b, c, d, a); rs64_s4571_dump(rdram); }"
if d in s:
    s = s.replace(d, d[:-1] + " rs64_s4571_totals(rdram, \"bad\"); }")
p.write_text(s); print("applied")
