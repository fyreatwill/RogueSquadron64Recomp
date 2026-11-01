"""s6144 G1d: widen the terrain-footprint frustum horizontally under widescreen.
buildVisibleTerrainGridAroundCamera (0x800437B0) builds the 4 footprint planes from the corner vector
(x = fovScalar(0x80130C50)*c, y, z) stored at 0x40($sp) by the swc1 at 0x800438C4. x is the horizontal half-extent
and ignores the widened aspect, so cells left/right of the 4:3 frustum are never submitted (21:9 left void, s6143).
ROGUESQ_FP_XSCALE=<k> (default: ROGUESQ_ASPECT_SCALE, else 1.0 = retail) multiplies that x. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    { MEM_W(0X40, ctx->r29) = ctx->f4.u32l; RS64_S5798_ST(0x800438C4u, 0X40, ctx->r29, 4); }\n"
NEW = r'''    { /* PATCH: s6144 fpx */ static double kx6144 = -1.0; if (kx6144 < 0.0) { const char* e = getenv("ROGUESQ_FP_XSCALE"); if (!e || !*e) e = getenv("ROGUESQ_ASPECT_SCALE"); kx6144 = (e && *e) ? atof(e) : 1.0; if (kx6144 <= 0.0) kx6144 = 1.0; if (kx6144 != 1.0) fprintf(stderr, "[g1d] footprint x-extent x%g\n", kx6144); }
      if (kx6144 != 1.0) { union { uint32_t u; float f; } c; c.u = ctx->f4.u32l; c.f = (float)(c.f * kx6144); ctx->f4.u32l = c.u; } }
'''
def apply9(text):
    if "PATCH: s6144 fpx" in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW + OLD), 1
# s6719 G1d: the 640x480 boot state (LucasArts logo carved from Hoth terrain) is never widened, and there the x-extent
# widening alone draws the logo ~1.75x too wide (settled-logo purple bbox w/h 2.13 at 21:9 vs retail 1.23; 1.16-1.27
# with ROGUESQ_ASPECT_SCALE=1; the s6719 guPerspective factor alone changed nothing). Keep kx at 1.0 while the
# video-state width at 0x8011A838 is <= 640, and at intro_w/640 in the s6718-widened 640x340 intro state (the logo is
# drawn there: 768 at 21:9), i.e. the same factor guPerspective gets. ROGUESQ_G1D_640PERSP=0 restores the old scaling.
S6719_OLD = "      if (kx6144 != 1.0) { union"
S6719_NEW = ("      { extern int rs64_g1d_intro_w, rs64_g1d_vs_intro; static int on6719 = -1; static double lk6719 = -1.0; int w6719 = (int32_t)MEM_W(-0X57C8, (gpr)(int32_t)0x80120000); if (on6719 < 0) { const char* e = getenv(\"ROGUESQ_G1D_640PERSP\"); on6719 = !(e && *e == '0'); }\n"
             "        double k6719 = !on6719 ? kx6144 : (rs64_g1d_vs_intro && rs64_g1d_intro_w > 640) ? rs64_g1d_intro_w / 640.0 : w6719 <= 640 ? 1.0 : kx6144;\n"
             "        if (kx6144 != 1.0 && k6719 != lk6719) { lk6719 = k6719; fprintf(stderr, \"[g1d-640p] fbw %d footprint x%g\\n\", w6719, k6719); }\n"
             "      if (k6719 != 1.0) { union")
S6719_MUL = "c.f = (float)(c.f * kx6144); ctx->f4.u32l = c.u; } }"
def apply9_s6719(text):
    if "on6719" in text or text.count(S6719_OLD) != 1: return text, 0
    text = text.replace(S6719_OLD, S6719_NEW, 1)
    i = text.find(S6719_NEW); m = text.find(S6719_MUL, i); assert m > 0
    return text[:m] + S6719_MUL.replace("kx6144", "k6719") + " }" + text[m + len(S6719_MUL):], 1

if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t); t2, m = apply9_s6719(t2); n += m
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
