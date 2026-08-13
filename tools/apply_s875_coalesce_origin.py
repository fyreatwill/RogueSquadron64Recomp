#!/usr/bin/env python3
"""Add the s875 coalescer value-origin probe to generated funcs_*.c."""
from pathlib import Path

BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "RS64_S875_COALESCE_ORIGIN"

def add_after(text, old, new):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one anchor, found {count}: {old!r}")
    return text.replace(old, old + new, 1)

probe = r'''    { /* RS64_S875_COALESCE_ORIGIN */
        static int co_en = -1;
        static unsigned co_phase = 0xFFFFFFFFu;
        static unsigned co_n = 0;
        if (co_en < 0) { const char *e = getenv("ROGUESQ_LOG_COALESCE_ORIGIN"); co_en = (e && e[0] && e[0] != '0') ? 1 : 0; }
        if (co_en) {
            extern uint32_t rs64_phase_ord(void);
            unsigned phase = rs64_phase_ord();
            const char *m = getenv("ROGUESQ_COALESCE_ORIGIN_PHASE_MIN");
            unsigned min_phase = m ? (unsigned)strtoul(m, 0, 0) : 0;
            if (phase != co_phase) { co_phase = phase; co_n = 0; }
            if (phase >= min_phase && co_n < 4096u) {
                fprintf(stderr, "[coalesce-origin] n=%u phase=%u site=%s pc=0x%08X value=0x%08X\n", co_n, phase, SITE, PC, VALUE);
                fflush(stderr);
                ++co_n;
            }
        }
    }
'''

def make(site, pc, value):
    return probe.replace("SITE", f'"{site}"').replace("PC", pc).replace("VALUE", value)

p = BASE / "funcs_0.c"
t = p.read_text()
if MARK in t:
    raise SystemExit("s875 probe already present; regenerate funcs first")

t = add_after(t, "    MEM_W(0X63E4, ctx->r1) = ctx->r5;\n", make("partition-0x63e4", "0x80000ED8u", "U32(ctx->r5)"))
t = add_after(t, "    MEM_W(0X63E8, ctx->r1) = ctx->r4;\n", make("partition-0x63e8-fit", "0x80000FFCu", "U32(ctx->r4)"))
t = add_after(t, "    MEM_W(0X63E8, ctx->r1) = ctx->r3;\n", make("partition-0x63e8-residual", "0x80001010u", "U32(ctx->r3)"))
t = add_after(t, "    MEM_W(0X63F8, ctx->r1) = ctx->r4;\n", make("partition-0x63f8-fit", "0x80001024u", "U32(ctx->r4)"))
t = add_after(t, "    MEM_W(0X63F8, ctx->r1) = ctx->r3;\n", make("partition-0x63f8-residual", "0x80001038u", "U32(ctx->r3)"))
t = add_after(t, "    SD(0, 0X0, ctx->r8);\n", make("clear-word-0", "0x80000420u", "U32(MEM_W(0, ctx->r8))"))
t = add_after(t, "    SD(0, 0X8, ctx->r8);\n", make("clear-word-8", "0x80000424u", "U32(MEM_W(8, ctx->r8))"))
t = add_after(t, "    MEM_W(-0XE8, ctx->r1) = ctx->r16;\n", make("freelist-head", "0x800021D8u", "U32(ctx->r16)"))

if '#include <stdint.h>' not in t:
    t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <stdint.h>\n', 1)
p.write_text(t)
print(f"patched {p}")
