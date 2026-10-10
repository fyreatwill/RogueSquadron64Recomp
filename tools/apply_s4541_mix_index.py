#!/usr/bin/env python3
"""s4541: the s4540 mix-call print names the caller but not the index.

At jal 0x80090F00, s0 (ctx->r16) is still the loop index. The beq delay
slot at 0x80090ECC has overwritten a1, so r5 is not the scaled offset.
Reload the base word at 0x801496F8 and the count halfword at 0x80149700,
the same absolute loads the loop uses, and print s0, base, count, and
base+s0*0x88 on the arm line, every in-range line, and the bad line.

ROGUESQ_LOG_S4539=1. Diagnostic only. Does not skip the call.
Idempotent against an already-applied s4540 helper.
"""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
marker = "s0=%u base=0x%08X count=%u sum=0x%08X"
if marker in s:
    print("already applied")
    raise SystemExit(0)

old_sig = "static void rs64_s4540_call(gpr a0g) {"
new_fn = r'''static void rs64_s4540_call(uint8_t* rdram, recomp_context* ctx) {
    uint32_t a0;
    uint32_t diff;
    uint32_t q;
    uint32_t s0;
    uint32_t mix_base;
    uint32_t mix_count;
    uint32_t sum;
    int in_range;
    int index;
    const uint32_t base = 0x801714D0u;
    const uint32_t stride = 0x88u;
    if (!rs64_s4540_enabled()) return;
    a0 = (uint32_t)ctx->r4;
    /* a1 was overwritten by the 0x80090ECC delay slot. s0 is still the index. */
    s0 = (uint32_t)ctx->r16 & 0xFFFFu;
    mix_base = (uint32_t)MEM_W(-0x6908, S32(0x8015 << 16));
    mix_count = (uint32_t)MEM_HU(-0x6900, S32(0x8015 << 16));
    sum = mix_base + s0 * 0x88u;
    rs64_s4540_n_all++;
    if (!rs64_s4540_arm) {
        rs64_s4540_arm = 1;
        fprintf(stderr,
            "[s4540-call] kind=arm a0=0x%08X n_all=%u s0=%u base=0x%08X count=%u sum=0x%08X\n",
            a0, rs64_s4540_n_all, s0, mix_base, mix_count, sum);
        fflush(stderr);
    }
    in_range = 0;
    index = -1;
    if (a0 >= base) {
        diff = a0 - base;
        if ((diff % stride) == 0u) {
            q = diff / stride;
            if (q <= 17u) {
                in_range = 1;
                index = (int)q;
            }
        }
    }
    if (in_range && !rs64_s4540_seen_idx[index]) {
        rs64_s4540_seen_idx[index] = 1;
        rs64_s4540_n_in++;
        fprintf(stderr,
            "[s4540-call] kind=in a0=0x%08X index=%d n_all=%u n_in=%u s0=%u base=0x%08X count=%u sum=0x%08X\n",
            a0, index, rs64_s4540_n_all, rs64_s4540_n_in, s0, mix_base, mix_count, sum);
        fflush(stderr);
    }
    if (a0 == 0x801724C0u && rs64_s4540_bad_rows < 4) {
        rs64_s4540_bad_rows++;
        fprintf(stderr,
            "[s4540-call] kind=bad a0=0x%08X n_all=%u n_in=%u s0=%u base=0x%08X count=%u sum=0x%08X\n",
            a0, rs64_s4540_n_all, rs64_s4540_n_in, s0, mix_base, mix_count, sum);
        fflush(stderr);
    }
}
'''

i = s.find(old_sig)
if i < 0:
    raise SystemExit("s4540 helper signature missing; apply s4540 first")
# The helper is inserted immediately before musyxMixActiveVoices.
end = s.find("\nRECOMP_FUNC void musyxMixActiveVoices", i)
if end < 0:
    raise SystemExit("musyxMixActiveVoices anchor missing after helper")
# Drop the old function, keep the blank line before RECOMP_FUNC.
s = s[:i] + new_fn + s[end + 1:]

old_call = "    rs64_s4540_call(ctx->r4); /* PATCH: s4540 */\n"
new_call = "    rs64_s4540_call(rdram, ctx); /* PATCH: s4541 */\n"
n = s.count(old_call)
if n != 1:
    raise SystemExit(f"call site count {n}")
s = s.replace(old_call, new_call, 1)

if s.count("rs64_s4540_call(") != 2:
    raise SystemExit(f"call count {s.count('rs64_s4540_call(')}")
if s.count(marker) != 3:
    raise SystemExit(f"field marker count {s.count(marker)}")
if "rs64_s4540_call(ctx->r4)" in s:
    raise SystemExit("old call site remains")
p.write_text(s)
print("applied")
