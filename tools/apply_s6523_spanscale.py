"""s6523: H-scale arm. ROGUESQ_SPANSCALE=<s> divides the span-grid height scale f22 (writer, scanConvertTriangleToSpanTable
0x800422C8) AND the cell-record thresholds rec[3]/rec[4] (consumer, streamTerrainGridCellsByDistance 0x80042D88/9C) by s, so
dd>1 far-column heights stay inside the signed-byte range. s=1 (default) is bit-identical to retail. Experiment arm only."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
if "s6523 spanscale" in T:
    print("already"); raise SystemExit(0)
helper = r'''static inline int s6523_scale(void) { /* PATCH: s6523 spanscale */
  static int s = 0; if (!s) { const char* e = getenv("ROGUESQ_SPANSCALE"); s = (e && atoi(e) > 0) ? atoi(e) : 1;
    if (s != 1) fprintf(stderr, "[spanscale] s=%d\n", s); } return s; }
'''
a0 = "    // 0x800422C8: mtc1        $a3, $f22\n    ctx->f22.u32l = ctx->r7;\n"
assert T.count(a0) == 1
T = T.replace(a0, a0 + "    { int s6523 = s6523_scale(); if (s6523 != 1) ctx->f22.fl = ctx->f22.fl / (float)s6523; } /* PATCH: s6523 spanscale */\n", 1)
for off in ("3", "4"):
    a = f"    // 0x80042D{'88' if off == '3' else '9C'}: lb          $v0, 0x{off}($v1)\n    ctx->r2 = MEM_B(ctx->r3, 0X{off});\n"
    assert T.count(a) == 1, off
    T = T.replace(a, a + "    { int s6523 = s6523_scale(); if (s6523 != 1) ctx->r2 = (int64_t)((int)(int8_t)ctx->r2 / s6523); } /* PATCH: s6523 spanscale */\n", 1)
# helper placed before the first function definition that uses it
m = "RECOMP_FUNC void scanConvertTriangleToSpanTable("
i = T.find(m); assert i > 0
T = T[:i] + helper + T[i:]
P.write_text(T); print("ok")
