"""s6527: H-reject-harmless discriminator. ROGUESQ_SPANFORCE=1 makes streamTerrainGridCellsByDistance's two span compares
(0x80042D8C A<rec[3], 0x80042DA4 rec[4]<plane) never reject, so every in-window cell is accepted. Unset = bit-identical.
Experiment arm only: compare terrain fraction of dd4 vs dd4+SPANFORCE in the same pinned run."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
if "s6527 spanforce" in T:
    print("already"); raise SystemExit(0)
helper = r'''static inline int s6527_force(void) { /* PATCH: s6527 spanforce */
  static int e = -1; if (e < 0) { const char* s = getenv("ROGUESQ_SPANFORCE"); e = (s && *s) ? 1 : 0; if (e) fprintf(stderr, "[spanforce] on\n"); } return e; }
'''
a1 = "    // 0x80042D8C: slt         $v0, $a0, $v0\n    ctx->r2 = SIGNED(ctx->r4) < SIGNED(ctx->r2) ? 1 : 0;\n"
a2 = "    // 0x80042DA4: slt         $v0, $v0, $v1\n    ctx->r2 = SIGNED(ctx->r2) < SIGNED(ctx->r3) ? 1 : 0;\n"
assert T.count(a1) == 1 and T.count(a2) == 1
T = T.replace(a1, a1 + "    if (s6527_force()) ctx->r2 = 0; /* PATCH: s6527 spanforce */\n", 1)
T = T.replace(a2, a2 + "    if (s6527_force()) ctx->r2 = 0; /* PATCH: s6527 spanforce */\n", 1)
m = "RECOMP_FUNC void scanConvertTriangleToSpanTable("
i = T.find(m); assert i > 0
T = T[:i] + helper + T[i:]
P.write_text(T); print("ok")
