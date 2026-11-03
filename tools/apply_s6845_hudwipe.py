"""s6845 G1d: 21:9 abort-level wipe ends bright for ~0.4 s (4:3/retail hold black). Writer = our s6156 HUD anchor
(apply_s6155_hudcpos): the wipe is glyph 0x180 of text object 0x80334E0C on vp 0x80138D20 with x scale 73.14 (21:9) /
36.57 (4:3), a full-screen sprite. Once the pause byte drops (~VI 6740) the anchor gate opens while the wipe is still
sweeping, so base x = w - A*sc moved the sprite -256 px (A=256 at w1024): x0 273 -> -750, -4 -> -1019; drawTextGlyphRect
then clips x0<0 to ul 0 with S = (-x0)>>1 and lr = x0 + 4681 (3931 / 3662), i.e. the observed RDP rects ul 0 lr 982.75
S 375 and ul 0 lr 914.5/915.5 S 511/509, whose S runs past the soft-edge texture (transparent). Gate: the anchor never
applies to an element whose x scale (obj+0x24) exceeds 8 (HUD items: 1.0-3.2). ROGUESQ_G1D_HUD_BIGSCALE=1 = old.
Runs after apply_s6725_hudflight. Idempotent."""
import pathlib
T = "PATCH: s6845 hudwipe"
ANC = "        if (an && !rs64_g1d_pause_live() && rs64_g1d_hud_flight() && "
NEW = ("        extern int rs64_s6845_hud_small(uint32_t); /* PATCH: s6845 hudwipe */\n"
       "        if (an && !rs64_g1d_pause_live() && rs64_g1d_hud_flight() && rs64_s6845_hud_small((uint32_t)MEM_W(ctx->r19, 0X24)) && ")
def apply(text):
    if T in text or text.count(ANC) != 1: return text, 0
    return text.replace(ANC, NEW), 1
if __name__ == "__main__":
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c"); t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_4.c live patched x%d" % n)
