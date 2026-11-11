#!/usr/bin/env python3
"""s7107 fps60-wall-painter: publish the TRI_GEN key (w0, word 8, word 9) of the last command the CPU emitted for EVERY one of the
49 terrain cells around the eye (7x7, s7105 index i = (dz+3)*7 + dx+3, i = 24 eye cell) into g_s7107_kw/k8/k9[49]
(src/rsp/s7106_rsptri.cpp), so the ucode-side tag FIFO (ROGUESQ_S7107_TAG=1) can label every RDP triangle with its source cell.
Needs apply_s7106_rsptri first. Gate: s7105_visit returns unless ROGUESQ_S7105_EMIT=1 (+ S7104_CELL=1, CHASE open).
Measurement only. Idempotent."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7107 painter"
p = BASE / "funcs_4.c"; t = p.read_text(errors="surrogateescape")
if MARK in t:
    print(p.name, "s7107 painter already applied"); sys.exit(0)
A = "    { int dx = i % 7 - 3, dz = i / 7 - 3; if (!un && dx >= -1 && dx <= 1 && dz >= -1 && dz <= 1) { int j = (dz + 1) * 3 + dx + 1; /* PATCH: s7106 rsptri */\n"
if t.count(A) != 1: sys.exit("s7107: s7106 anchor count %d" % t.count(A))
R = ("    if (!un) { g_s7107_kw[i] = g_s7105_w0[i]; g_s7107_k8[i] = (uint32_t)MEM_W(0x20, (int64_t)(int32_t)cmd); "
     "g_s7107_k9[i] = (uint32_t)MEM_W(0x24, (int64_t)(int32_t)cmd); } /* " + MARK + " */\n")
D = "extern uint32_t g_s7106_kw[9], g_s7106_k8[9], g_s7106_k9[9]; /* PATCH: s7106 rsptri */\n"
if t.count(D) != 1: sys.exit("s7107: extern anchor count %d" % t.count(D))
t = t.replace(A, R + A).replace(D, D + "extern uint32_t g_s7107_kw[49], g_s7107_k8[49], g_s7107_k9[49]; /* " + MARK + " */\n")
p.write_text(t, errors="surrogateescape")
print(p.name, "s7107 painter applied")
