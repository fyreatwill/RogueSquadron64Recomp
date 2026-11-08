#!/usr/bin/env python3
"""s6963 G1e: the periodic game-thread CPU bursts behind the dd4 dense-second tail are clampGridCellLookup's instance-chain walk
(0x80048A7C..0x80048AB4; xctrace s6961: +231 of ~+300 ms/s in burst seconds, via streamTerrainGridCellsByDistance -> getGridCellValueAt).
ORIGIN: retail code; the chains only get long because our dd>1 window runs far past the map, so many off-map cells clamp to one edge
template. Hooks: rs64_s6963_pre before the walk (may answer from a host index and jump to the walk's exit), an iteration counter at the
loop head, rs64_s6963_post at the exit (learns / CHECK compare), rs64_s6963_create after the new record is linked (0x80048B4C).
Env in src/main/upstream_compat.cpp (ROGUESQ_G1E_CELLIDX, _CHECK, _BLK). Usage: apply_s6963_cellidx.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6963 cellidx"
f = D / "funcs_10.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
def ins(anchor, text, after=False):
    global t
    assert t.count(anchor) == 1, (anchor, t.count(anchor))
    t = t.replace(anchor, anchor + text if after else text + anchor, 1)
ins("    // 0x80048A70: lw          $a2, 0x7A5C($v0)\n",
    "    { extern int rs64_s6963_pre(uint8_t*, recomp_context*); if (rs64_s6963_pre(rdram, ctx)) goto L_80048ABC; } /* " + TAG + " */\n")
ins("L_80048A7C:\n", "    { extern uint64_t rs64_s6963_it; rs64_s6963_it++; } /* " + TAG + " */\n", after=True)
ins("L_80048ABC:\n", "    { extern void rs64_s6963_post(uint8_t*, recomp_context*); rs64_s6963_post(rdram, ctx); } /* " + TAG + " */\n", after=True)
ins("    // 0x80048B50: j           L_80048B8C\n",
    "    { extern void rs64_s6963_create(uint8_t*, recomp_context*); rs64_s6963_create(rdram, ctx); } /* " + TAG + " */\n")
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
