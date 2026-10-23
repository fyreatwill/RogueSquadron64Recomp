"""s6048 G1c: bound the span-table byte stores in scanConvertTriangleToSpanTable (0x800426D8, 0x80042820).
Writer proof (s6047 lldb write-watch on the terrain table pointer 0x80136DC4): these stores, addr = 0x80130DB0 + row*64 + col,
overwrote the pointer with 0x7f bytes (0x80246434 -> 7f246434 -> 7f7f6434 -> 7f7f7f34 -> 7f7f7f7f) when row ~384. The min/max arrays
(0x80130C70/0x80130D10, 0xA0 bytes) hold 80 rows and a row is 64 columns; the row range (a1..t3) is unclamped. Retail footprints
fit; a ROGUESQ_DRAW_DISTANCE-scaled footprint does not. Active only when ROGUESQ_DRAW_DISTANCE != 1. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
def guard(pc):
    old = "    { MEM_B(0X0, ctx->r2) = ctx->r3; RS64_S5798_ST(0x%08Xu, 0X0, ctx->r2, 1); }\n" % pc
    new = ("    { /* PATCH: s6048 spanbound */ static int on6048 = -1; static unsigned n6048;\n"
           "      if (on6048 < 0) { const char* e = getenv(\"ROGUESQ_DRAW_DISTANCE\"); on6048 = (e && *e && atof(e) != 1.0) ? 1 : 0; }\n"
           "      if (on6048 && ((uint32_t)ctx->r5 >= 80u || (uint32_t)ctx->r4 >= 64u)) { if (n6048++ < 8) fprintf(stderr, \"[spanbound] skip row=%%d col=%%d pc=%08Xu\\n\", (int)ctx->r5, (int)ctx->r4); }\n"
           "      else ") % pc + old.lstrip().rstrip("\n") + " }\n"
    return old, new
def apply9(text):
    if "PATCH: s6048 spanbound" in text: return text, 0
    n = 0
    for pc in (0x800426D8, 0x80042820):
        old, new = guard(pc)
        if text.count(old) != 1: continue
        text = text.replace(old, new); n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
