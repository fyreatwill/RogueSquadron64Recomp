"""s6155 G1d: HUD sprite emitter 0x800159B4 (funcs_4.c). x=(elem+0x18 + vp+0x18)*[0x800006F8] ends at 0x800160C0
(mul.s f4). ROGUESQ_HUD_LOG=1 logs each distinct elem (s3) once: x, y, vp (s1). ROGUESQ_HUD_CPOS=<px> adds +px*scale to
x when x < 160*scale and -px*scale otherwise (edge anchoring lever; default 0 = retail). Idempotent."""
import pathlib
T = "PATCH: s6155 hudcpos"
ANC = "    ctx->f4.fl = MUL_S(ctx->f4.fl, ctx->f6.fl);\n    // 0x800160C4: lwc1        $f0, 0x1C($s1)\n"
ADD = r'''    { /* PATCH: s6155 hudcpos */ static int en = -1; static double cp = 0; static int lg = 0;
      if (en < 0) { const char* a = getenv("ROGUESQ_HUD_CPOS"); const char* l = getenv("ROGUESQ_HUD_LOG"); cp = (a && *a) ? atof(a) : 0.0; lg = (l && *l) ? 1 : 0; en = 1; if (cp != 0.0 || lg) fprintf(stderr, "[hudc] cpos=%g log=%d\n", cp, lg); }
      if (lg) { static uint32_t seen[512]; static int ns = 0; uint32_t ea = (uint32_t)ctx->r19; int i; for (i = 0; i < ns; i++) if (seen[i] == ea) break;
        if (i == ns && ns < 512) { seen[ns++] = ea; float yy; uint32_t yv = (uint32_t)MEM_W(ctx->r19, 0X1C); memcpy(&yy, &yv, 4); fprintf(stderr, "[hudc] elem=%08x vp=%08x x=%g ey=%g scale=%g\n", ea, (uint32_t)ctx->r17, (double)ctx->f4.fl, (double)yy, (double)ctx->f6.fl); } }
      if (cp != 0.0) { double c = 160.0 * ctx->f6.fl; ctx->f4.fl = (float)(ctx->f4.fl + (ctx->f4.fl < c ? cp : -cp) * ctx->f6.fl); } }
'''
def apply(text):
    if T in text or text.count(ANC) != 1: return text, 0
    return text.replace(ANC, ANC.split("    // 0x800160C4")[0] + ADD + "    // 0x800160C4: lwc1        $f0, 0x1C($s1)\n"), 1
if __name__ == "__main__":
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c"); t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_4.c live patched x%d" % n)
