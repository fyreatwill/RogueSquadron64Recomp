"""M5 Step 9c: command-list record census around musyxRenderVoiceSamples in musyxMixActiveVoices.

Diagnostic only (ROGUESQ_LOG_M5_CMDLIST=1 or ROGUESQ_LOG_ALL=1). At the render jal
(0x80090F00, a3 = 0x88-byte command-list record) it captures the record pointer,
calls render, then tallies/dumps the record. Positive control: the voice slot
(s1, 0x88 bytes) must hash nonzero (ctl_nz). Per-phase: visits, records with any
nonzero byte, and records with a nonzero halfword in +0x40..+0x60 (volume region);
first 3 records per phase dumped as 34 words.
"""
from pathlib import Path

CALL_OLD = ("    // 0x80090F00: jal         0x8008FFAC\n"
            "    // 0x80090F04: addu        $a3, $t0, $a3\n"
            "    ctx->r7 = ADD32(ctx->r8, ctx->r7);\n"
            "    musyxRenderVoiceSamples(rdram, ctx);\n")
CALL_NEW = ("    // 0x80090F00: jal         0x8008FFAC\n"
            "    // 0x80090F04: addu        $a3, $t0, $a3\n"
            "    ctx->r7 = ADD32(ctx->r8, ctx->r7);\n"
            "    { uint32_t s4205_rec = (uint32_t)ctx->r7; /* PATCH: s4205 cmdlist census */\n"
            "    musyxRenderVoiceSamples(rdram, ctx);\n"
            "    rs64_s4205_rec(rdram, s4205_rec, (gpr)ctx->r17); }\n")
SIG = "RECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
MARK = "PATCH: s4205 cmdlist census"

HELPER = r'''
/* PATCH: s4205 cmdlist census (ROGUESQ_LOG_M5_CMDLIST) */
static void rs64_s4205_rec(uint8_t* rdram, uint32_t rec, gpr s1) {
    static int enabled = -1;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static unsigned long n, rec_nz, rec_zero, rec_bad, vol_nz, ctl_nz;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_CMDLIST");
        const char* a = getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') || (a && a[0] && a[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    uint32_t phase = rs64_phase_ord();
    if (phase != phase_key) { phase_key = phase; n = rec_nz = rec_zero = rec_bad = vol_nz = ctl_nz = 0; }
    ++n;
    unsigned i, cnz = 0, rnz = 0, vnz = 0;
    for (i = 0; i < 0x88; ++i) if (MEM_BU(i, s1)) ++cnz;
    if (cnz) ++ctl_nz;
    if (rec < 0x80000000u || rec >= 0x807FFF78u) { ++rec_bad; }
    else {
        gpr r = (gpr)(int32_t)rec;
        for (i = 0; i < 0x88; ++i) if (MEM_BU(i, r)) ++rnz;
        for (i = 0x40; i < 0x60; i += 2) if (MEM_HU(i, r)) ++vnz;
        if (rnz) ++rec_nz; else ++rec_zero;
        if (vnz) ++vol_nz;
    }
    if (n <= 3 || (n % 512ul) == 0) {
        fprintf(stderr, "[m5-cmdlist] phase=%u width=%u n=%lu rec_nz=%lu rec_zero=%lu rec_bad=%lu vol_nz=%lu ctl_nz=%lu rec=0x%08X rnz=%u vnz=%u s1nz=%u w:",
                phase, rs64_vi_committed_width(), n, rec_nz, rec_zero, rec_bad, vol_nz, ctl_nz, rec, rnz, vnz, cnz);
        if (rec >= 0x80000000u && rec < 0x807FFF78u && n <= 3)
            for (i = 0; i < 0x88; i += 4) fprintf(stderr, " %08X", (unsigned)MEM_W(i, (gpr)(int32_t)rec));
        fputc('\n', stderr);
        fflush(stderr);
    }
}
'''


def apply_s4205_text(text: str):
    if MARK in text:
        return text, False
    if text.count(CALL_OLD) != 1:
        raise RuntimeError(f"s4205 render-jal site count={text.count(CALL_OLD)}")
    if text.count(SIG) != 1:
        raise RuntimeError(f"s4205 musyxMixActiveVoices signature count={text.count(SIG)}")
    text = text.replace(CALL_OLD, CALL_NEW, 1)
    text = text.replace(SIG, HELPER + SIG, 1)
    return text, True


if __name__ == "__main__":
    p = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_24.c"
    t, changed = apply_s4205_text(p.read_text())
    if changed:
        p.write_text(t)
    print("s4205 cmdlist", "patched" if changed else "already present", p.name)
