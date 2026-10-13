"""s4782: log ra / a0 / guard byte / stack-scan return candidates on entry to
shutdownMusyXEngine (0x8008ECA4), shutdownAudioEngine (0x80091D40) and, as the
same-run positive control, shutdownMusyXVoices (0x8009BCC4).

Gate: ROGUESQ_LOG_S4782=1. Rows are [s4782-shut], capped at 40 per function.
ORIGIN: read-only logging, no state forced or cleared. Live-tree patch like
s4694 (full regen is broken, REGEN WARNING s4204).
"""
from pathlib import Path

base = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"

CALL = (
    "    { /* PATCH: s4782 shutdown caller */ extern void rs64_s4782_shut(uint8_t*, const char*, recomp_context*);\n"
    "      rs64_s4782_shut(rdram, \"%s\", ctx); }\n"
)
HELPER = r'''
/* PATCH: s4782 shutdown caller helper */
void rs64_s4782_shut(uint8_t* rdram, const char* fn, recomp_context* ctx) {
    static int enabled = -1;
    static unsigned long rows[3];
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4782"); enabled = (e && e[0] && e[0] != '0'); }
    if (!enabled) return;
    unsigned idx = (fn[13] == 'E') ? 0 : (fn[8] == 'A' ? 1 : 2);
    if (rows[idx]++ >= 40ul) return;
    fprintf(stderr, "[s4782-shut] fn=%s n=%lu phase=%u vi=%u/0x%06X ra=0x%08X a0=0x%08X sp=0x%08X guard800A0F50=%02X\n",
            fn, rows[idx], rs64_phase_ord(), rs64_vi_committed_width(), rs64_vi_committed_origin(),
            (unsigned)ctx->r31, (unsigned)ctx->r4, (unsigned)ctx->r29, (unsigned)MEM_BU(0, S32(0x800A0F50u)));
    fprintf(stderr, "[s4782-stack] fn=%s cand:", fn);
    int shown = 0;
    for (int i = 0; i < 128 && shown < 14; ++i) {
        uint32_t w = (uint32_t)MEM_W(i * 4, ctx->r29);
        if (w >= 0x80000000u && w < 0x800F0000u && (w & 3u) == 0u) { fprintf(stderr, " +%X=%08X", i * 4, w); ++shown; }
    }
    fprintf(stderr, "\n"); fflush(stderr);
}
'''

targets = [
    ("funcs_23.c", "    // 0x8008ECA4: lui         $v0, 0x800A\n", "shutdownMusyXEngine", True),
    ("funcs_24.c", "    // 0x80091D40: lui         $v0, 0x800A\n", "shutdownAudioEngine", False),
    ("funcs_26.c", "    // 0x8009BCC4: addiu       $sp, $sp, -0x18\n", "shutdownMusyXVoices", False),
]
for fname, anchor, fn, helper_here in targets:
    p = base / fname
    t = p.read_text()
    if "PATCH: s4782 shutdown caller" in t:
        print("already patched", fname)
        continue
    if t.count(anchor) != 1:
        raise SystemExit(f"anchor count {t.count(anchor)} in {fname}")
    t = t.replace(anchor, CALL % fn + anchor)
    if helper_here:
        inc = '#include "funcs.h"\n'
        assert t.count(inc) == 1
        t = t.replace(inc, inc + HELPER, 1)
    p.write_text(t)
    print("patched", p)
