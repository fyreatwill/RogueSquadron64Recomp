#!/usr/bin/env python3
"""s4984: make the voice-array publication and observation atomic.

ORIGIN: allocateSongChannelArray publishes a legitimate base at 0x801496F8
and count at 0x80149700; musyxMixActiveVoices consumes that pair on another
host thread.  The prior release/acquire fences did not make the guest-memory
accesses atomic, so this variant uses host atomic loads/stores at the exact
guest locations.  This is a synchronization experiment, not a value guard.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
p23 = root / "funcs_23.c"
p24 = root / "funcs_24.c"
s23 = p23.read_text()
s24 = p24.read_text()
marker = "PATCH: s4984 atomic voice pair"
if marker in s23 or marker in s24:
    print("s4984 already applied")
    raise SystemExit(0)

helper = r'''static inline uint32_t rs64_s4984_load_voice_count(uint8_t* rdram) {
    return (uint32_t)__atomic_load_n((uint16_t*)(rdram + 0x149702u), __ATOMIC_ACQUIRE);
}
static inline uint32_t rs64_s4984_load_voice_base(uint8_t* rdram) {
    return __atomic_load_n((uint32_t*)(rdram + 0x1496F8u), __ATOMIC_ACQUIRE);
}
/* PATCH: s4984 atomic voice pair */
'''
anchor24 = "RECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
if s24.count(anchor24) != 1:
    raise SystemExit(f"musyxMixActiveVoices anchor count={s24.count(anchor24)}")
s24 = s24.replace(anchor24, helper + anchor24, 1)

old_count = "{ uint32_t s4575_a = U32(ADD32(ctx->r4, -0X6900)); ctx->r4 = MEM_HU(ctx->r4, -0X6900); rs64_s4307_synth_read(rdram, 0x80090E1Cu, s4575_a, U32(ctx->r4)); } /* PATCH: s4307 synth read join */"
new_count = "{ uint32_t s4575_a = U32(ADD32(ctx->r4, -0X6900)); ctx->r4 = rs64_s4984_load_voice_count(rdram); rs64_s4307_synth_read(rdram, 0x80090E1Cu, s4575_a, U32(ctx->r4)); } /* PATCH: s4984 atomic count load */"
if s24.count(old_count) != 1:
    raise SystemExit(f"count reader anchor count={s24.count(old_count)}")
s24 = s24.replace(old_count, new_count, 1)

old_base = "{ uint32_t s4575_a = U32(ADD32(ctx->r4, -0X6908)); ctx->r4 = MEM_W(ctx->r4, -0X6908); rs64_s4307_synth_read(rdram, 0x80090E78u, s4575_a, U32(ctx->r4)); } /* PATCH: s4307 synth read join */"
new_base = "{ uint32_t s4575_a = U32(ADD32(ctx->r4, -0X6908)); ctx->r4 = rs64_s4984_load_voice_base(rdram); rs64_s4307_synth_read(rdram, 0x80090E78u, s4575_a, U32(ctx->r4)); } /* PATCH: s4984 atomic base load */"
if s24.count(old_base) != 1:
    raise SystemExit(f"base reader anchor count={s24.count(old_base)}")
s24 = s24.replace(old_base, new_base, 1)

old_base_store = "    MEM_W(-0X6908, ctx->r1) = ctx->r2;\n"
new_base_store = "    __atomic_store_n((uint32_t*)(rdram + 0x1496F8u), (uint32_t)ctx->r2, __ATOMIC_RELEASE); /* PATCH: s4984 atomic base store */\n"
if s23.count(old_base_store) != 1:
    raise SystemExit(f"base writer anchor count={s23.count(old_base_store)}")
s23 = s23.replace(old_base_store, new_base_store, 1)

old_count_store = "    MEM_H(-0X6900, ctx->r1) = ctx->r16;\n"
new_count_store = "    __atomic_store_n((uint16_t*)(rdram + 0x149702u), (uint16_t)ctx->r16, __ATOMIC_RELEASE); /* PATCH: s4984 atomic count store */\n"
if s23.count(old_count_store) != 1:
    raise SystemExit(f"count writer anchor count={s23.count(old_count_store)}")
s23 = s23.replace(old_count_store, new_count_store, 1)

p23.write_text(s23)
p24.write_text(s24)
print("s4984 atomic voice pair applied")
