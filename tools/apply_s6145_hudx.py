"""s6145 G1d: HUD x-shift lever. linkHudNodeAndComputeScreenPos (0x80055B90, funcs_12.c) stores the HUD node's
screen x (float) at node+0x18 (store at 0x80055C14). ROGUESQ_HUD_DX=<px> (default 0 = retail) adds px to it.
First positive-control lever for HUD edge anchoring; other HUD writers (radar etc.) still to be located. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    { MEM_W(0X18, ctx->r6) = ctx->f0.u32l; RS64_S5798_ST(0x80055C14u, 0X18, ctx->r6, 4); }\n"
NEW = r'''    { /* PATCH: s6145 hudx */ static double dx6145 = -1e9; if (dx6145 < -1e8) { const char* e = getenv("ROGUESQ_HUD_DX"); dx6145 = (e && *e) ? atof(e) : 0.0; if (dx6145 != 0.0) fprintf(stderr, "[g1d] HUD node x +%g\n", dx6145); }
      if (dx6145 != 0.0) ctx->f0.fl = (float)(ctx->f0.fl + dx6145); }
'''
def apply(text):
    if "PATCH: s6145 hudx" in text or text.count(OLD) != 1: return text, 0
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    p = base / "funcs_12.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_12.c live patched x%d" % n)
