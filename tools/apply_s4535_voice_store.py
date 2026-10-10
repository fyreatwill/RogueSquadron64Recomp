#!/usr/bin/env python3
"""s4535: at the two named voice+0x34 stores, log the stored word.

Sites, both in funcs_24.c:
  musyxKeyOnVoice          0x80090C80  sw v1, 0x34(s1)  v1 from s0+0x38
  musyxInitVoiceFromSample 0x800921E8  sw v1, 0x34(a0)  v1 from a1+4

One bad row per site when the word is odd or its top byte is ASCII.
Always print 0x6C617465, cap 8 per site. One in-range even control per
site (word < 0x01000000). ROGUESQ_LOG_S4535=1. The s4534 jal probe stays
in the binary and is a separate gate. Diagnostic only. Does not skip
the store. Idempotent.
"""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4535_store" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4535 voice+0x34 store. Diagnostic only. Does not skip the store. */
static void rs64_s4535_store(uint8_t* rdram, const char* site, int site_id, uint32_t pc, gpr voice, gpr stored, gpr src, uint32_t src_off) {
    static int on = -1;
    static int mark = 0;
    static unsigned seq = 0;
    static int exact_n[2];
    static int bad_n[2];
    static int ctl_n[2];
    if (on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4535");
        on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!on) return;
    if (site_id < 0 || site_id > 1) return;
    uint32_t d = (uint32_t)stored;
    uint32_t top = d >> 24;
    int exact = (d == 0x6C617465u);
    int bad = (d & 1u) || (top >= 0x20u && top < 0x7fu);
    int normal = (d < 0x01000000u) && ((d & 1u) == 0);
    uint32_t v32 = (uint32_t)voice;
    uint32_t s32 = (uint32_t)src;
    uint32_t phys = s32 & 0x1fffffffu;
    int src_ok = ((s32 >> 29) == 4u) && (phys < 0x800000u) && ((phys + src_off + 4u) <= 0x800000u);
    uint32_t srcw = 0;
    if (src_ok) srcw = (uint32_t)MEM_W(src_off, src);
    unsigned n = ++seq;
    if (!mark) {
        mark = 1;
        fprintf(stderr,
            "[s4535-store] kind=arm site=%s pc=0x%08X voice=0x%08X word=0x%08X src=0x%08X off=0x%X srcw=0x%08X src_ok=%d n=%u\n",
            site, pc, v32, d, s32, src_off, srcw, src_ok, n);
        fflush(stderr);
    }
    const char* kind = 0;
    if (exact) {
        if (exact_n[site_id] >= 8) return;
        exact_n[site_id]++;
        kind = "bad";
    } else if (bad) {
        if (bad_n[site_id] >= 1) return;
        bad_n[site_id]++;
        kind = "bad";
    } else if (normal) {
        if (ctl_n[site_id] >= 1) return;
        ctl_n[site_id]++;
        kind = "ctl";
    } else {
        return;
    }
    fprintf(stderr,
        "[s4535-store] kind=%s site=%s pc=0x%08X voice=0x%08X word=0x%08X src=0x%08X off=0x%X srcw=0x%08X src_ok=%d n=%u\n",
        kind, site, pc, v32, d, s32, src_off, srcw, src_ok, n);
    fflush(stderr);
}

'''

anchor = "RECOMP_FUNC void musyxKeyOnVoice(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"musyxKeyOnVoice anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

inserts = [
    (
        "    // 0x80090C80: sw          $v1, 0x34($s1)\n",
        '    rs64_s4535_store(rdram, "80090C80", 0, 0x80090C80u, ctx->r17, ctx->r3, ctx->r16, 0x38u); /* PATCH: s4535 */\n',
    ),
    (
        "    // 0x800921E8: sw          $v1, 0x34($a0)\n",
        '    rs64_s4535_store(rdram, "800921E8", 1, 0x800921E8u, ctx->r4, ctx->r3, ctx->r5, 0x4u); /* PATCH: s4535 */\n',
    ),
]
for comment, call in inserts:
    n = s.count(comment)
    if n != 1:
        raise SystemExit(f"anchor count {n} for {comment.strip()}")
    s = s.replace(comment, comment + call, 1)

if s.count("rs64_s4535_store(rdram") != 2:
    raise SystemExit("call count is not 2")
p.write_text(s)
print("applied")
