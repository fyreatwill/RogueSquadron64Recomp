"""s6513: per-cell span-filter decision joined to the keyed stream return.

Logs the signed span bytes read at 0x80042D50, before DB4/DC0 can rewrite
them, plus the eight-site writer mask at that decision. Printed on the
existing ROGUESQ_FORFACE_LOG return budget. No guard and no behavior change.
"""

from pathlib import Path

P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
MARK = "PATCH: s6513 span filter"
if MARK in T:
    print("s6513 already applied")
    raise SystemExit(0)


def rep(old, new, expect=1):
    global T
    n = T.count(old)
    assert n == expect, (old[:70], n)
    T = T.replace(old, new)


rep(
    "    uint32_t s6505_key = 0, s6505_start[4] = {0, 0, 0, 0};\n",
    "    uint32_t s6505_key = 0, s6505_start[4] = {0, 0, 0, 0};\n"
    "    uint32_t s6513_nd = 0, s6513_n127 = 0, s6513_n80 = 0, s6513_noth = 0;\n"
    "    uint32_t s6513_nclear = 0, s6513_nskip = 0, s6513_npass = 0, s6513_ns = 0, s6513_npop = 0, s6513_nsent = 0;\n"
    "    uint32_t s6513_w0[8] = {0, 0, 0, 0, 0, 0, 0, 0};\n"
    "    uint32_t s6513_addr[8] = {0, 0, 0, 0, 0, 0, 0, 0};\n"
    "    uint32_t s6513_wbit[8] = {0, 0, 0, 0, 0, 0, 0, 0};\n"
    "    uint16_t s6513_row[8] = {0, 0, 0, 0, 0, 0, 0, 0};\n"
    "    uint16_t s6513_col[8] = {0, 0, 0, 0, 0, 0, 0, 0};\n"
    "    int8_t s6513_s0[8] = {0, 0, 0, 0, 0, 0, 0, 0};\n"
    "    int8_t s6513_s1[8] = {0, 0, 0, 0, 0, 0, 0, 0}; /* " + MARK + " */\n",
)

rep(
    "        for (int i = 0; i < 4; i++) s6505_startmask[i] = s6500_wmask[i];\n",
    "        for (int i = 0; i < 4; i++) s6505_startmask[i] = s6500_wmask[i];\n"
    "        for (int i = 0; i < 8; i++) s6513_w0[i] = s6512_n[i];\n",
)

rep(
    "    ctx->r4 = MEM_B(ctx->r21, 0X0);\n",
    "    ctx->r4 = MEM_B(ctx->r21, 0X0);\n"
    "    if (s6505_key) { /* " + MARK + " */\n"
    "      int8_t s0 = (int8_t)ctx->r4;\n"
    "      uint32_t idx = (uint32_t)ctx->r5;\n"
    "      int8_t s1 = (int8_t)MEM_B(0, (int64_t)(int32_t)(0x80131DB0u + idx));\n"
    "      int pop = (s0 != 127 && (uint8_t)s0 != 0x80u);\n"
    "      s6513_nd++;\n"
    "      if (s0 == 127) s6513_n127++; else if ((uint8_t)s0 == 0x80u) s6513_n80++; else s6513_noth++;\n"
    "      int take = 0;\n"
    "      if (pop && s6513_npop < 4) { s6513_npop++; take = 1; }\n"
    "      else if (!pop && s6513_nsent < 4) { s6513_nsent++; take = 1; }\n"
    "      if (take && s6513_ns < 8) {\n"
    "        uint32_t si = s6513_ns++;\n"
    "        s6513_row[si] = (uint16_t)ctx->r30; s6513_col[si] = (uint16_t)ctx->r20;\n"
    "        s6513_s0[si] = s0; s6513_s1[si] = s1; s6513_addr[si] = 0x80130DB0u + idx; s6513_wbit[si] = 0;\n"
    "        for (int wi = 0; wi < 8; wi++) if (s6512_n[wi] != s6513_w0[wi]) s6513_wbit[si] |= 1u << wi;\n"
    "      }\n"
    "    }\n",
)

rep(
    "        g_s6493[4]++; /* PATCH: s6493 streamcum */\n",
    "        g_s6493[4]++; if (s6505_key) s6513_nskip++; /* PATCH: s6493 streamcum */\n",
)

rep(
    "s6500_note_writer(0x80042DB4u, U32(ctx->r3), U32(ctx->r2)); MEM_B(0X0, ctx->r2) = ctx->r3; RS64_S5798_ST(0x80042DB4u, 0X0, ctx->r2, 1);",
    "s6500_note_writer(0x80042DB4u, U32(ctx->r3), U32(ctx->r2)); if (s6505_key) s6513_nclear++; MEM_B(0X0, ctx->r2) = ctx->r3; RS64_S5798_ST(0x80042DB4u, 0X0, ctx->r2, 1);",
)

rep(
    "L_80042DC4:\n",
    "L_80042DC4:\n    if (s6505_key) s6513_npass++; /* " + MARK + " */\n",
)

old_tail = "s6500_wmask[3] ^ s6505_startmask[3]); } } } /* PATCH: s6493b emptydump */"
new_tail = (
    "s6500_wmask[3] ^ s6505_startmask[3]); "
    "fprintf(stderr, \"[span-filter] key=%u %s nd=%u n127=%u n80=%u nother=%u nclear=%u nskip=%u npass=%u "
    "wentry=%u,%u,%u,%u,%u,%u,%u,%u wend=%u,%u,%u,%u,%u,%u,%u,%u w=%d,%d,%d,%d samples=\", "
    "s6505_key, emp ? \"EMPTY\" : \"ok\", s6513_nd, s6513_n127, s6513_n80, s6513_noth, s6513_nclear, s6513_nskip, s6513_npass, "
    "s6513_w0[0], s6513_w0[1], s6513_w0[2], s6513_w0[3], s6513_w0[4], s6513_w0[5], s6513_w0[6], s6513_w0[7], "
    "s6512_n[0], s6512_n[1], s6512_n[2], s6512_n[3], s6512_n[4], s6512_n[5], s6512_n[6], s6512_n[7], "
    "(int)MEM_W(0, (int64_t)(int32_t)0x80132DB0), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB4), "
    "(int)MEM_W(0, (int64_t)(int32_t)0x80132DB8), (int)MEM_W(0, (int64_t)(int32_t)0x80132DBC)); "
    "for (uint32_t si = 0; si < s6513_ns; si++) { int8_t post = (int8_t)MEM_B(0, (int64_t)(int32_t)s6513_addr[si]); "
    "int8_t post1 = (int8_t)MEM_B(0, (int64_t)(int32_t)(s6513_addr[si] + 0x1000u)); "
    "fprintf(stderr, \"%u:%u:%d:%d:%d:%d:%02x,\", s6513_row[si], s6513_col[si], (int)s6513_s0[si], (int)s6513_s1[si], (int)post, (int)post1, s6513_wbit[si]); } "
    "fprintf(stderr, \"\\n\"); } } } /* PATCH: s6493b emptydump */"
)
rep(old_tail, new_tail)
P.write_text(T)
print("s6513 applied")
