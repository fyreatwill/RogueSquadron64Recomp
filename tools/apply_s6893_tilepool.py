#!/usr/bin/env python3
"""s6893 G5a ROOT CAUSE: selectGridCellTileVariant (0x80046030) writes 25 bytes to pool[phase] + 25*count with no bound.
initGridLayerFromLevelData sizes each pool for one slot per flagged map cell (lvl4: 90 -> req 0x8CA). The dd>1 window visits
more than that in a frame (count 0x5E = 94 read back from RDRAM in one dd2 tour; most runs peak lower), so the pool ran into
the next block, the sky object (hardware watch names this store). That this is the owner's two crashes is inference: same object,
same word, same kind of junk bytes; the owner's mission has not been re-flown. Fix: pools scale with the window
(rs64_s6893_tilepool_size) and the writer's slot index is bounded (rs64_s6893_tileslot). dd1 4:3 keeps retail size.
ROGUESQ_TILEPOOL=0 restores both. Usage: apply_s6893_tilepool.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6893 tilepool"
f = D / "funcs_10.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
HEAD = "RECOMP_FUNC void initGridLayerFromLevelData(uint8_t* rdram, recomp_context* ctx) {"
DECL = "/* %s */ extern uint32_t rs64_s6893_tilepool_size(uint32_t); extern uint32_t rs64_s6893_tileslot(uint32_t);\n" % TAG
A1 = "    // 0x800459E0: addu        $a0, $s0, $zero\n    ctx->r4 = ADD32(ctx->r16, 0);\n"
A2 = "    // 0x800459EC: addu        $a0, $s0, $zero\n    ctx->r4 = ADD32(ctx->r16, 0);\n"
W = "    // 0x80046150: lw          $v1, 0x7168($v0)\n    ctx->r3 = MEM_W(ctx->r2, 0X7168);\n"
SZ = "    ctx->r4 = (gpr)(int32_t)rs64_s6893_tilepool_size(U32(ctx->r4)); /* %s */\n" % TAG
for a, b in ((A1, A1 + SZ), (A2, A2 + SZ), (W, W + "    ctx->r3 = (gpr)(int32_t)rs64_s6893_tileslot(U32(ctx->r3)); /* %s */\n" % TAG)):
    assert t.count(a) >= 1, a
    t = t.replace(a, b, 1)
assert t.count(HEAD) == 1
t = t.replace(HEAD, DECL + HEAD, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
