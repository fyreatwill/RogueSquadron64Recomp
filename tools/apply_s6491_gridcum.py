"""s6491 G1c: cumulative counters in buildVisibleTerrainGridAroundCamera (funcs_9.c): [0]=calls reaching the post-stream point,
[1]=calls whose cell list head (s0) is nonzero, [2]=calls where buildGridCellMeshForFace returned with a nonempty mesh chain (*s4 != 0).
upstream_compat.cpp prints them as [gridcum] at each [fbdump]. Idempotent."""
import pathlib
TAG = "PATCH: s6491 gridcum"
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
if TAG in t: print("already"); raise SystemExit
a = "    after_10:\n    { /* PATCH: s6034 gridlog */"
b = "    after_11:\n    { /* PATCH: s6417 meshlog */"
assert t.count(a) == 1 and t.count(b) == 1
t = t.replace(a, "    after_10:\n    { g_s6491[0]++; if (ctx->r16) g_s6491[1]++; } /* %s */\n    { /* PATCH: s6034 gridlog */" % TAG)
t = t.replace(b, "    after_11:\n    { if (MEM_W(0, ctx->r20)) g_s6491[2]++; } /* %s */\n    { /* PATCH: s6417 meshlog */" % TAG)
first = t.index("RECOMP_FUNC void ")
t = t[:first] + "uint32_t g_s6491[4]; /* %s */\n" % TAG + t[first:]
p.write_text(t); print("ok")
