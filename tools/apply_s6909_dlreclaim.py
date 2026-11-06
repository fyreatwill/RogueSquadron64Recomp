#!/usr/bin/env python3
"""s6909: the dd>1 DL chunk arena (rs64_s6099_alloc, 4 MB ending 0x81000000) is a bump allocator with no way back, so every scene's grows add up and
the 18th or so scene load runs it dry: AT THE MOVIES dd4 16:9 died 8 min in, 15872 chunks, `[dlpoolx] arena exhausted`, then a NULL node store
(si_addr 0x380000004) in renderFlatMeshFaceGroup under cinematicLoopBody.
ORIGIN: ours (s6099/s6284 arena). buildAndRegisterDefaultMaterial (0x80017B88) relinks the game's fixed chunk pool and stores a new head at
0x80018094, which drops every chunk the old list held, so arena chunks linked into it are unreachable from then on and the arena can restart.
ROGUESQ_DLPOOLX_RECLAIM=0 = old (never reset). Logs `[dlpoolx] rebuild` either way, so the rebuilds are countable in the =0 arm.
The hook sits before the store, so s6564 reinitx (after the store) still allocates from the reset arena. Usage: apply_s6909_dlreclaim.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6909 dlreclaim"
f = D / "funcs_4.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "    // 0x80018094: sw          $s2, 0x63B0($at)\n"
assert t.count(A) == 1, t.count(A)
t = t.replace(A, "    { extern void rs64_s6909_rebuild(void); rs64_s6909_rebuild(); } /* " + TAG + " */\n" + A, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
