"""s6526: at the 0x80042D8C span compare dump cell idx, rec address and 30 raw rec bytes for the first
12 rejects and first 6 passes (positive control: passes must show rec3 != -2). Observation only."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
MARK = "PATCH: s6526 recdump"
if MARK in T:
    print("s6526 already applied"); raise SystemExit(0)
old = ("    if (s6505_key) { /* PATCH: s6515 span predicate */\n"
       "      s6515_span = (int8_t)ctx->r4;\n")
assert T.count(old) == 1
new = ("    if (s6505_key) { /* " + MARK + " */\n"
       "      static uint32_t s6526_nrej = 0, s6526_npas = 0;\n"
       "      int s6526_rej = SIGNED(ctx->r4) < SIGNED(ctx->r2);\n"
       "      uint32_t *s6526_n = s6526_rej ? &s6526_nrej : &s6526_npas;\n"
       "      if (s6505_key >= 745 && *s6526_n < (s6526_rej ? 12u : 6u)) { (*s6526_n)++;\n"
       "        fprintf(stderr, \"[recdump] key=%u %s span=%d idx=%u rec=%08X tbl=%08X raw=\", s6505_key, s6526_rej ? \"REJ\" : \"PASS\", (int)(int8_t)ctx->r4,\n"
       "          (unsigned)(MEM_HU(ctx->r18, 0) & 0x1FFF), (unsigned)ctx->r3, (unsigned)MEM_W(ctx->r8, 4));\n"
       "        for (int s6526_i = 0; s6526_i < 30; s6526_i++) fprintf(stderr, \"%02X\", (unsigned)(uint8_t)MEM_B(ctx->r3, s6526_i));\n"
       "        fprintf(stderr, \"\\n\"); }\n"
       "    }\n"
       "    if (s6505_key) { /* PATCH: s6515 span predicate */\n"
       "      s6515_span = (int8_t)ctx->r4;\n")
T = T.replace(old, new)
P.write_text(T); print("s6526 applied")
