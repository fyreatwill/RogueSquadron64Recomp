// s7739 fixture: head of data_gap_80024A0C as N64Recomp emitted it before s6871 real sizes (live tree until s7739), cut after
// its two s7506-latched jr sites (0x80024A54, 0x80024A64). Used by s7416_ctrl_flow.py S4 latch control when the live tree lacks them.
RECOMP_FUNC void data_gap_80024A0C(uint8_t* rdram, recomp_context* ctx) {
    uint64_t hi = 0, lo = 0, result = 0;
    int c1cs = 0;
    // 0x80024A0C: sw          $a0, 0x18($fp)
    if (__builtin_expect(g_rs64_store_diag, 0)) rs64_m5_writer_parity('W', 0x80024A0Cu, U32(ADD32(ctx->r30, 0X18)), 0u); /* PATCH: s2190 m5 scalar */
    if (__builtin_expect(g_rs64_store_diag, 0)) rs64_probe_submit_gate_store('W', 0x80024A0Cu, U32(ADD32(ctx->r30, 0X18)), U32(ctx->r4));
    { MEM_W(0X18, ctx->r30) = ctx->r4; RS64_S5798_ST(0x80024A0Cu, 0X18, ctx->r30, 4); }
    if (__builtin_expect(g_rs64_store_diag, 0)) { extern void rs64_f5_store_shadow_post(char, uint32_t, uint32_t); rs64_f5_store_shadow_post('W', 0x80024A0Cu, U32(ADD32(ctx->r30, 0X18))); } /* PATCH: s6336 F5 post-store shadow */
    // 0x80024A10: jal         0x8400125C
    // 0x80024A14: ori         $a1, $zero, 0x0
    ctx->r5 = 0 | 0X0;
    LOOKUP_FUNC(0x8400125C)(rdram, ctx);
        goto after_0;
    // 0x80024A14: ori         $a1, $zero, 0x0
    ctx->r5 = 0 | 0X0;
    after_0:
    // 0x80024A18: jal         0x840011E4
    // 0x80024A1C: nop

    LOOKUP_FUNC(0x840011E4)(rdram, ctx);
        goto after_1;
    // 0x80024A1C: nop

    after_1:
L_80024A20:
    // 0x80024A20: mfc0        $v0, Context
    do_break(2147633696);
    // 0x80024A24: lw          $s3, 0x0($s1)
    { RS64_S7484_LD(0x80024A24u, ctx->r17, 0X0, 4); ctx->r19 = MEM_W(ctx->r17, 0X0); }
    // 0x80024A28: lw          $s4, 0x4($s1)
    { RS64_S7484_LD(0x80024A28u, ctx->r17, 0X4, 4); ctx->r20 = MEM_W(ctx->r17, 0X4); }
    // 0x80024A2C: andi        $v0, $v0, 0x80
    ctx->r2 = ctx->r2 & 0X80;
    // 0x80024A30: bne         $v0, $zero, L_80024B38
    if (ctx->r2 != 0) {
        // 0x80024A34: srl         $v0, $s3, 30
        ctx->r2 = S32(U32(ctx->r19) >> 30);
            goto L_80024B38;
    }
    // 0x80024A34: srl         $v0, $s3, 30
    ctx->r2 = S32(U32(ctx->r19) >> 30);
    // 0x80024A38: ori         $v1, $zero, 0x3
    ctx->r3 = 0 | 0X3;
    // 0x80024A3C: beq         $v0, $v1, L_80024A84
    if (ctx->r2 == ctx->r3) {
        // 0x80024A40: addiu       $s1, $s1, 0x8
        ctx->r17 = ADD32(ctx->r17, 0X8);
            goto L_80024A84;
    }
    // 0x80024A40: addiu       $s1, $s1, 0x8
    ctx->r17 = ADD32(ctx->r17, 0X8);
    // 0x80024A44: bne         $v0, $zero, L_80024A58
    if (ctx->r2 != 0) {
        // 0x80024A48: sra         $v0, $s3, 23
        ctx->r2 = S32(SIGNED(ctx->r19) >> 23);
            goto L_80024A58;
    }
    // 0x80024A48: sra         $v0, $s3, 23
    ctx->r2 = S32(SIGNED(ctx->r19) >> 23);
    // 0x80024A4C: andi        $v0, $v0, 0x1FE
    ctx->r2 = ctx->r2 & 0X1FE;
    // 0x80024A50: lhu         $v0, 0xD6($v0)
    { RS64_S7484_LD(0x80024A50u, ctx->r2, 0XD6, 2); ctx->r2 = MEM_HU(ctx->r2, 0XD6); }
    // 0x80024A54: jr          $v0
    gpr jr_target_80024A54 = ctx->r2;
    // 0x80024A58: negu        $v0, $v0
    ctx->r2 = SUB32(0, ctx->r2);
    LOOKUP_FUNC(jr_target_80024A54)(rdram, ctx);
    return;
L_80024A58:
    // 0x80024A58: negu        $v0, $v0
    ctx->r2 = SUB32(0, ctx->r2);
    // 0x80024A5C: andi        $v0, $v0, 0x1FE
    ctx->r2 = ctx->r2 & 0X1FE;
    // 0x80024A60: lhu         $v0, 0x64($v0)
    { RS64_S7484_LD(0x80024A60u, ctx->r2, 0X64, 2); ctx->r2 = MEM_HU(ctx->r2, 0X64); }
    // 0x80024A64: jr          $v0
    gpr jr_target_80024A64 = ctx->r2;
    // 0x80024A68: ori         $v0, $zero, 0x278
    ctx->r2 = 0 | 0X278;
    LOOKUP_FUNC(jr_target_80024A64)(rdram, ctx);
    return;
L_80024A68:
    // 0x80024A68: ori         $v0, $zero, 0x278
    ctx->r2 = 0 | 0X278;
    // 0x80024A6C: bne         $s1, $v0, L_80024A20
    if (ctx->r17 != ctx->r2) {
        // 0x80024A70: ori         $ra, $zero, 0x1088
}
