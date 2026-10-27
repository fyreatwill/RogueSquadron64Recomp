"""s6492 G1c: cumulative counters inside buildGridCellMeshForFace (funcs_9.c), g_s6492[0..7], printed as [forface] next to [gridcum].
[0] loop-body entries (L_8004323C) [1] cells reaching the jal buildGridCellMesh (L_8004349C) [2] last-cell exits at 0x800434A8
[3] ...of those, last cell had d2 < [0x8009DEB4] (a cell the d2 test never sees) [4] d2 test passes (c1cs) [5] chain-head set (s5==0 && pass)
[6] epilogues [7] epilogues with s5==0. Idempotent."""
import pathlib
TAG = "PATCH: s6492 forface"
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
if TAG in t: print("already"); raise SystemExit
def sub(old, new, cnt=1):
    global t
    assert t.count(old) == cnt, (old, t.count(old)); t = t.replace(old, new)
sub("L_8004323C:\n", "L_8004323C:\n    g_s6492[0]++; /* %s */\n" % TAG)
sub("L_8004349C:\n", "L_8004349C:\n    g_s6492[1]++; /* %s */\n" % TAG)
sub("    if (ctx->r3 == 0) {\n        // 0x800434AC: nop\n    \n            goto L_800431C0;\n",
    "    if (ctx->r3 == 0) {\n        g_s6492[2]++; { union { uint32_t u; float f; } a, b; a.u = MEM_W(ctx->r16, 8); b.u = MEM_W(0, (int64_t)(int32_t)0x8009DEB4); if (a.f < b.f) g_s6492[3]++; } /* %s */\n        // 0x800434AC: nop\n    \n            goto L_800431C0;\n" % TAG)
sub("    // 0x800434E8: nop\n\n    // 0x800434EC: bc1f        L_8004351C\n",
    "    if (c1cs) { g_s6492[4]++; if (ctx->r21 == 0) g_s6492[5]++; } /* %s */\n    // 0x800434E8: nop\n\n    // 0x800434EC: bc1f        L_8004351C\n" % TAG)
sub("L_80043780:\n", "L_80043780:\n    g_s6492[6]++; if (ctx->r21 == 0) g_s6492[7]++; /* %s */\n" % TAG)
first = t.index("RECOMP_FUNC void ")
t = t[:first] + "uint32_t g_s6492[8]; /* %s */\n" % TAG + t[first:]
p.write_text(t); print("ok")
