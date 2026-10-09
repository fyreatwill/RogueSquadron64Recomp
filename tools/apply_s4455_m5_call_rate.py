"""M5 s4455: per-second call-rate counter for musyxMixActiveVoices / musyxBuildVoiceCommandList.

Diagnostic only (ROGUESQ_LOG_M5_RATE=1 or ROGUESQ_LOG_ALL=1). Entry-counts each function,
prints one line per wall second: calls/s for mix, build, and phase ordinal. Retail
reference (s4454): mix ~114 calls/s (0x80091018 2285x/20s), cmdlist area 23,900x/20s.
Positive control: the counter lines themselves carry a wall-clock second index and
the s4205 render-jal count is untouched (compare with ROGUESQ_LOG_M5_CMDLIST).
"""
from pathlib import Path

MARK = "PATCH: s4455 call rate"
SIG_MIX = "RECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
SIG_BLD = "RECOMP_FUNC void musyxBuildVoiceCommandList(uint8_t* rdram, recomp_context* ctx) {\n"

HELPER = r'''
/* PATCH: s4455 call rate (ROGUESQ_LOG_M5_RATE) */
#include <time.h>
static void rs64_s4455_tick(int which) {
    static int enabled = -1;
    static unsigned long cnt[2];
    static long sec0 = -1, cur = -1;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_RATE");
        const char* a = getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') || (a && a[0] && a[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    if (sec0 < 0) { sec0 = ts.tv_sec; cur = ts.tv_sec; }
    if (ts.tv_sec != cur) {
        fprintf(stderr, "[m5-rate] t=%lds phase=%u width=%u mix=%lu build=%lu\n",
                cur - sec0, rs64_phase_ord(), rs64_vi_committed_width(), cnt[0], cnt[1]);
        fflush(stderr);
        cnt[0] = cnt[1] = 0; cur = ts.tv_sec;
    }
    ++cnt[which];
}
'''

def apply_s4455_text(text: str):
    if MARK in text:
        return text, False
    for s in (SIG_MIX, SIG_BLD):
        if text.count(s) != 1:
            raise RuntimeError(f"s4455 signature count={text.count(s)} for {s[:40]}")
    text = text.replace(SIG_MIX, HELPER + SIG_MIX + "    rs64_s4455_tick(0);\n", 1)
    text = text.replace(SIG_BLD, SIG_BLD + "    rs64_s4455_tick(1);\n", 1)
    return text, True

if __name__ == "__main__":
    p = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_24.c"
    t, changed = apply_s4455_text(p.read_text())
    if changed:
        p.write_text(t)
    print("s4455 call rate", "patched" if changed else "already present", p.name)
