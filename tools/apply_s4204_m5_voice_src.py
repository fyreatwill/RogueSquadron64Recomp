"""M5 Step 9b: voice sample-source census at the musyxKeyOnVoice shared tail.

Diagnostic only (ROGUESQ_LOG_M5_VOICE_SRC=1 or ROGUESQ_LOG_ALL=1). At 0x80090DDC
(s0 = key-on param struct, s1 = voice record) it hashes the 64 bytes behind each
source pointer in s0+0x28/0x2C/0x30/0x34/0x40 and logs [m5-voice-src] rows with a
per-phase nz/zero/bad tally. Positive control: the 0x80-byte param struct itself
must hash nonzero (ctl_nz counts it).

Shared by the live-tree CLI below and fixup_game_funcs.py (one transform).
"""
from pathlib import Path

SITE = "    // 0x80090DDC: lhu         $v0, 0x0($s2)\n"
CALL = ("    rs64_s4204_voice_src(rdram, (gpr)ctx->r16, (gpr)ctx->r17); "
        "/* PATCH: s4204 voice source census */\n")
SIG = "RECOMP_FUNC void musyxKeyOnVoice(uint8_t* rdram, recomp_context* ctx) {\n"
MARK = "PATCH: s4204 voice source census"

HELPER = r'''
/* PATCH: s4204 voice sample-source census (ROGUESQ_LOG_M5_VOICE_SRC) */
static uint64_t rs64_s4204_fnv(uint8_t* rdram, gpr addr, unsigned n, unsigned* nz) {
    uint64_t h = 1469598103934665603ull;
    unsigned i;
    *nz = 0;
    for (i = 0; i < n; ++i) {
        uint8_t b = MEM_BU(i, addr);
        if (b) ++*nz;
        h = (h ^ b) * 1099511628211ull;
    }
    return h;
}
static int rs64_s4204_ok(uint32_t a) { return a >= 0x80000000u && a < 0x807FFFC0u; }
static void rs64_s4204_voice_src(uint8_t* rdram, gpr s0, gpr s1) {
    static int enabled = -1;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static unsigned long n, src_nz, src_zero, src_bad, ctl_nz;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_VOICE_SRC");
        const char* a = getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') || (a && a[0] && a[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    uint32_t phase = rs64_phase_ord();
    if (phase != phase_key) { phase_key = phase; n = src_nz = src_zero = src_bad = ctl_nz = 0; }
    ++n;
    uint32_t s0u = (uint32_t)s0;
    unsigned cnz = 0, k;
    uint64_t chash = rs64_s4204_fnv(rdram, s0, 0x80, &cnz); /* positive control: param struct itself */
    if (cnz) ++ctl_nz;
    static const unsigned offs[5] = {0x28, 0x2C, 0x30, 0x34, 0x40};
    uint32_t ptr[5]; unsigned nzs[5]; uint64_t hs[5]; int any_nz = 0, any_ok = 0;
    for (k = 0; k < 5; ++k) {
        ptr[k] = (uint32_t)MEM_W(offs[k], s0);
        nzs[k] = 0; hs[k] = 0;
        if (rs64_s4204_ok(ptr[k])) {
            any_ok = 1;
            hs[k] = rs64_s4204_fnv(rdram, (gpr)(int32_t)ptr[k], 64, &nzs[k]);
            if (nzs[k]) any_nz = 1;
        }
    }
    if (!any_ok) ++src_bad; else if (any_nz) ++src_nz; else ++src_zero;
    if (n <= 12 || (n % 256ul) == 0) {
        fprintf(stderr,
            "[m5-voice-src] phase=%u width=%u n=%lu src_nz=%lu src_zero=%lu src_bad=%lu ctl_nz=%lu type=%u s0=0x%08X ctl_hash=%016llx ctl_nz64=%u "
            "p28=0x%08X nz=%u h=%016llx p2c=0x%08X nz=%u h=%016llx p30=0x%08X nz=%u h=%016llx p34=0x%08X nz=%u h=%016llx p40=0x%08X nz=%u h=%016llx "
            "len44=%u w48=%u vol60=0x%04X s1_20=0x%04X s1_22=0x%04X s1_4c=0x%04X\n",
            phase, rs64_vi_committed_width(), n, src_nz, src_zero, src_bad, ctl_nz,
            (unsigned)MEM_BU(0x21, s0), s0u, (unsigned long long)chash, cnz,
            ptr[0], nzs[0], (unsigned long long)hs[0], ptr[1], nzs[1], (unsigned long long)hs[1],
            ptr[2], nzs[2], (unsigned long long)hs[2], ptr[3], nzs[3], (unsigned long long)hs[3],
            ptr[4], nzs[4], (unsigned long long)hs[4],
            (unsigned)MEM_HU(0x44, s0), (unsigned)MEM_HU(0x48, s0), (unsigned)MEM_HU(0x60, s0),
            (unsigned)MEM_HU(0x20, s1), (unsigned)MEM_HU(0x22, s1), (unsigned)MEM_HU(0x4C, s1));
        fflush(stderr);
    }
}
'''


def apply_s4204_text(text: str):
    """Return (text, changed). Raises on anchor mismatch."""
    if MARK in text:
        return text, False
    if text.count(SITE) != 1:
        raise RuntimeError(f"s4204 key-on tail site count={text.count(SITE)}")
    if text.count(SIG) != 1:
        raise RuntimeError(f"s4204 musyxKeyOnVoice signature count={text.count(SIG)}")
    text = text.replace(SITE, CALL + SITE, 1)
    text = text.replace(SIG, HELPER + SIG, 1)
    return text, True


if __name__ == "__main__":
    p = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_24.c"
    t, changed = apply_s4204_text(p.read_text())
    if changed:
        p.write_text(t)
    print("s4204 voice-src", "patched" if changed else "already present", p.name)
