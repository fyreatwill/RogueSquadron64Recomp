"""s6522: log pre-clamp value/bounds at the span edge-loop clamp (funcs_9.c, 0x80042820 sb site).
Env ROGUESQ_CLAMPP=1. Per call: col(a0), rowbase(t1), layer(t4), pre-clamp f4, bounds f12/f10, f2, f22, result.
Aggregates: per (dd arm) counts of f4<f12, f4>f10, inside; first 40 rows of each class printed. Observation only."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
if "s6522 clampp" in T:
    print("already"); raise SystemExit(0)
anchor = "    // 0x80042820: sb          $v1, 0x0($v0)\n    s6512_note_writer(0x80042820u,"
assert T.count(anchor) == 1
probe = r'''    { /* PATCH: s6522 clampp */ static int e = -1; static unsigned n[3], pr[3], tot;
      if (e < 0) { const char* s = getenv("ROGUESQ_CLAMPP"); e = (s && *s) ? 1 : 0; }
      if (e) { int cls = ctx->f4.fl < ctx->f12.fl ? 0 : (ctx->f4.fl > ctx->f10.fl ? 1 : 2); n[cls]++; tot++;
        if (pr[cls]++ < 40) fprintf(stderr, "[clampp] cls=%d col=%d rowb=%d layer=%d f4=%g lo=%g hi=%g f2=%g f22=%g res=%d\n", cls, (int)ctx->r4, (int)ctx->r9, (int)ctx->r12, (double)ctx->f4.fl, (double)ctx->f12.fl, (double)ctx->f10.fl, (double)ctx->f2.fl, (double)ctx->f22.fl, (int)ctx->r3);
        if ((tot & 0x3FFFFu) == 0) fprintf(stderr, "[clampp] tot=%u below=%u above=%u inside=%u\n", tot, n[0], n[1], n[2]); } }
'''
T = T.replace(anchor, probe + anchor, 1)
P.write_text(T); print("ok")
