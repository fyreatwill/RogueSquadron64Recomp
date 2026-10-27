"""s6516: log the cell record (index, table base, address, bytes +0..+5) read at
0x80042D88, per keyed invocation, bounded. Observation only; no behavior change.
"""

from pathlib import Path

P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
MARK = "PATCH: s6516 cell record"
if MARK in T:
    print("s6516 already applied")
    raise SystemExit(0)


def rep(old, new, expect=1):
    global T
    n = T.count(old)
    assert n == expect, (old[:80], n)
    T = T.replace(old, new)


rep(
    "    int8_t s6515_span = 0;\n",
    "    int8_t s6515_span = 0;\n    uint32_t s6516_n = 0; /* " + MARK + " */\n",
)

rep(
    "      s6515_span = (int8_t)ctx->r4;\n      int8_t c3 = (int8_t)ctx->r2;\n",
    "      s6515_span = (int8_t)ctx->r4;\n      int8_t c3 = (int8_t)ctx->r2;\n"
    "      if (s6516_n < 24) { s6516_n++; uint32_t cell = (uint32_t)ctx->r3; uint32_t base = (uint32_t)MEM_W(4, ctx->r8);\n"
    "        uint32_t idx = (uint32_t)MEM_HU(0, ctx->r18) & 0x1FFF;\n"
    "        fprintf(stderr, \"[cell-rec] key=%u span=%d plane=%d idx=%u base=%08X cell=%08X off=%d b=%02X %02X %02X %02X %02X %02X %s\\n\", s6505_key, (int)s6515_span, (int)(int8_t)MEM_B(0, ctx->r19), idx, base, cell, (int)(cell - base), "
    "(uint8_t)MEM_B(ctx->r3, 0), (uint8_t)MEM_B(ctx->r3, 1), (uint8_t)MEM_B(ctx->r3, 2), (uint8_t)MEM_B(ctx->r3, 3), (uint8_t)MEM_B(ctx->r3, 4), (uint8_t)MEM_B(ctx->r3, 5), "
    "SIGNED(ctx->r4) < SIGNED(ctx->r2) ? \"s0clear\" : \"pass0\"); } /* " + MARK + " */\n",
)
P.write_text(T)
print("s6516 applied")
