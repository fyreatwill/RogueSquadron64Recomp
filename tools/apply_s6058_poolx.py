"""s6058 G1c: ROGUESQ_DD_POOLX=<k> multiplies the terrain stream-pool capacity argument (a0, stored to 0x80130C4C and
used as malloc(cap*0x18) at loadLevelAssets 0x800453C8). Unset = retail. Tests whether the pool cap truncates dd>=1.5 frames. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    // 0x800453C8: addiu       $sp, $sp, -0x48\n    ctx->r29 = ADD32(ctx->r29, -0X48);\n"
NEW = r'''    { /* PATCH: s6058 poolx */ const char* e = getenv("ROGUESQ_DD_POOLX"); if (e && *e) { double k = atof(e); if (k >= 1.0 && k <= 16.0) { uint32_t o = (uint32_t)ctx->r4 & 0xFFFFu, n = (uint32_t)(o * k); if (n > 0xFFFFu) n = 0xFFFFu; ctx->r4 = (int64_t)(int32_t)n; fprintf(stderr, "[poolx] cap %u -> %u\n", o, n); } } }
'''
def apply9(text):
    if "PATCH: s6058 poolx" in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
