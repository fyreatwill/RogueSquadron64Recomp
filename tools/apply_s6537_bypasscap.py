"""s6537: cap span-bypass force-accepts per swap. ROGUESQ_BYPASS_MAXCELLS=N (<0 = unlimited; unset = 120 when ROGUESQ_DRAW_DISTANCE>1 (s6540), else unlimited).
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
  static int cap = -2, lastn = -1, used = 0; if (cap == -2) { const char* s = getenv("ROGUESQ_BYPASS_MAXCELLS"); cap = (s && *s) ? atoi(s) : -1; if (!(s && *s)) { const char* d = getenv("ROGUESQ_DRAW_DISTANCE"); if (d && atof(d) > 1.0) cap = 120; } /* s6540: dd>1 default 120 */ if (cap >= 0) fprintf(stderr, "[bypasscap] maxcells=%d\n", cap); }
  static int alt = -2, rej = 0, cur = -1; if (alt == -2) { const char* a = getenv("ROGUESQ_CAP_ALT"); alt = (a && atoi(a) > 0) ? atoi(a) : 0; if (alt) fprintf(stderr, "[capalt] period=%d\n", alt); }
  int n = rs64_swap_n();
  if (alt) { /* s6542: same-run toggle: cap 0 / 120 / inf rotating every `alt` swaps */
    if (n != lastn) { if (lastn >= 0) fprintf(stderr, "[capalt] swap=%d cap=%d taken=%d rejected=%d\n", lastn, cur, used, rej); lastn = n; used = 0; rej = 0; int ph = n > 0 ? ((n - 1) / alt) % 3 : 0; cur = ph == 0 ? 0 : (ph == 1 ? 120 : -1); }
    if (cur < 0) { used++; return 1; }
    if (used >= cur) { rej++; return 0; } used++; return 1; }
  if (cap < 0) return 1;
  if (n != lastn) { lastn = n; used = 0; }
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
