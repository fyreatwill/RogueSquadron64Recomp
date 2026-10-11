#!/usr/bin/env python3
"""s4571c: H-stale-heap A/B. s4571b showed the per-buffer render-record tables (0x80149708/0C, cap=(count+1)*3 records of 0x88 bytes,
allocated by allocateSongChannelArray via rs_malloc(size,0), never cleared) read as ZERO for idx<count but as non-zero stale heap data
for chunk-2+ records (idx>=count; e.g. pre=54005622 03003966 ...). Retail's allocator is not known to zero either, so this is a test,
not a fix: ROGUESQ_S4571_ZERO=1 zeroes both tables right after the third rs_malloc in allocateSongChannelArray. Run concurrent arms with
and without it; compare odd-PI-DMA aborts / [s4534-jal kind=bad]. Idempotent. Diagnostic: env-gated, default OFF."""
from pathlib import Path
p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
s = p.read_text()
if "s4571c" in s:
    print("already applied"); raise SystemExit(0)
a = "    MEM_W(-0X68F4, ctx->r1) = ctx->r2;\n"
assert s.count(a) == 1
hook = r'''    { /* PATCH: s4571c zero render-record tables (env ROGUESQ_S4571_ZERO) */
        static int s4571c_on = -1;
        if (s4571c_on < 0) { const char* e = getenv("ROGUESQ_S4571_ZERO"); s4571c_on = (e && e[0] && e[0] != '0') ? 1 : 0; }
        uint32_t t0 = (uint32_t)MEM_W(-0X68F8, S32(0x8015 << 16)), t1 = (uint32_t)ctx->r2, cap = (uint32_t)MEM_HU(-0X68FC, S32(0x8015 << 16));
        if (s4571c_on && t0 && t1 && cap && cap < 4096) {
            for (uint32_t i = 0; i < cap * 0x88u; i += 4) { MEM_W(i, (int32_t)t0) = 0; MEM_W(i, (int32_t)t1) = 0; }
            fprintf(stderr, "[s4571c-zero] tbl0=0x%08X tbl1=0x%08X cap=%u bytes=%u each\n", t0, t1, cap, cap * 0x88u); fflush(stderr);
        }
    }
'''
s = s.replace(a, a + hook)
p.write_text(s); print("applied")
