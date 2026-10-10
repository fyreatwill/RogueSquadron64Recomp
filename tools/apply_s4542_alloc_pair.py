#!/usr/bin/env python3
"""s4542: did allocateSongChannelArray publish count 32 with base 0x801714D0?

Prints after the 0x8008F0EC store, before the zeroing loop. count is the
halfword reloaded from 0x80149700. s0 is ctx->r16. base is ctx->r2, the
pointer just stored. Gate ROGUESQ_LOG_S4539=1. Diagnostic only. Does not
skip the store or the malloc. Does not read r31.

A line is printed when the call is the first, or (count, base) differs
from the previous printed pair. Identical pairs, including a repeated
count>=18, are not reprinted: reprinting them fills the cap and drops a
later distinct pair. A distinct pair whose count is >=18, whose base is
0x801714D0, or which is the arm control (count 16, base 0x8018D4A0) is
printed even past the cap of 48. Further non-special bases that repeat
an already-printed count>=18 are not extra publications of a new count.
Idempotent.
"""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
s = p.read_text()
if "rs64_s4542_alloc" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4542 alloc pair. Diagnostic only. Does not skip the store. */
static int rs64_s4542_on = -1;
static unsigned rs64_s4542_n = 0;
static unsigned rs64_s4542_printed = 0;
static int rs64_s4542_have = 0;
static uint32_t rs64_s4542_prev_count = 0;
static uint32_t rs64_s4542_prev_base = 0;
static uint32_t rs64_s4542_fold_count = 0xFFFFFFFFu;

static int rs64_s4542_enabled(void) {
    if (rs64_s4542_on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4539");
        rs64_s4542_on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    return rs64_s4542_on;
}

static void rs64_s4542_alloc(uint8_t* rdram, recomp_context* ctx) {
    uint32_t count;
    uint32_t s0;
    uint32_t base;
    int changed;
    int lattice;
    int arm;
    int hi;
    if (!rs64_s4542_enabled()) return;
    count = (uint32_t)MEM_HU(-0x6900, S32(0x8015 << 16));
    s0 = (uint32_t)ctx->r16 & 0xFFFFu;
    base = (uint32_t)ctx->r2;
    rs64_s4542_n++;
    changed = !rs64_s4542_have || count != rs64_s4542_prev_count || base != rs64_s4542_prev_base;
    if (!changed) return;
    lattice = (base == 0x801714D0u);
    arm = (count == 16u && base == 0x8018D4A0u);
    hi = (count >= 18u);
    if (hi && !lattice && !arm && count == rs64_s4542_fold_count) {
        rs64_s4542_prev_count = count;
        rs64_s4542_prev_base = base;
        rs64_s4542_have = 1;
        return;
    }
    if (rs64_s4542_printed >= 48u && !hi && !lattice && !arm) return;
    fprintf(stderr, "[s4542-alloc] n=%u count=%u s0=%u base=0x%08X\n",
        rs64_s4542_n, count, s0, base);
    fflush(stderr);
    if (hi && !lattice && !arm) rs64_s4542_fold_count = count;
    rs64_s4542_printed++;
    rs64_s4542_prev_count = count;
    rs64_s4542_prev_base = base;
    rs64_s4542_have = 1;
}

'''

anchor = "RECOMP_FUNC void allocateSongChannelArray(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"allocateSongChannelArray anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

call_anchor = (
    "    MEM_W(-0X6908, ctx->r1) = ctx->r2;\n"
    "    rs64_m5_lowfield_store('W', 0x8008F0ECu, U32(ADD32(ctx->r1, -0X6908)), U32(ctx->r2)); /* PATCH: s4340 lowfield writer */\n"
    "    // 0x8008F0F0: lui         $at, 0x8015\n"
)
n = s.count(call_anchor)
if n != 1:
    raise SystemExit(f"store anchor count {n}")
s = s.replace(
    call_anchor,
    "    MEM_W(-0X6908, ctx->r1) = ctx->r2;\n"
    "    rs64_m5_lowfield_store('W', 0x8008F0ECu, U32(ADD32(ctx->r1, -0X6908)), U32(ctx->r2)); /* PATCH: s4340 lowfield writer */\n"
    "    rs64_s4542_alloc(rdram, ctx); /* PATCH: s4542 */\n"
    "    // 0x8008F0F0: lui         $at, 0x8015\n",
    1,
)

if s.count("rs64_s4542_alloc(") != 2:
    raise SystemExit(f"call count {s.count('rs64_s4542_alloc(')}")
if s.count("[s4542-alloc]") != 1:
    raise SystemExit("format marker missing")
p.write_text(s)
print("applied")
