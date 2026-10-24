"""s6048/s6049 G1c: bound the span-table byte stores of the terrain rasteriser (funcs_9.c, 0x800426D8..0x80042EC4).
Layout (s6049, from binPolygonIntoTerrainGrid 0x80042A44-0x80042A50): two 64x64 byte tables, min at 0x80130DB0 and max at
0x80131DB0 (0x1000 each, end 0x80132DB0). Writer proof (s6047 lldb): these stores overwrote the terrain-table pointer at
0x80136DC4 with 0x7f bytes (row ~384 = footprint far beyond 64 rows). s6048 guarded only 0x800426D8/0x80042820 on row>=80 and
dd2b still crashed with the same 0x7F7F.. window: the clear loop (0x80042A74/78) and the clamp stores (0x80042DB4/DC0/EC4)
write the same tables unbounded. s6049 skips any store at these seven sites whose guest address lies outside the tables.
Active only when ROGUESQ_DRAW_DISTANCE != 1 (retail path untouched). Idempotent; upgrades s6048-patched text."""
import pathlib, re
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
SITES = (0x800426D8, 0x80042820, 0x80042A74, 0x80042A78, 0x80042DB4, 0x80042DC0, 0x80042EC4)
PAT = r"    \{ MEM_B\(0X0, ctx->(r\d+)\) = ctx->(r\d+); RS64_S5798_ST\(0x%08Xu, 0X0, ctx->\1, 1\); \}\n"
OLD6048 = re.compile(r"    \{ /\* PATCH: s6048 spanbound \*/.*?\n      else (\{ MEM_B\(0X0, ctx->r\d+\) = ctx->r\d+; RS64_S5798_ST\(0x[0-9A-F]+u, 0X0, ctx->r\d+, 1\); \})\n    \}\n", re.S)
def new_block(pc, reg, val):
    return ("    { /* PATCH: s6049 tablebound */ static int on6049 = -1; static unsigned n6049;\n"
            "      if (on6049 < 0) { const char* e = getenv(\"ROGUESQ_DRAW_DISTANCE\"); on6049 = (e && *e && atof(e) != 1.0) ? 1 : 0; }\n"
            "      if (on6049 && (uint32_t)(U32(ctx->%s) - 0x80130DB0u) >= 0x2000u) { if (n6049++ < 8) fprintf(stderr, \"[spanbound] skip addr=0x%%08X pc=0x%08X\\n\", (unsigned)U32(ctx->%s)); }\n"
            "      else { MEM_B(0X0, ctx->%s) = ctx->%s; RS64_S5798_ST(0x%08Xu, 0X0, ctx->%s, 1); }\n    }\n") % (reg, pc, reg, reg, val, pc, reg)
def apply9(text):
    n = 0
    # upgrade s6048 blocks back to the raw store, then wrap uniformly
    text, k = OLD6048.subn(lambda m: "    " + m.group(1) + "\n", text)
    for pc in SITES:
        def rep(m):
            nonlocal n
            n += 1
            return new_block(pc, m.group(1), m.group(2))
        text = re.sub(PAT % pc, rep, text)
    return text, n
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if t2 != t: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
