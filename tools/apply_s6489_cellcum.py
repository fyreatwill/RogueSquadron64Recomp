"""s6489 G1c: cumulative (never reset) copy of the s6476 buildGridCellMesh exit counters, g_s6489[0..7]
(e7 = normal fall-through = cell passed every gate). upstream_compat.cpp prints them at every [fbdump] as [cellcum],
so tools/g1c_cellpass_tris.py can difference them per dump window and join with tricnt + ground score. Idempotent."""
import re, pathlib
TAG = "PATCH: s6489 cellcum"
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_10.c")
t = p.read_text()
if TAG in t: print("already"); raise SystemExit
n = [0]
def rep(m):
    n[0] += 1
    return "%s g_s6489[%s]++; /* %s */" % (m.group(0), m.group(1), TAG)
t = re.sub(r"g_s6476\[(\d)\]\+\+;(?: /\* PATCH: s6476 exitcount \*/)?", rep, t)
first = t.index("RECOMP_FUNC void ")
t = t[:first] + "uint32_t g_s6489[8]; /* %s */\n" % TAG + t[first:]
p.write_text(t); print("sites", n[0])
