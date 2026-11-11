#!/usr/bin/env python3
"""s7106 fps60-wall-rsp-clip: publish the TRI_GEN key (w0, word 8, word 9 = +0x00/+0x20/+0x24 of the 0x28-byte command) of the
last command the CPU emitted for each ring<=1 terrain cell around the eye (s7105_visit, renderFlatMeshFaceGroup visits only) into
g_s7106_kw/k8/k9 (src/rsp/s7106_rsptri.cpp), so the ucode-side census can attribute RDP triangles to those 9 cells.
Slot j = (dz+1)*3 + (dx+1), row-major dz -1..1, dx -1..1 (slot 4 = eye cell). Needs apply_s7105_emit (s7105_visit) first.
Gate: s7105_visit already returns unless ROGUESQ_S7105_EMIT=1 (and S7104_CELL=1, CHASE open, through s7105's own exit gate);
ROGUESQ_S7106_RSPTRI=<file> arms the ucode side. Measurement only. Idempotent."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7106 rsptri"
p = BASE / "funcs_4.c"; t = p.read_text(errors="surrogateescape")
if MARK in t:
    print(p.name, "s7106 rsptri already applied"); sys.exit(0)
if "PATCH: s7105 emit" not in t: sys.exit("s7106: needs apply_s7105_emit first")
A = ("  for (int i = 0; i < 49; i++) if (g_s7105_el[i] == el) { if (g_s7105_vis[i] < 255) g_s7105_vis[i]++; "
     "g_s7105_w0[i] = (uint32_t)MEM_W(0, (int64_t)(int32_t)cmd); } }\n")
if t.count(A) != 1: sys.exit("s7106: s7105_visit anchor count %d" % t.count(A))
R = ("  for (int i = 0; i < 49; i++) if (g_s7105_el[i] == el) { if (g_s7105_vis[i] < 255) g_s7105_vis[i]++; "
     "g_s7105_w0[i] = (uint32_t)MEM_W(0, (int64_t)(int32_t)cmd);\n"
     "    { int dx = i % 7 - 3, dz = i / 7 - 3; if (!un && dx >= -1 && dx <= 1 && dz >= -1 && dz <= 1) { int j = (dz + 1) * 3 + dx + 1; /* " + MARK + " */\n"
     "      g_s7106_kw[j] = g_s7105_w0[i]; g_s7106_k8[j] = (uint32_t)MEM_W(0x20, (int64_t)(int32_t)cmd); g_s7106_k9[j] = (uint32_t)MEM_W(0x24, (int64_t)(int32_t)cmd); } } } }\n")
D = "extern uint8_t g_s7105_vis[49];\n"
if t.count(D) != 1: sys.exit("s7106: extern anchor count %d" % t.count(D))
t = t.replace(A, R).replace(D, D + "extern uint32_t g_s7106_kw[9], g_s7106_k8[9], g_s7106_k9[9]; /* " + MARK + " */\n")
p.write_text(t, errors="surrogateescape")
print(p.name, "s7106 rsptri applied")
