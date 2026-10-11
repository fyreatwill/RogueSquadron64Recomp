#!/usr/bin/env python3
"""s4579: which thread runs musyxMixActiveVoices while allocateSongChannelArray is inside rs_malloc?
Events (stderr, env ROGUESQ_LOG_S4579=1): [s4579-A] alloc pre-rs_malloc (host tid, guest sp, count a0, ra), [s4579-P] post-rs_malloc,
[s4579-M] each mixer entry whose count (0x80149700 half) > 18 OR that occurs while an alloc is in flight (host tid, sp, in-flight alloc tid/sp,
count, ra), first 40 only. Positive control: alloc #1..#5 print matched A/P pairs with the same tid. Diagnostic only. Idempotent."""
from pathlib import Path
D = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
HELP = r'''
#include <pthread.h>
static volatile int rs64_s4579_inflight = 0; static volatile unsigned long rs64_s4579_atid = 0; static volatile uint32_t rs64_s4579_asp = 0; static unsigned rs64_s4579_na = 0, rs64_s4579_nm = 0;
static int rs64_s4579_en = -1;
static int rs64_s4579_on(void) { if (rs64_s4579_en < 0) { const char* e = getenv("ROGUESQ_LOG_S4579"); rs64_s4579_en = (e && e[0] && e[0] != '0') ? 1 : 0; } return rs64_s4579_en; }
static void rs64_s4579_alloc(uint8_t* rdram, recomp_context* ctx, char k) {
    if (!rs64_s4579_on()) return;
    unsigned long t = (unsigned long)(uintptr_t)pthread_self();
    if (k == 'A') { rs64_s4579_inflight = 1; rs64_s4579_atid = t; rs64_s4579_asp = (uint32_t)ctx->r29; rs64_s4579_na++; }
    else rs64_s4579_inflight = 0;
    fprintf(stderr, "[s4579-%c] n=%u tid=%lx sp=%08X a0=%u ra=%08X v0=%08X cnt=%u\n", k, rs64_s4579_na, t, (uint32_t)ctx->r29, (uint32_t)ctx->r4 & 0xFFFFu, (uint32_t)ctx->r31, (uint32_t)ctx->r2, (unsigned)MEM_HU(-0x6900, S32(0x8015 << 16)));
    fflush(stderr);
}
static void rs64_s4579_mix(uint8_t* rdram, recomp_context* ctx) {
    if (!rs64_s4579_on()) return;
    unsigned cnt = (unsigned)MEM_HU(-0x6900, S32(0x8015 << 16));
    if (!(cnt > 20 || rs64_s4579_inflight) || rs64_s4579_nm >= 40) return;
    rs64_s4579_nm++;
    fprintf(stderr, "[s4579-M] n=%u tid=%lx sp=%08X ra=%08X cnt=%u inflight=%d alloc_tid=%lx alloc_sp=%08X same_tid=%d\n", rs64_s4579_nm, (unsigned long)(uintptr_t)pthread_self(), (uint32_t)ctx->r29, (uint32_t)ctx->r31, cnt, rs64_s4579_inflight, rs64_s4579_atid, rs64_s4579_asp, (int)(rs64_s4579_atid == (unsigned long)(uintptr_t)pthread_self()));
    fflush(stderr);
}
void rs64_s4579_mix_ext(uint8_t* rdram, recomp_context* ctx) { rs64_s4579_mix(rdram, ctx); }
'''
p = D / "funcs_23.c"; s = p.read_text()
if "rs64_s4579_alloc" not in s:
    sig = "RECOMP_FUNC void allocateSongChannelArray(uint8_t* rdram, recomp_context* ctx) {\n"
    assert s.count(sig) == 1
    s = s.replace(sig, HELP + sig)
    a = s.find('rs64_m5_selector_alloc_edge("pre0", 0x8008F0D0u')
    assert a > 0
    e1 = s.find("\n", a) + 1
    assert s[e1:].startswith("    rs_malloc(rdram, ctx);\n"), s[e1:e1 + 60]
    s = s[:e1] + "    rs64_s4579_alloc(rdram, ctx, 'A'); /* PATCH: s4579 */\n" + s[e1:]
    b = s.find('rs64_m5_selector_alloc_edge("post0", 0x8008F0D0u', a)
    assert b > 0
    e2 = s.find("\n", b) + 1
    s = s[:e2] + "    rs64_s4579_alloc(rdram, ctx, 'P'); /* PATCH: s4579 */\n" + s[e2:]
    p.write_text(s)
p = D / "funcs_24.c"; s = p.read_text()
if "rs64_s4579_mix" not in s:
    sig = "\nRECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
    assert s.count(sig) == 1
    s = s.replace(sig, "\nvoid rs64_s4579_mix_ext(uint8_t* rdram, recomp_context* ctx);" + sig + "    rs64_s4579_mix_ext(rdram, ctx); /* PATCH: s4579 */\n")
    p.write_text(s)
print("applied")
