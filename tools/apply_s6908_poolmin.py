#!/usr/bin/env python3
"""s6908 G5h: cutscenes lose background at dd>1 because their terrain pool is authored small. setupCutsceneLevel (0x800A6D3C) passes
loadLevelAssets a per-scene size from the table at 0x800B090C (400, 600 seen) where a mission passes 2048 (0x8006B630). 0x80130C4C is that size
times POOLX, and our dd window clamp treats it as an area cap: LEVEL=4 intro dd4 cap 2400, window 37x64 where flight has 64x64, so the ground ends
on a straight line. ORIGIN: ours; the s6037 clamp reuses a pool size chosen for a retail radius, in a scene that dd has widened.
Fix: at dd>1 the pool is never below ROGUESQ_DD_POOLMIN (default 4096 = the 64x64 slot limit, set by the dd bundle; 0 = old). dd1 has no POOLX, so it never gets here.
ROGUESQ_DD_POOLMIN_TOG=1: the clamp alone uses the old size on odd mach seconds, pool unchanged, for a same-run comparison.
Runs after apply_s6058_poolx and the s6086 arm. Usage: apply_s6908_poolmin.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6908 poolmin"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = 'if (n > 0xFFFFu) n = 0xFFFFu; ctx->r4 = (int64_t)(int32_t)n; fprintf(stderr, "[poolx] cap %u -> %u\\n", o, n);'
N = ('if (n > 0xFFFFu) n = 0xFFFFu; g_s6908_old = n; { /* ' + TAG + ' */ const char* m = getenv("ROGUESQ_DD_POOLMIN"); uint32_t q = (m && *m) ? (uint32_t)atoi(m) : 0u; if (q > 0xFFFFu) q = 0xFFFFu; if (n < q && (int32_t)MEM_W(0, (int64_t)(int32_t)0x80130B70) < 19) n = q; } '
     'ctx->r4 = (int64_t)(int32_t)n; fprintf(stderr, "[poolx] cap %u -> %u (old %u)\\n", o, n, g_s6908_old);')
assert t.count(A) == 1, t.count(A)
t = t.replace(A, N, 1)
B = "          /* s6548 log */ static int n6548 = 0;"
C = ('          { /* ' + TAG + ' tog */ static int tg6908 = -1; extern uint64_t mach_absolute_time(void); if (tg6908 < 0) { const char* e = getenv("ROGUESQ_DD_POOLMIN_TOG"); tg6908 = (e && *e && *e != \'0\') ? 1 : 0; }\n'
     '            if (tg6908 && cap > 0 && g_s6908_old && (uint32_t)cap > g_s6908_old && ((mach_absolute_time() / 24000000u) & 1u)) cap = (int32_t)g_s6908_old; }\n')
assert t.count(B) == 1, t.count(B)
t = t.replace(B, C + B, 1)
P = "void rs64_g3e_trace(unsigned site, unsigned a, unsigned b, unsigned c, unsigned d); int rs64_g3e_on(void); /* s6788 ddtrace */\n"
assert t.count(P) == 1, t.count(P)
t = t.replace(P, P + "static uint32_t g_s6908_old; /* " + TAG + " */\n", 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
