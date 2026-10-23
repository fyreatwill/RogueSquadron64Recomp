"""s6036 G1c: ROGUESQ_DRAW_DISTANCE=<m> scales the terrain-window radius float (0x8009DEAC, 14.5) at its read in
buildVisibleTerrainGridAroundCamera (0x80043918, funcs_9.c). Unset/1.0 = retail. m clamped to [0.25,4]. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    // 0x80043918: lwc1        $f2, -0x2154($v0)\n    ctx->f2.u32l = MEM_W(ctx->r2, -0X2154);\n"
NEW = r'''    { /* PATCH: s6036 dd */ static float m6036 = -1.0f;
      if (m6036 < 0.0f) { const char* e = getenv("ROGUESQ_DRAW_DISTANCE"); double v = (e && *e) ? atof(e) : 1.0; if (v < 0.25) v = 0.25; if (v > 4.0) v = 4.0; m6036 = (float)v; fprintf(stderr, "[dd] ROGUESQ_DRAW_DISTANCE multiplier %g\n", m6036); }
      if (m6036 != 1.0f && MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0) { union { uint32_t u; float f; } c; c.u = ctx->f2.u32l; c.f *= m6036; ctx->f2.u32l = c.u; } }
'''
def apply9(text):
    if "PATCH: s6036 dd" in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, OLD + NEW), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
