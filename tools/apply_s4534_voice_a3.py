#!/usr/bin/env python3
"""s4534: at the four musyxRenderVoiceSamples jals to fillSampleStreamRange,
log a3 after the delay slot. One bad row when a3 is odd or its top byte is
ASCII, and one in-range even control per site. ROGUESQ_LOG_S4534=1.
Idempotent. Diagnostic only. Does not skip the call."""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4534_jal" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4534 voice a3 callsite. Diagnostic only. */
static void rs64_s4534_jal(uint8_t* rdram, const char* site, int site_id, uint32_t pc, gpr s1, gpr a3, gpr a1) {
    static int on = -1;
    static int mark = 0;
    static int ctl_mask = 0;
    static int bad_rows = 0;
    static int exact_rows = 0;
    if (on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4534");
        on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!on) return;
    uint32_t d = (uint32_t)a3;
    uint32_t top = d >> 24;
    int bad = (d & 1u) || (top >= 0x20u && top < 0x7fu);
    int normal = (d < 0x01000000u) && ((d & 1u) == 0);
    int exact = (d == 0x6C617465u);
    uint32_t s32 = (uint32_t)s1;
    uint32_t phys = s32 & 0x1fffffffu;
    int raw_ok = ((s32 >> 29) == 4u) && ((phys + 0x38u) < 0x800000u);
    uint32_t raw = 0;
    if (raw_ok) raw = (uint32_t)MEM_W(0x34, s1);
    if (!mark) {
        mark = 1;
        fprintf(stderr,
            "[s4534-jal] kind=arm site=%s pc=0x%08X s1=0x%08X raw34=0x%08X raw_ok=%d a3=0x%08X a1=0x%08X\n",
            site, pc, s32, raw, raw_ok, d, (uint32_t)a1);
        fflush(stderr);
    }
    if (bad) {
        if (exact) {
            if (exact_rows >= 4) return;
            exact_rows++;
        } else {
            if (bad_rows >= 8) return;
            bad_rows++;
        }
    } else if (normal) {
        int bit = 1 << (site_id & 7);
        if (ctl_mask & bit) return;
        ctl_mask |= bit;
    } else {
        return;
    }
    fprintf(stderr,
        "[s4534-jal] kind=%s site=%s pc=0x%08X s1=0x%08X raw34=0x%08X raw_ok=%d a3=0x%08X a1=0x%08X\n",
        bad ? "bad" : "ctl", site, pc, s32, raw, raw_ok, d, (uint32_t)a1);
    fflush(stderr);
}

'''

anchor = "RECOMP_FUNC void musyxRenderVoiceSamples(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"musyxRenderVoiceSamples anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

inserts = [
    (
        '    rs64_s2084_fill_range_edge("callsite-0x8009024C", 0x8009024Cu, ctx); /* PATCH: s2084 fill-range reachability table */\n',
        '    rs64_s4534_jal(rdram, "8009024C", 0, 0x8009024Cu, ctx->r17, ctx->r7, ctx->r5); /* PATCH: s4534 */\n',
    ),
    (
        '    rs64_s2084_fill_range_edge("callsite-0x800902CC", 0x800902CCu, ctx); /* PATCH: s2084 fill-range reachability table */\n',
        '    rs64_s4534_jal(rdram, "800902CC", 1, 0x800902CCu, ctx->r17, ctx->r7, ctx->r5); /* PATCH: s4534 */\n',
    ),
    (
        '    rs64_s2084_fill_range_edge("callsite-0x8009039C", 0x8009039Cu, ctx); /* PATCH: s2084 fill-range reachability table */\n',
        '    rs64_s4534_jal(rdram, "8009039C", 2, 0x8009039Cu, ctx->r17, ctx->r7, ctx->r5); /* PATCH: s4534 */\n',
    ),
    (
        '    rs64_s2084_fill_range_edge("callsite-0x800903F0", 0x800903F0u, ctx); /* PATCH: s2084 fill-range reachability table */\n',
        '    rs64_s4534_jal(rdram, "800903F0", 3, 0x800903F0u, ctx->r17, ctx->r7, ctx->r5); /* PATCH: s4534 */\n',
    ),
]
for comment, call in inserts:
    n = s.count(comment)
    if n != 1:
        raise SystemExit(f"anchor count {n} for {comment.strip()}")
    s = s.replace(comment, comment + call, 1)

if s.count("rs64_s4534_jal(rdram") != 4:
    raise SystemExit("call count is not 4")
p.write_text(s)
print("applied")
