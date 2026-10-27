"""s6493 G1c: exit/skip counters g_s6493[16] in streamTerrainGridCellsByDistance (funcs_9.c), printed as [streamcum].
[0] entries [1] early-out z-depth<=0 [2] x-width<=0 row skip [3] pool-cap row break [4] beq span-equal cell skip
[5] +3 range branch (->0x7F store) [6] +4 branch to DC4 [7] spanbound skip DB4 [8] spanbound skip DC0 [9] node+0x14==0 no-node
[10] empty return [11] nonempty return [12] sum z-depth [13] sum x-width. Idempotent."""
import pathlib
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
TAG = "PATCH: s6493 streamcum"
if TAG in t: print("already"); raise SystemExit
def rep(old, new, expect=1):
    global t
    assert t.count(old) == expect, (old[:60], t.count(old))
    t = t.replace(old, new)
rep("uint32_t g_s6492[12];", "uint32_t g_s6493[16]; uint32_t g_s6492[12];")
S = "RECOMP_FUNC void streamTerrainGridCellsByDistance(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
rep(S, S + "    g_s6493[0]++; g_s6493[12] += (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80132DBC); g_s6493[13] += (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80132DB4); /* " + TAG + " */\n")
# early-out
rep("    if (SIGNED(ctx->r14) <= 0) {\n        // 0x80042CDC: addu        $fp, $zero, $zero\n        ctx->r30 = ADD32(0, 0);\n            goto L_80043138;",
    "    if (SIGNED(ctx->r14) <= 0) {\n        g_s6493[1]++; /* " + TAG + " */\n        // 0x80042CDC: addu        $fp, $zero, $zero\n        ctx->r30 = ADD32(0, 0);\n            goto L_80043138;")
rep("    // 0x80042D14: blez        $t6, L_80043070\n    if (SIGNED(ctx->r14) <= 0) {", "    // 0x80042D14: blez        $t6, L_80043070\n    if (SIGNED(ctx->r14) <= 0) {\n        g_s6493[2]++; /* " + TAG + " */")
rep("    // 0x80042DE0: beq         $v0, $zero, L_80043070\n    if (ctx->r2 == 0) {", "    // 0x80042DE0: beq         $v0, $zero, L_80043070\n    if (ctx->r2 == 0) {\n        g_s6493[3]++; /* " + TAG + " */")
rep("    // 0x80042D64: beq         $v0, $a0, L_80043020\n    if (ctx->r2 == ctx->r4) {", "    // 0x80042D64: beq         $v0, $a0, L_80043020\n    if (ctx->r2 == ctx->r4) {\n        g_s6493[4]++; /* " + TAG + " */")
rep("    // 0x80042D90: bne         $v0, $zero, L_80042DB0\n    if (ctx->r2 != 0) {", "    // 0x80042D90: bne         $v0, $zero, L_80042DB0\n    if (ctx->r2 != 0) {\n        g_s6493[5]++; /* " + TAG + " */")
rep("    // 0x80042DA8: beq         $v0, $zero, L_80042DC4\n    if (ctx->r2 == 0) {", "    // 0x80042DA8: beq         $v0, $zero, L_80042DC4\n    if (ctx->r2 == 0) {\n        g_s6493[6]++; /* " + TAG + " */")
rep('{ if (n6049++ < 8) fprintf(stderr, "[spanbound] skip addr=0x%08X pc=0x80042DB4', '{ g_s6493[7]++; if (n6049++ < 8) fprintf(stderr, "[spanbound] skip addr=0x%08X pc=0x80042DB4', 1)
rep('{ if (n6049++ < 8) fprintf(stderr, "[spanbound] skip addr=0x%08X pc=0x80042DC0', '{ g_s6493[8]++; if (n6049++ < 8) fprintf(stderr, "[spanbound] skip addr=0x%08X pc=0x80042DC0', 2)
rep("    // 0x80042EA8: bne         $v0, $zero, L_80042EC8\n    if (ctx->r2 != 0) {", "    // 0x80042EA8: bne         $v0, $zero, L_80042EC8\n    if (ctx->r2 != 0) {", 1)
rep("    // 0x80042EA4: lw          $v0, 0x14($s0)\n    ctx->r2 = MEM_W(ctx->r16, 0X14);\n", "    // 0x80042EA4: lw          $v0, 0x14($s0)\n    ctx->r2 = MEM_W(ctx->r16, 0X14); if (ctx->r2 == 0) g_s6493[9]++; /* " + TAG + " */\n")
rep("    // 0x80043170: addu        $v0, $t1, $zero\n    ctx->r2 = ADD32(ctx->r9, 0);\n    // 0x80043174: jr          $ra\n    // 0x80043178: addiu       $sp, $sp, 0x80\n    ctx->r29 = ADD32(ctx->r29, 0X80);\n    return;",
    "    // 0x80043170: addu        $v0, $t1, $zero\n    ctx->r2 = ADD32(ctx->r9, 0); g_s6493[ctx->r2 ? 11 : 10]++; /* " + TAG + " */\n    // 0x80043174: jr          $ra\n    // 0x80043178: addiu       $sp, $sp, 0x80\n    ctx->r29 = ADD32(ctx->r29, 0X80);\n    return;")
p.write_text(t); print("ok")
