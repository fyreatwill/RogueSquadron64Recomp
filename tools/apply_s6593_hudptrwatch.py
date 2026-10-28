"""s6593: attribute stores around the high HUD pointer seen in the lvl7 dd4 fault.

The watch is diagnostic only and is disabled unless ROGUESQ_HUDPTRWATCH is set.
The existing low-RAM HUD word is retained as a positive control in the same
handler.  `prev` is the last observed value for that word; generated store
hooks run after the store, so the true pre-store value is unavailable here.
"""
from pathlib import Path
import re

MARK = "PATCH: s6593 hudptrwatch"
HANDLER_MARK = "PATCH: s6593 hudptrwatch handler"
ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
HIGH = " || (uint32_t)(_a5798 - 0x951335A0u) < 0x20u"

def apply_file(path: Path) -> int:
    text = path.read_text()
    if MARK in text or "RS64_S5798_ST" not in text:
        return 0
    old = ") rs64_s5798_st(rdram, ctx, (pc), _a5798, (w), __func__); } while (0)"
    if old not in text:
        return 0
    text = text.replace(old, HIGH + old, 1)
    path.write_text(text + "\n/* " + MARK + " */\n")
    return 1

def apply_handler(path: Path) -> int:
    text = path.read_text()
    if HANDLER_MARK in text:
        return 0
    anchor = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
    if anchor not in text:
        return 0
    helper = r'''/* PATCH: s6593 hudptrwatch handler */
extern uint32_t rs64_phase_ord(void);
extern uint32_t rs64_vi_committed_origin(void);
static void s6593_hudptr_note(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {
    static int en = -1; static uint32_t last_hi = 0, last_ctl = 0; static unsigned n = 0;
    if (en < 0) { const char* e = getenv("ROGUESQ_HUDPTRWATCH"); en = (e && e[0] && e[0] != '0') ? 1 : 0; }
    if (!en || n >= 400) return;
    const uint32_t p = a & 0x1FFFFFFFu;
    const int high = p >= 0x1135A0u && p < 0x1135C0u;
    const int control_hud = p >= 0x10CA30u && p < 0x10CA34u;
    const int control_player = p >= 0x137DB0u && p < 0x137ED0u;
    const int control = control_hud || control_player;
    if (!high && !control) return;
    uint32_t now = (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u));
    uint32_t* last = high ? &last_hi : &last_ctl;
    uint32_t prev = *last; *last = now;
    fprintf(stderr, "[hudptrw] n=%u kind=%s pc=%08X ra=%08X fn=%s addr=%08X phys=%06X w=%d prev=%08X new=%08X phase=%u vi_origin=%06X\n",
        ++n, high ? "target" : control_player ? "control_player" : "control_hud", pc, (uint32_t)ctx->r31, fn ? fn : "?", a, p, w, prev, now,
        rs64_phase_ord(), rs64_vi_committed_origin() & 0x00FFFFFFu);
    fflush(stderr);
    (void)rdram;
}
'''
    text = text.replace(anchor, helper + anchor + "    if (((uint32_t)(a - 0x951335A0u) < 0x20u) || ((uint32_t)(a - 0x8010CA30u) < 4u) || ((uint32_t)(a - 0x80137DB0u) < 0x120u)) { s6593_hudptr_note(rdram, ctx, pc, a, w, fn); return; } /* " + HANDLER_MARK + " */\n", 1)
    path.write_text(text)
    return 1

total = 0
for p in sorted(ROOT.glob("funcs_*.c")):
    total += apply_file(p)
handler = ROOT / "funcs_13.c"
if handler.exists():
    total += apply_handler(handler)
print("s6593 patched", total, "files")
