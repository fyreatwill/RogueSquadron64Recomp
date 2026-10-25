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
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
