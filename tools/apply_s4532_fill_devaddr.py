#!/usr/bin/env python3
"""s4532: at fillSampleStreamRange's three DMA devAddr stores, log the node
when the value is odd or has an ASCII top byte, plus one normal-offset
control per site. ROGUESQ_LOG_S4533=1. Idempotent."""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4532_devaddr" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4532 fillSampleStreamRange devAddr node dump. Diagnostic only. */
static void rs64_s4532_devaddr(uint8_t* rdram, const char* site, gpr dev, gpr size, gpr node) {
    static int on = -1;
    if (on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4533");
        on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!on) return;
    uint32_t d = (uint32_t)dev;
    uint32_t top = d >> 24;
    int bad = (d & 1u) || (top >= 0x20u && top < 0x7fu);
    int normal = (d < 0x01000000u) && ((d & 1u) == 0);
    static int ctl_mask = 0;
    static int bad_rows = 0;
    int bit = site[0] == 'F' && site[1] == 'B' ? 1 : (site[2] == '0' ? 2 : 4);
    if (!bad) {
        if (!normal || (ctl_mask & bit)) return;
        ctl_mask |= bit;
    } else if (bad_rows >= 6) {
        return;
    } else {
        bad_rows++;
    }
    uint32_t phys = (uint32_t)node & 0x1fffffffu;
    int in_ram = (phys + 0x18u) < 0x800000u && (((uint32_t)node >> 29) == 4u);
    uint32_t w0 = 0, w4 = 0, w8 = 0, wc = 0, w10 = 0, w14 = 0;
    if (in_ram) {
        w0 = (uint32_t)MEM_W(0x0, node);
        w4 = (uint32_t)MEM_W(0x4, node);
        w8 = (uint32_t)MEM_W(0x8, node);
        wc = (uint32_t)MEM_W(0xC, node);
        w10 = (uint32_t)MEM_W(0x10, node);
        w14 = (uint32_t)MEM_W(0x14, node);
    }
    fprintf(stderr,
        "[s4532-fill] kind=%s site=%s dev=0x%08X size=0x%08X node=0x%08X in_ram=%d w0=%08X w4=%08X w8=%08X wC=%08X w10=%08X w14=%08X\n",
        bad ? "bad" : "ctl", site, d, (uint32_t)size, (uint32_t)node, in_ram, w0, w4, w8, wc, w10, w14);
    fflush(stderr);
}

'''

anchor = "RECOMP_FUNC void fillSampleStreamRange(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"fillSampleStreamRange anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

inserts = [
    (
        "    // 0x8008FB64: sw          $v0, 0x4($a0)\n",
        '    rs64_s4532_devaddr(rdram, "FB64", ctx->r2, ctx->r6, ctx->r8); /* PATCH: s4532 */\n',
    ),
    (
        "    // 0x8008FE04: sw          $v1, 0x4($v0)\n",
        '    rs64_s4532_devaddr(rdram, "FE04", ctx->r3, ctx->r14, ctx->r8); /* PATCH: s4532 */\n',
    ),
    (
        "    // 0x8008FE98: sw          $v1, 0x4($v0)\n",
        '    rs64_s4532_devaddr(rdram, "FE98", ctx->r3, MEM_W(0x10, ctx->r8), ctx->r8); /* PATCH: s4532 */\n',
    ),
]
for comment, call in inserts:
    n = s.count(comment)
    if n != 1:
        raise SystemExit(f"anchor count {n} for {comment.strip()}")
    s = s.replace(comment, comment + call, 1)

p.write_text(s)
print("applied")
