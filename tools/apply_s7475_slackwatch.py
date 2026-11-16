"""s7475 class ED: name the writer of every guest store into heap-block slack.

The s7475 canary (src/main/upstream_compat.cpp, ROGUESQ_S7475_CANARY=1) fills the bytes [ptr+req, ptr+size) of each
rs_malloc block with 0xA5 and marks them in a 1-bit-per-byte bitmap g_rs64_s7475_bm over KSEG0 0x80000000..0x81800000
(NULL unless the canary is on). This patch adds to the per-store s5798 macro (needs g_rs64_store_diag, so set
ROGUESQ_STORE_DIAG=1) a test of the first and last byte of each store against that bitmap, and a dispatch at the top of
rs64_s5798_st that calls rs64_s7475_store(pc, a, w, fn) (returns: the s5798 tail indexes its own fixed table and must not see a slack address; s7475 v1 fell through and SIGBUSed). The host side
logs `[s7475] slack-store pc= fn= a= blk= req= off= w= alloc=<host caller symbol>`.
Blind to host writers (memcpy / PI DMA / RSP); a canary tail-hit with no slack-store row names a host writer.
Measurement only: no game value is changed. Idempotent; mirrored in fixup_game_funcs_vendored.py's apply list."""
from pathlib import Path
import re
D = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7475 slackwatch"
COND = ("(g_rs64_s7475_bm && (uint32_t)(_a5798 - 0x80000000u) < 0x1800000u && "
        "(((g_rs64_s7475_bm[(_a5798 - 0x80000000u) >> 3] >> (_a5798 & 7u)) | "
        "(g_rs64_s7475_bm[(_a5798 + (uint32_t)(w) - 1u - 0x80000000u) >> 3] >> ((_a5798 + (uint32_t)(w) - 1u) & 7u))) & 1u)) || ")
n = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if "#define RS64_S5798_ST" not in t or MARK in t:
        continue
    new, k = re.subn(r"(_a5798 = \(uint32_t\)\(\(base\) \+ \(off\)\); if \()", lambda m: m.group(1) + COND, t, count=1)
    if k:
        new = new.replace("#define RS64_S5798_ST", "/* " + MARK + " */\nextern unsigned char* g_rs64_s7475_bm;\n#define RS64_S5798_ST", 1)
        p.write_text(new); n += 1
print("s7475 macro patched in", n, "files")
P = D / "funcs_13.c"
T = P.read_text()
anchor = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
assert T.count(anchor) == 1
if "rs64_s7475_store(pc, a, w, fn); /* " + MARK in T:
    T = T.replace("extern void rs64_s7475_store(", "extern int rs64_s7475_store(", 1)
    T = T.replace("&& (uint32_t)(a - 0x80000000u) < 0x1800000u) rs64_s7475_store(pc, a, w, fn); /*", "&& (uint32_t)(a - 0x80000000u) < 0x1800000u && rs64_s7475_store(pc, a, w, fn)) return; /*", 1)
    P.write_text(T); print("s7475 handler upgraded to returning form")
elif "rs64_s7475_store" in T:
    print("s7475 handler already present")
else:
    decl = "/* " + MARK + " helper */\nextern int rs64_s7475_store(uint32_t pc, uint32_t a, int w, const char* fn);\n"
    T = T.replace(anchor, decl + anchor + "    if (g_rs64_s7475_bm && (uint32_t)(a - 0x80000000u) < 0x1800000u && rs64_s7475_store(pc, a, w, fn)) return; /* " + MARK + " */\n", 1)
    P.write_text(T); print("s7475 handler added")
