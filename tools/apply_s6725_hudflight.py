"""s6725 G1d: 21:9 level-select name clipped at the left edge. Writer = our s6156 HUD anchor (apply_s6155_hudcpos): the
level select draws SELECT LEVEL, the preview and the level name on vp 0x800CDC80, one of the anchored flight-HUD lists,
so every rect moved -A (256 px at w1024; anchor-off arm: rects 64..419 -> 320..675, centred like 4:3). Gate: the anchor
applies only while rs64_g1d_hud_flight() (renderRadarMinimap stamped within 8 swaps). ROGUESQ_G1D_HUD_ANYWHERE=1 = old.
Runs after apply_s6721_pausegate.apply4. Idempotent."""
import pathlib
T = "PATCH: s6725 hudflight"
ANC = "        if (an && !rs64_g1d_pause_live() && "
NEW = "        extern int rs64_g1d_hud_flight(void); /* PATCH: s6725 hudflight */\n        if (an && !rs64_g1d_pause_live() && rs64_g1d_hud_flight() && "
def apply(text):
    if T in text or text.count(ANC) != 1: return text, 0
    return text.replace(ANC, NEW), 1
if __name__ == "__main__":
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c"); t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_4.c live patched x%d" % n)
