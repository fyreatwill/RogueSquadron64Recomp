#!/usr/bin/env python3
"""s4539/s4540: at musyxRenderVoiceSamples' 0x8008FFB4 addu, record entry a0
and ra. In-range means (a0 - 0x801714D0) is divisible by 0x88 and the
quotient is in 0..17. One arm line, up to 32 distinct in-range ras, and
up to 4 entries of voice 0x801724C0. ROGUESQ_LOG_S4539=1. Diagnostic
only. Does not skip the call. Idempotent.
"""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4539_entry" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4539 render entry caller. Diagnostic only. Does not skip the call.
   a0 is ctx->r4 and ra is ctx->r31 at the 0x8008FFB4 addu. In-range is
   base 0x801714D0, stride 0x88, index 0..17. A 33rd distinct in-range ra
   sets overflow and is not stored. */
static uint32_t rs64_s4539_ras[32];
static unsigned rs64_s4539_n_in = 0;
static int rs64_s4539_overflow = 0;
static int rs64_s4539_arm = 0;
static int rs64_s4539_bad_rows = 0;
static int rs64_s4539_on = -1;

static int rs64_s4539_enabled(void) {
    if (rs64_s4539_on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4539");
        rs64_s4539_on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    return rs64_s4539_on;
}

static int rs64_s4539_has_ra(uint32_t ra) {
    unsigned i;
    for (i = 0; i < rs64_s4539_n_in; i++) {
        if (rs64_s4539_ras[i] == ra) return 1;
    }
    return 0;
}

static void rs64_s4539_entry(gpr a0g, gpr rag) {
    uint32_t a0;
    uint32_t ra;
    uint32_t diff;
    uint32_t q;
    int in_range;
    int index;
    const uint32_t base = 0x801714D0u;
    const uint32_t stride = 0x88u;
    if (!rs64_s4539_enabled()) return;
    a0 = (uint32_t)a0g;
    ra = (uint32_t)rag;
    if (!rs64_s4539_arm) {
        rs64_s4539_arm = 1;
        fprintf(stderr, "[s4539-entry] kind=arm a0=0x%08X ra=0x%08X\n", a0, ra);
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
    if (in_range && !rs64_s4539_has_ra(ra)) {
        if (rs64_s4539_n_in < 32u) {
            rs64_s4539_ras[rs64_s4539_n_in] = ra;
            rs64_s4539_n_in++;
            fprintf(stderr,
                "[s4539-entry] kind=in a0=0x%08X ra=0x%08X index=%d n_in=%u\n",
                a0, ra, index, rs64_s4539_n_in);
            fflush(stderr);
        } else {
            rs64_s4539_overflow = 1;
        }
    }
    if (a0 == 0x801724C0u && rs64_s4539_bad_rows < 4) {
        rs64_s4539_bad_rows++;
        fprintf(stderr,
            "[s4539-entry] kind=bad a0=0x%08X ra=0x%08X in_match=%d n_in=%u overflow=%d\n",
            a0, ra, rs64_s4539_has_ra(ra), rs64_s4539_n_in, rs64_s4539_overflow);
        fflush(stderr);
    }
}

'''

anchor = "RECOMP_FUNC void musyxRenderVoiceSamples(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"musyxRenderVoiceSamples anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

addu = "    // 0x8008FFB4: addu        $s1, $a0, $zero\n    ctx->r17 = ADD32(ctx->r4, 0);\n"
n = s.count(addu)
if n != 1:
    raise SystemExit(f"addu anchor count {n}")
s = s.replace(
    addu,
    addu + "    rs64_s4539_entry(ctx->r4, ctx->r31); /* PATCH: s4539 */\n",
    1,
)

if s.count("rs64_s4539_entry(") != 2:
    raise SystemExit("entry count is not declaration+call")
p.write_text(s)
print("applied")
