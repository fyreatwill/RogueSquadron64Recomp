"""s6789 G3e fix: scanConvertTriangleToSpanTable (0x80042298) clamps each frustum-footprint height byte to [-128.0, 127.0]
(ROM floats 0x8003A4E8/EC and 0x8003A4F0/F4) before `sb` into the span tables 0x80131DB0 / 0x80130DB0. But -128 (0x80) is also
the "cell untouched" sentinel those tables are cleared to (binPolygonIntoTerrainGrid 0x80042A74/78), and
streamTerrainGridCellsByDistance skips a cell when both bytes are 0x80 (0x80042D58/64). At retail draw distance the pyramid
never reaches -128; at dd>1 the far corners sit ~4x deeper, so saturated cells read as off-screen and ~1400 visible cells
drop for 4-6 frames whenever the pose pushes them past the clamp (s6789 trace: spaneq 61 -> 957 per call on dip calls).
Fix: when ROGUESQ_DRAW_DISTANCE>1, clamp the low end to -127.0 so a saturated height is never the sentinel. dd<=1 is
bit-identical retail. ROGUESQ_SPANSENT_FIX=0 opts out; ROGUESQ_SPANSENT_TOG=N alternates off/on every N calls (same-run A/B,
state printed as [spansent]). Idempotent."""
import pathlib
P = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
TAG = "/* PATCH: s6789 spansent */"
HELPER = ("static int s6789_spansent(void) { " + TAG + "\n"
          "  static int on = -1, tog = 0, last = -1; static unsigned n = 0;\n"
          "  if (on < 0) { const char* d = getenv(\"ROGUESQ_DRAW_DISTANCE\"); const char* f = getenv(\"ROGUESQ_SPANSENT_FIX\"); const char* t = getenv(\"ROGUESQ_SPANSENT_TOG\");\n"
          "    on = (d && atof(d) > 1.0 && !(f && f[0] == '0')) ? 1 : 0; tog = t ? atoi(t) : 0; fprintf(stderr, \"[spansent] fix=%d tog=%d\\n\", on, tog); }\n"
          "  if (!on) return 0; if (tog <= 0) return 1;\n"
          "  { int b = (int)((n++ / (unsigned)tog) & 1u); if (b != last) { last = b; if (rs64_g3e_on()) rs64_g3e_trace(10, (uint32_t)b, n, 0, 0); } return b; } }\n")
ANCHOR = "RECOMP_FUNC void scanConvertTriangleToSpanTable(uint8_t* rdram, recomp_context* ctx) {"
SITES = ["    ctx->f10.u32l = MEM_W(ctx->r1, -0X5B14);\n", "    ctx->f10.u32l = MEM_W(ctx->r1, -0X5B0C);\n"]
def apply(t):
    if TAG in t: return t, 0
    assert t.count(ANCHOR) == 1 and "int rs64_g3e_on(void);" in t
    s = t.index(ANCHOR); e = t.index("RECOMP_FUNC", s + 10)
    body = t[s:e]
    for o in SITES: assert body.count(o) == 1, o
    for o in SITES:
        body = body.replace(o, o + "    if (s6789_spansent()) ctx->f10.u32l = 0xC2FE0000u; /* -127.0f */ " + TAG + "\n", 1)
    t = t[:s] + HELPER + body + t[e:]
    return t, 1
if __name__ == "__main__":
    t = P.read_text(); t2, n = apply(t)
    if n: P.write_text(t2)
    print("funcs_9.c s6789 spansent x%d" % n)
