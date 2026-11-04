"""s6860 G1d: lvl10 (Battle Above Taloraan) flight HUD stays in the centred 512 px at 21:9 while the disc moves to the right
edge. Writer = our s6161 reticle exemption (apply_s6155_hudcpos): vp 0x80138D20 elements below 0x80300000 skip the s6156
anchor, on the assumption that the HUD table is above it. The table is heap: 0x805623xx on lvl1, 0x8028FD3C..FE8C on lvl10
(ROGUESQ_HUD_LOG, same binary), so the whole lvl10 HUD read as "projected sprite". The reticle itself is static data at
0x8010CA58/88 on both levels. The bound is now rs64_s6860_hud_elem_top() = 0x80110000. ROGUESQ_G1D_HUD_ELEMTOP=1 = old.
Runs after apply_s6845_hudwipe. Idempotent."""
import pathlib
T = "PATCH: s6860 hudelem"
ANC = "(uint32_t)ctx->r19 < 0x80300000u"
NEW = "(uint32_t)ctx->r19 < rs64_s6860_hud_elem_top() /* PATCH: s6860 hudelem */"
DECL_ANC = "        extern int rs64_s6845_hud_small(uint32_t); /* PATCH: s6845 hudwipe */\n"
def apply(text):
    if T in text or text.count(ANC) != 1 or text.count(DECL_ANC) != 1: return text, 0
    # declared ahead of the s6155 anchor block, the first use of the bound
    i = text.index(ANC); j = text.rfind("{ static int an = -1;", 0, i)
    text = text[:j] + "extern uint32_t rs64_s6860_hud_elem_top(void); " + text[j:]
    return text.replace(ANC, NEW), 1
if __name__ == "__main__":
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c"); t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_4.c live patched x%d" % n)
