#!/usr/bin/env python3
"""Add the phase-gated s4595 caller/input census to funcs_24.c."""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4595_caller" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4595 phase-gated caller/input census. Diagnostic only. */
static void rs64_s4595_caller(uint8_t* rdram, const char* site, uint32_t voice,
                              uint32_t raw34, uint32_t a1, uint32_t a2,
                              uint32_t a3) {
    static int on = -1;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static unsigned bad_rows = 0, ctl_rows = 0;
    if (on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4595");
        on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!on) return;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    if (width != 640u || origin != 0x006A2900u) return;
    if (phase_seen != phase) { phase_seen = phase; bad_rows = 0; ctl_rows = 0; }
    const uint32_t vals[4] = { raw34, a1, a2, a3 };
    int first = -1;
    for (int i = 0; i < 4; ++i) {
        const uint32_t top = vals[i] >> 24;
        if ((vals[i] >= 0x20000000u && vals[i] < 0x7F000000u) ||
            (vals[i] & 1u)) { first = i; break; }
    }
    if (first >= 0) {
        if (bad_rows++ >= 16) return;
    } else if (ctl_rows++ >= 4) return;
    fprintf(stderr,
        "[s4595-caller] kind=%s site=%s phase=%u width=%u origin=0x%06X voice=%08X raw34=%08X a1=%08X a2=%08X a3=%08X first=%d\n",
        first >= 0 ? "bad" : "control", site, phase, width, origin,
        voice, raw34, a1, a2, a3, first);
    fflush(stderr);
}

'''

anchor = "RECOMP_FUNC void musyxRenderVoiceSamples(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"function anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

# FE98 is in fillSampleStreamRange, which precedes musyxRenderVoiceSamples;
# declare the helper before that earlier call site.
decl_anchor = "RECOMP_FUNC void fillSampleStreamRange(uint8_t* rdram, recomp_context* ctx) {\n"
decl = "static void rs64_s4595_caller(uint8_t* rdram, const char* site, uint32_t voice, uint32_t raw34, uint32_t a1, uint32_t a2, uint32_t a3);\n\n"
if s.count(decl_anchor) != 1:
    raise SystemExit(f"fill function anchor count {s.count(decl_anchor)}")
s = s.replace(decl_anchor, decl + decl_anchor, 1)

sites = {
    "0x8009024Cu": "8009024C",
    "0x800902CCu": "800902CC",
    "0x8009039Cu": "8009039C",
    "0x800903F0u": "800903F0",
}
for needle, site in sites.items():
    anchor = f"    rs64_s4534_jal(rdram, \"{site}\", "
    call = f"    rs64_s4595_caller(rdram, \"{site}\", U32(ctx->r17), (uint32_t)MEM_W(0x34, ctx->r17), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); /* PATCH: s4595 */\n"
    if s.count(anchor) != 1:
        raise SystemExit(f"site anchor count {site}: {s.count(anchor)}")
    s = s.replace(anchor, call + anchor, 1)

anchor = "    rs64_s4594_operand(rdram, U32(ctx->r8), s4594_a1, s4594_a2, s4594_a3, U32(ctx->r2)); /* PATCH: s4594 */\n"
call = "    rs64_s4595_caller(rdram, \"FE98\", U32(ctx->r4), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); /* PATCH: s4595 */\n"
if s.count(anchor) != 1:
    raise SystemExit(f"FE98 anchor count {s.count(anchor)}")
s = s.replace(anchor, anchor + call, 1)
p.write_text(s)
print("applied")
