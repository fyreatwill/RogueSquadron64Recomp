"""s6492b G1c: entry/a0zero counters g_s6492[8..9] in buildGridCellMeshForFace + ROGUESQ_FORFACE_LOG [ffempty] line (first 60 empty-chain epilogues).
Run after tools/apply_s6492_forface_cum.py. upstream_compat.cpp prints [forface] (already edited, committed). Idempotent."""
import pathlib
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
TAG = "PATCH: s6492b forface"
if TAG in t: print("already"); raise SystemExit
t = t.replace("uint32_t g_s6492[8];", "uint32_t g_s6492[12]; static uint32_t s6492_ent;")
sig = "RECOMP_FUNC void buildGridCellMeshForFace(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
assert t.count(sig) == 1
t = t.replace(sig, sig + "    g_s6492[8]++; s6492_ent = g_s6492[0]; if (ctx->r4 == 0) g_s6492[9]++; /* " + TAG + " */\n")
old = "L_80043780:\n    g_s6492[6]++; if (ctx->r21 == 0) g_s6492[7]++; /* PATCH: s6492 forface */\n"
assert t.count(old) == 1
new = old + r'''    if (ctx->r21 == 0 && getenv("ROGUESQ_FORFACE_LOG")) { static int nl6492 = 0; if (nl6492++ < 60) { union { uint32_t u; float f; } d, b; uint32_t a0 = MEM_W(ctx->r29, 0X38); d.u = a0 ? MEM_W(a0, 8) : 0; b.u = MEM_W(0, (int64_t)(int32_t)0x8009DEB4);
      fprintf(stderr, "[ffempty] a0=0x%08X head_d2=%g deb4=%g gate=%u iters=%u\n", a0, d.f, b.f, (unsigned)MEM_W(4, (int64_t)(int32_t)0x80136DC0), g_s6492[0] - s6492_ent); } } /* @@T@@ */
'''.replace("@@T@@", TAG)
t = t.replace(old, new)
p.write_text(t); print("ok")
