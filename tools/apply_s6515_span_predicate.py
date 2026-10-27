"""s6515: split span-filter clears by the two live compares.

0x80042D8C rejects when span < cell+3. 0x80042DA4 rejects when cell+4 <
the second-plane byte. Counts and the first four operand pairs of each
are printed on the existing keyed return. No guard and no behavior change.
"""

from pathlib import Path

P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
MARK = "PATCH: s6515 span predicate"
if MARK in T:
    print("s6515 already applied")
    raise SystemExit(0)


def rep(old, new, expect=1):
    global T
    n = T.count(old)
    assert n == expect, (old[:80], n)
    T = T.replace(old, new)


rep(
    "    int8_t s6513_s1[8] = {0, 0, 0, 0, 0, 0, 0, 0}; /* PATCH: s6513 span filter */\n",
    "    int8_t s6513_s1[8] = {0, 0, 0, 0, 0, 0, 0, 0}; /* PATCH: s6513 span filter */\n"
    "    uint32_t s6515_ns0 = 0, s6515_ns1 = 0, s6515_ns1_127 = 0, s6515_ns0s = 0, s6515_ns1s = 0;\n"
    "    int8_t s6515_span = 0;\n"
    "    int8_t s6515_s0a[4] = {0, 0, 0, 0}, s6515_s0b[4] = {0, 0, 0, 0};\n"
    "    int8_t s6515_s1a[4] = {0, 0, 0, 0}, s6515_s1b[4] = {0, 0, 0, 0}, s6515_s1c[4] = {0, 0, 0, 0}; /* "
    + MARK + " */\n",
)

rep(
    "    // 0x80042D88: lb          $v0, 0x3($v1)\n"
    "    ctx->r2 = MEM_B(ctx->r3, 0X3);\n"
    "    // 0x80042D8C: slt         $v0, $a0, $v0\n"
    "    ctx->r2 = SIGNED(ctx->r4) < SIGNED(ctx->r2) ? 1 : 0;\n",
    "    // 0x80042D88: lb          $v0, 0x3($v1)\n"
    "    ctx->r2 = MEM_B(ctx->r3, 0X3);\n"
    "    if (s6505_key) { /* " + MARK + " */\n"
    "      s6515_span = (int8_t)ctx->r4;\n"
    "      int8_t c3 = (int8_t)ctx->r2;\n"
    "      if (SIGNED(ctx->r4) < SIGNED(ctx->r2)) {\n"
    "        s6515_ns0++;\n"
    "        if (s6515_ns0s < 4) { uint32_t i = s6515_ns0s++; s6515_s0a[i] = s6515_span; s6515_s0b[i] = c3; }\n"
    "      }\n"
    "    }\n"
    "    // 0x80042D8C: slt         $v0, $a0, $v0\n"
    "    ctx->r2 = SIGNED(ctx->r4) < SIGNED(ctx->r2) ? 1 : 0;\n",
)

rep(
    "    // 0x80042D9C: lb          $v0, 0x4($v1)\n"
    "    ctx->r2 = MEM_B(ctx->r3, 0X4);\n"
    "    // 0x80042DA0: lb          $v1, 0x0($s3)\n"
    "    ctx->r3 = MEM_B(ctx->r19, 0X0);\n"
    "    // 0x80042DA4: slt         $v0, $v0, $v1\n"
    "    ctx->r2 = SIGNED(ctx->r2) < SIGNED(ctx->r3) ? 1 : 0;\n",
    "    // 0x80042D9C: lb          $v0, 0x4($v1)\n"
    "    ctx->r2 = MEM_B(ctx->r3, 0X4);\n"
    "    // 0x80042DA0: lb          $v1, 0x0($s3)\n"
    "    ctx->r3 = MEM_B(ctx->r19, 0X0);\n"
    "    if (s6505_key) { /* " + MARK + " */\n"
    "      int8_t c4 = (int8_t)ctx->r2;\n"
    "      int8_t pl = (int8_t)ctx->r3;\n"
    "      if (SIGNED(ctx->r2) < SIGNED(ctx->r3)) {\n"
    "        s6515_ns1++;\n"
    "        if (pl == 127 && c4 < 127) s6515_ns1_127++;\n"
    "        if (s6515_ns1s < 4) { uint32_t i = s6515_ns1s++; s6515_s1a[i] = s6515_span; s6515_s1b[i] = c4; s6515_s1c[i] = pl; }\n"
    "      }\n"
    "    }\n"
    "    // 0x80042DA4: slt         $v0, $v0, $v1\n"
    "    ctx->r2 = SIGNED(ctx->r2) < SIGNED(ctx->r3) ? 1 : 0;\n",
)

rep(
    'fprintf(stderr, "\\n"); } } } /* PATCH: s6493b emptydump */',
    'fprintf(stderr, "\\n"); '
    'fprintf(stderr, "[span-pred] key=%u %s ns0=%u ns1=%u ns1_127=%u npass=%u nskip=%u nclear=%u nd=%u sum=%u s0=", '
    's6505_key, emp ? "EMPTY" : "ok", s6515_ns0, s6515_ns1, s6515_ns1_127, s6513_npass, s6513_nskip, s6513_nclear, s6513_nd, '
    's6515_ns0 + s6515_ns1 + s6513_npass + s6513_nskip); '
    'for (uint32_t s6515_i = 0; s6515_i < s6515_ns0s; s6515_i++) fprintf(stderr, "%d<%d,", (int)s6515_s0a[s6515_i], (int)s6515_s0b[s6515_i]); '
    'fprintf(stderr, " s1="); '
    'for (uint32_t s6515_i = 0; s6515_i < s6515_ns1s; s6515_i++) fprintf(stderr, "%d:%d<%d,", (int)s6515_s1a[s6515_i], (int)s6515_s1b[s6515_i], (int)s6515_s1c[s6515_i]); '
    'fprintf(stderr, "\\n"); } } } /* PATCH: s6493b emptydump */',
)

P.write_text(T)
print("s6515 applied")
