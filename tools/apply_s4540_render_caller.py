#!/usr/bin/env python3
"""s4540: the s4539 entry probe's ra is not a caller. Direct jal does not
write ctx->r31, and the first run printed ra=0 on arm, in-range, and the
bad voice. This probe sits on the only static call, musyxMixActiveVoices
jal 0x80090F00, and reads a0 (ctx->r4) after the delay slot.

In-range is base 0x801714D0, stride 0x88, index 0..17. Prints one arm
line, up to 18 distinct in-range indices, and up to 4 calls whose a0 is
0x801724C0. ROGUESQ_LOG_S4539=1, same gate as the entry probe.
Diagnostic only. Does not skip the call. Idempotent.
"""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4540_call" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4540 mix-call caller. Diagnostic only. Does not skip the call.
   a0 is ctx->r4 at jal 0x80090F00. In-range is base 0x801714D0, stride
   0x88, index 0..17. */
static int rs64_s4540_seen_idx[18];
static unsigned rs64_s4540_n_all = 0;
static unsigned rs64_s4540_n_in = 0;
static int rs64_s4540_arm = 0;
static int rs64_s4540_bad_rows = 0;
static int rs64_s4540_on = -1;

static int rs64_s4540_enabled(void) {
    if (rs64_s4540_on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4539");
        rs64_s4540_on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    return rs64_s4540_on;
}

static void rs64_s4540_call(gpr a0g) {
    uint32_t a0;
    uint32_t diff;
    uint32_t q;
    int in_range;
    int index;
    const uint32_t base = 0x801714D0u;
    const uint32_t stride = 0x88u;
    if (!rs64_s4540_enabled()) return;
    a0 = (uint32_t)a0g;
    rs64_s4540_n_all++;
    if (!rs64_s4540_arm) {
        rs64_s4540_arm = 1;
        fprintf(stderr, "[s4540-call] kind=arm a0=0x%08X n_all=%u\n", a0, rs64_s4540_n_all);
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
            "[s4540-call] kind=in a0=0x%08X index=%d n_all=%u n_in=%u\n",
            a0, index, rs64_s4540_n_all, rs64_s4540_n_in);
        fflush(stderr);
    }
    if (a0 == 0x801724C0u && rs64_s4540_bad_rows < 4) {
        rs64_s4540_bad_rows++;
        fprintf(stderr,
            "[s4540-call] kind=bad a0=0x%08X n_all=%u n_in=%u\n",
            a0, rs64_s4540_n_all, rs64_s4540_n_in);
        fflush(stderr);
    }
}

'''

anchor = "RECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"musyxMixActiveVoices anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

call = "    { uint32_t s4205_rec = (uint32_t)ctx->r7; /* PATCH: s4205 cmdlist census */\n    musyxRenderVoiceSamples(rdram, ctx);\n"
n = s.count(call)
if n != 1:
    raise SystemExit(f"call anchor count {n}")
s = s.replace(
    call,
    "    { uint32_t s4205_rec = (uint32_t)ctx->r7; /* PATCH: s4205 cmdlist census */\n"
    "    rs64_s4540_call(ctx->r4); /* PATCH: s4540 */\n"
    "    musyxRenderVoiceSamples(rdram, ctx);\n",
    1,
)

if s.count("rs64_s4540_call(") != 2:
    raise SystemExit("call count is not declaration+call")
p.write_text(s)
print("applied")
