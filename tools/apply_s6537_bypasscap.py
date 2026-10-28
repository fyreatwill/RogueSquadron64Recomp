"""s6537: cap span-bypass force-accepts per swap. ROGUESQ_BYPASS_MAXCELLS=N (unset/<0 = unlimited, bit-identical to s6529).
Only counts cells the retail compare WOULD have rejected (r2==1) and the bypass flips to accept; once N are taken in a swap, later rejects stay rejected.
streamTerrainGridCellsByDistance walks cells by distance, so the cap keeps the nearest N extra cells."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
try:
    import apply_s6529_spanbypass  # noqa: F401  (applies s6527+s6529 if absent; exits via SystemExit if already)
except SystemExit:
    pass
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
if "s6537 bypasscap" in T:
    print("already"); raise SystemExit(0)
helper = r'''static inline int s6537_take(void) { /* PATCH: s6537 bypasscap */
  static int cap = -2, lastn = -1, used = 0; if (cap == -2) { const char* s = getenv("ROGUESQ_BYPASS_MAXCELLS"); cap = (s && *s) ? atoi(s) : -1; if (cap >= 0) fprintf(stderr, "[bypasscap] maxcells=%d\n", cap); }
  if (cap < 0) return 1;
  int n = rs64_swap_n(); if (n != lastn) { lastn = n; used = 0; }
  if (used >= cap) return 0; used++; return 1; }
'''
old = "    if (s6527_force()) ctx->r2 = 0; /* PATCH: s6527 spanforce */\n"
new = "    if (ctx->r2 && s6527_force() && s6537_take()) ctx->r2 = 0; /* PATCH: s6527 spanforce */\n"
assert T.count(old) == 2
T = T.replace(old, new)
m = "RECOMP_FUNC void scanConvertTriangleToSpanTable("
i = T.find(m); assert i > 0
T = T[:i] + helper + T[i:]
P.write_text(T); print("ok")
