"""s6555: per-swap visit census inside traverseSceneGraphRecursive's sibling loop (L_8001558C; s2 = node, next = *(s2)).
Gate ROGUESQ_TRAVLOG=1. Per swap: iterations, distinct nodes, revisits (cycle), first revisit node, min/max node addr, min sp
(recursion depth proxy, 0x90/frame), entry calls. Running line every 4096 iterations so the crash frame is still visible.
ROGUESQ_TRAV_SELFTEST=1 double-visits the first node of every swap (positive control: revisits must be >=1). Idempotent."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
T = P.read_text()
if "s6555 travwalk" in T:
    print("already"); raise SystemExit(0)
helper = r'''extern int rs64_swap_n(void);
static void s6555_visit(uint32_t node, uint32_t sp, int self) { /* PATCH: s6555 travwalk */
  static int en = -1, st = 0; if (en < 0) { const char* e = getenv("ROGUESQ_TRAVLOG"); en = (e && *e && *e != '0'); const char* s = getenv("ROGUESQ_TRAV_SELFTEST"); st = (s && *s && *s != '0'); if (en) fprintf(stderr, "[trav] enabled selftest=%d\n", st); }
  if (!en) return;
  static uint32_t tab[1u << 17], stamp[1u << 17]; static int cur = -1; static uint32_t it, dist, rev, firstrev, nmin, nmax, spmin, calls, nextlog;
  int n = rs64_swap_n();
  if (n != cur) { if (cur >= 0 && it) fprintf(stderr, "[trav] swap=%d iters=%u distinct=%u revisits=%u firstrev=%08x nodes=[%08x..%08x] depth=%u\n", cur, it, dist, rev, firstrev, nmin, nmax, (0x80300000u - spmin) / 0x90u);
    cur = n; it = dist = rev = firstrev = calls = 0; nmin = 0xFFFFFFFFu; nmax = 0; spmin = 0xFFFFFFFFu; nextlog = 4096; }
  if (!self) { /* the loop-top hook fires per iteration; entry calls are counted by sp pattern, not here */ }
  if (sp < spmin) spmin = sp;
  uint32_t h = (node * 2654435761u) >> 15, k = 0;
  while (k < (1u << 17)) { uint32_t i = (h + k) & ((1u << 17) - 1); if (stamp[i] != (uint32_t)(n + 1)) { stamp[i] = n + 1; tab[i] = node; dist++; break; } if (tab[i] == node) { rev++; if (!firstrev) firstrev = node; break; } k++; }
  it++; if (node < nmin) nmin = node; if (node > nmax) nmax = node;
  if (it >= nextlog) { nextlog += 4096; fprintf(stderr, "[trav] run swap=%d iters=%u distinct=%u revisits=%u firstrev=%08x nodes=[%08x..%08x] depth=%u\n", n, it, dist, rev, firstrev, nmin, nmax, (0x80300000u - spmin) / 0x90u); }
  if (st && it == 1 && !self) s6555_visit(node, sp, 1);
}
'''
sig = "RECOMP_FUNC void traverseSceneGraphRecursive("
i = T.find(sig); assert i > 0
T = T[:i] + helper + T[i:]
j = T.find(sig, i + len(helper)); assert j > 0
k = T.find("L_8001558C:\n", j); assert k > 0
k2 = k + len("L_8001558C:\n")
T = T[:k2] + "    s6555_visit(U32(ctx->r18), U32(ctx->r29), 0); /* PATCH: s6555 travwalk */\n" + T[k2:]
P.write_text(T); print("ok")
