"""s6721 G1d: pause menu text split at wide aspect. The s6156 HUD anchor (apply_s6155_hudcpos) shifts every emitter
element on vp 0x80138D20, and the pause menu text (MISSION GOALS / objective / PAUSED / CONTINUE...) is drawn there too:
items left of retail centre stayed left, items right of it were pushed right by fbw-512. Gate: initHudStruct tests the
HUD struct's pause-menu byte (+0x258, 0x800C1998) every frame before calling runPauseMenuStateMachine; stamp it, and skip
the anchor while it is set. ROGUESQ_G1D_PAUSE_ANCHOR=1 = old behaviour. Idempotent."""
import pathlib
T33 = "PATCH: s6721 pausemark"
ANC33 = "    // 0x800C1998: lbu         $v0, 0x258($s2)\n    ctx->r2 = MEM_BU(ctx->r18, 0X258);\n"
ADD33 = "    { extern void rs64_g1d_pause_mark(int); rs64_g1d_pause_mark((int)ctx->r2); } /* PATCH: s6721 pausemark */\n"
T4 = "PATCH: s6721 pausegate"
ANC4 = "        if (an && !((uint32_t)ctx->r17 == 0x80138d20u"
NEW4 = "        extern int rs64_g1d_pause_live(void); /* PATCH: s6721 pausegate */\n        if (an && !rs64_g1d_pause_live() && !((uint32_t)ctx->r17 == 0x80138d20u"
def apply33(text):
    if T33 in text or text.count(ANC33) != 1: return text, 0
    return text.replace(ANC33, ANC33 + ADD33), 1
def apply4(text):
    if T4 in text or text.count(ANC4) != 1: return text, 0
    return text.replace(ANC4, NEW4), 1
if __name__ == "__main__":
    for name, fn in (("funcs_33.c", apply33), ("funcs_4.c", apply4)):
        p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs") / name; t = p.read_text(); t2, n = fn(t)
        if n: p.write_text(t2)
        print("%s live patched x%d" % (name, n))
