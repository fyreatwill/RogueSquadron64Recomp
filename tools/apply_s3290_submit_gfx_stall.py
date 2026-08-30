#!/usr/bin/env python3
"""Inject s3290 submitGfxFrame jal-stall census into funcs_3.c.

Sites: entry of every jal inside submitGfxFrame (23) plus return of the
seven recv/yield/send sites. Keep s3288 fade and s3289 SENT/SRET.
Diagnostic only — no skip, allow, restore, or wait bypass.

This patches an already-sentinel'd RecompiledFuncs/funcs_3.c without
re-running the full fixup. The same transform lives in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c")
MARK = "PATCH: s3290 submit stall"

HELPER = r'''
static void rs64_s3290_submit_stall(const char* site, int idx, int is_ret, int is_7,
                                    uint32_t saved_ra, uint32_t a0, uint32_t a1, uint32_t a2) {
    static unsigned long n[30];
    static const char* open7 = "";
    static unsigned long open7_n = 0;
    static unsigned long viewer_sub = 0;
    static int armed = 0;
    unsigned long c;
    int viewer;
    int miss;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    viewer = (saved_ra == 0x800C2D98u) ? 1 : 0;
    if (!is_ret && site[1] == '0' && site[2] == '8' && site[3] == '8' && viewer) {
        ++viewer_sub;
        if (viewer_sub >= 3ul) armed = 1;
    }
    miss = 0;
    if (is_ret) {
        if (open7[0] && open7[1] == site[1] && open7[2] == site[2] && open7[3] == site[3]) {
            open7 = "";
            open7_n = 0;
        } else if (open7[0]) {
            miss = 1;
        }
    } else {
        if (open7[0]) miss = 1;
        if (is_7) {
            open7 = site;
        }
    }
    c = ++n[idx];
    if (is_7 && !is_ret) open7_n = c;
    {
        uint32_t width = rs64_vi_committed_width();
        if (!miss && width < 640u && c > 10ul && (c % 50ul) != 0ul) return;
        fprintf(stderr,
                "[s3290-stall] site=%s n=%lu open7=%s open7_n=%lu miss=%d viewer=%d vsub=%lu armed=%d ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X phase=%u width=%u origin=0x%06X\n",
                site, c, open7[0] ? open7 : "-", open7_n, miss, viewer, viewer_sub, armed,
                saved_ra, a0, a1, a2,
                rs64_phase_ord(), width,
                rs64_vi_committed_origin() & 0x00FFFFFFu);
    }
    fflush(stderr);
}
'''

FUNC_OLD = "RECOMP_FUNC void submitGfxFrame(uint8_t* rdram, recomp_context* ctx) {\n"

PROBE = (
    "    {{ /* PATCH: s3290 submit stall */\n"
    "        rs64_s3290_submit_stall(\"{site}\", {idx}, {is_ret}, {is_7},\n"
    "                                U32(MEM_W(0X40, ctx->r29)), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6));\n"
    "    }}\n"
)

# (old, site, idx, is_ret, is_7) — old is the unique pre-call or post-after block
# is_ret 0 = insert BEFORE the first line that is the call (old includes the call)
# We replace `old` with probe+old for entries, and after_label+\n+probe+rest for returns.

ENTRIES = [
    (
        "    // 0x8000C088: jal         0x80023D08\n"
        "    // 0x8000C08C: sw          $s0, 0x38($sp)\n"
        "    rs64_m5_writer_parity('W', 0x8000C08Cu, U32(ADD32(ctx->r29, 0X38)), 0u); /* PATCH: s2190 m5 scalar */\n"
        "    rs64_probe_submit_gate_store('W', 0x8000C08Cu, U32(ADD32(ctx->r29, 0X38)), U32(ctx->r16));\n"
        "    MEM_W(0X38, ctx->r29) = ctx->r16;\n"
        "    getTimeSinceLastFrame(rdram, ctx);\n",
        "E088", 0, 0, 0,
        "    getTimeSinceLastFrame(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C0B4: jal         0x800331D0\n"
        "    // 0x8000C0B8: addiu       $a2, $zero, 0x1\n"
        "    ctx->r6 = ADD32(0, 0X1);\n"
        "    osRecvMesg_recomp(rdram, ctx);\n",
        "E0B4", 1, 0, 1,
        "    osRecvMesg_recomp(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C0BC: jal         0x8001A018\n"
        "    // 0x8000C0C0: nop\n"
        "\n"
        "    yieldFromSpThread(rdram, ctx);\n",
        "E0BC", 2, 0, 1,
        "    yieldFromSpThread(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C0C4: jal         0x8001BEC8\n"
        "    // 0x8000C0C8: addu        $s0, $zero, $zero\n"
        "    ctx->r16 = ADD32(0, 0);\n"
        "    bufferArbiterMarkSlotReady(rdram, ctx);\n",
        "E0C4", 3, 0, 0,
        "    bufferArbiterMarkSlotReady(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C0CC: jal         0x8000815C\n"
        "    // 0x8000C0D0: nop\n"
        "\n"
        "    drainMeshReleaseQueue(rdram, ctx);\n",
        "E0CC", 4, 0, 0,
        "    drainMeshReleaseQueue(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C0F0: jal         0x80008550\n"
        "    // 0x8000C0F4: addiu       $s1, $s1, 0x4\n"
        "    ctx->r17 = ADD32(ctx->r17, 0X4);\n"
        "    commitMeshDrawBatchRefs(rdram, ctx);\n",
        "E0F0", 5, 0, 0,
        "    commitMeshDrawBatchRefs(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C13C: jal         0x8001BF20\n"
        "    // 0x8000C140: addiu       $a0, $zero, 0x1\n"
        "    ctx->r4 = ADD32(0, 0X1);\n"
        "    bufferArbiterAllocSlot(rdram, ctx);\n",
        "E13C", 6, 0, 0,
        "    bufferArbiterAllocSlot(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C150: jal         0x80019BE4\n"
        "    // 0x8000C154: nop\n"
        "\n"
        "    getInactiveBufferIndex(rdram, ctx);\n",
        "E150", 7, 0, 0,
        "    getInactiveBufferIndex(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C200: jal         0x80035930\n"
        "    // 0x8000C204: nop\n"
        "\n"
        "    osWritebackDCacheAll_recomp(rdram, ctx);\n",
        "E200", 8, 0, 0,
        "    osWritebackDCacheAll_recomp(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C2A0: jal         0x80033410\n"
        "    // 0x8000C2A4: addu        $a2, $zero, $zero\n"
        "    ctx->r6 = ADD32(0, 0);\n"
        "    osSendMesg_recomp(rdram, ctx);\n",
        "E2A0", 9, 0, 1,
        "    osSendMesg_recomp(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C2B8: jal         0x800331D0\n"
        "    // 0x8000C2BC: addiu       $a2, $zero, 0x1\n"
        "    ctx->r6 = ADD32(0, 0X1);\n"
        "    osRecvMesg_recomp(rdram, ctx);\n",
        "E2B8", 10, 0, 1,
        "    osRecvMesg_recomp(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C2C0: jal         0x8001A038\n"
        "    // 0x8000C2C4: nop\n"
        "\n"
        "    yieldFromGfxFrame(rdram, ctx);\n",
        "E2C0", 11, 0, 1,
        "    yieldFromGfxFrame(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C2C8: jal         0x8002B590\n"
        "    // 0x8000C2CC: addiu       $a0, $sp, 0x10\n"
        "    ctx->r4 = ADD32(ctx->r29, 0X10);\n"
        "    osDpGetCounters_recomp(rdram, ctx);\n",
        "E2C8", 12, 0, 0,
        "    osDpGetCounters_recomp(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C438: jal         0x8002B5E0\n"
        "    // 0x8000C43C: addiu       $a0, $zero, 0x1C0\n"
        "    ctx->r4 = ADD32(0, 0X1C0);\n"
        "    osDpSetStatus_recomp(rdram, ctx);\n",
        "E438", 13, 0, 0,
        "    osDpSetStatus_recomp(rdram, ctx);\n",
    ),
    (
        "    rs64_m5_producer_mark_handoff(rdram, 2u, 0x8000C440u, U32(ctx->r16), U32(ctx->r17), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r2)); /* PATCH: s3092 producer-mark callsites */\n"
        "    bufferArbiterProducerMark(rdram, ctx);\n",
        "E440", 14, 0, 0,
        "    bufferArbiterProducerMark(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C4A8: jal         0x800331D0\n"
        "    // 0x8000C4AC: addiu       $a2, $zero, 0x1\n"
        "    ctx->r6 = ADD32(0, 0X1);\n"
        "    osRecvMesg_recomp(rdram, ctx);\n",
        "E4A8", 15, 0, 1,
        "    osRecvMesg_recomp(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C4B0: jal         0x8001A038\n"
        "    // 0x8000C4B4: nop\n"
        "\n"
        "    yieldFromGfxFrame(rdram, ctx);\n",
        "E4B0", 16, 0, 1,
        "    yieldFromGfxFrame(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C4B8: jal         0x8002B590\n"
        "    // 0x8000C4BC: addiu       $a0, $sp, 0x10\n"
        "    ctx->r4 = ADD32(ctx->r29, 0X10);\n"
        "    osDpGetCounters_recomp(rdram, ctx);\n",
        "E4B8", 17, 0, 0,
        "    osDpGetCounters_recomp(rdram, ctx);\n",
    ),
    (
        "    rs64_m5_route_candidate(rdram, 0x8001BCE4u, U32(ctx->r31), U32(ctx->r16), U32(ctx->r17), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r2)); /* PATCH: s2993 producer-mark c628 handoff */\n"
        "    bufferArbiterProducerMark(rdram, ctx);\n",
        "E628", 18, 0, 0,
        "    bufferArbiterProducerMark(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C630: jal         0x8001C244\n"
        "    // 0x8000C634: nop\n"
        "\n"
        "    setPostSwapPendingFlags(rdram, ctx);\n",
        "E630", 19, 0, 0,
        "    setPostSwapPendingFlags(rdram, ctx);\n",
    ),
    (
        "    rs64_m5_producer_mark_handoff(rdram, 2u, 0x8000C64Cu, U32(ctx->r16), U32(ctx->r17), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r2)); /* PATCH: s3092 producer-mark callsites */\n"
        "    bufferArbiterProducerMark(rdram, ctx);\n",
        "E64C", 20, 0, 0,
        "    bufferArbiterProducerMark(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C654: jal         0x80000C50\n"
        "    // 0x8000C658: nop\n"
        "\n"
        "    isPreNmiPending(rdram, ctx);\n",
        "E654", 21, 0, 0,
        "    isPreNmiPending(rdram, ctx);\n",
    ),
    (
        "    // 0x8000C6CC: jal         0x80023CC0\n"
        "    // 0x8000C6D0: nop\n"
        "\n"
        "    recordFrameTimestamp(rdram, ctx);\n",
        "E6CC", 22, 0, 0,
        "    recordFrameTimestamp(rdram, ctx);\n",
    ),
]

RETURNS = [
    (
        "    after_1:\n"
        "    // 0x8000C0BC: jal         0x8001A018\n",
        "R0B4", 23, 1, 1,
    ),
    (
        "    after_2:\n"
        "L_8000C0C4:\n",
        "R0BC", 24, 1, 1,
    ),
    (
        "    after_9:\n"
        "    // 0x8000C2A8: beq         $s1, $zero, L_8000C2C8\n",
        "R2A0", 25, 1, 1,
    ),
    (
        "    after_10:\n"
        "    // 0x8000C2C0: jal         0x8001A038\n",
        "R2B8", 26, 1, 1,
    ),
    (
        "    after_11:\n"
        "L_8000C2C8:\n",
        "R2C0", 27, 1, 1,
    ),
    (
        "    after_15:\n"
        "    // 0x8000C4B0: jal         0x8001A038\n",
        "R4A8", 28, 1, 1,
    ),
    (
        "    after_16:\n"
        "L_8000C4B8:\n",
        "R4B0", 29, 1, 1,
    ),
]


def _probe(site, idx, is_ret, is_7):
    return PROBE.format(site=site, idx=idx, is_ret=is_ret, is_7=is_7)


def apply_s3290_submit_gfx_stall_text(text: str):
    if MARK in text:
        return text, ["funcs_3.c: s3290 submit stall already present"], False
    n = text.count(FUNC_OLD)
    if n != 1:
        raise RuntimeError(f"s3290 submitGfxFrame count={n}")
    text = text.replace(FUNC_OLD, HELPER + "\n" + FUNC_OLD, 1)
    patched = 0
    for old, site, idx, is_ret, is_7, call in ENTRIES:
        c = text.count(old)
        if c != 1:
            raise RuntimeError(f"s3290 entry {site} count={c} for {old[:80]!r}")
        probe = _probe(site, idx, is_ret, is_7)
        # insert probe immediately before the call line inside `old`
        if call not in old:
            raise RuntimeError(f"s3290 entry {site} missing call {call!r}")
        new = old.replace(call, probe + call, 1)
        text = text.replace(old, new, 1)
        patched += 1
    for old, site, idx, is_ret, is_7 in RETURNS:
        c = text.count(old)
        if c != 1:
            raise RuntimeError(f"s3290 return {site} count={c} for {old[:80]!r}")
        probe = _probe(site, idx, is_ret, is_7)
        # insert probe after the first line (the after_N / label line)
        first, rest = old.split("\n", 1)
        new = first + "\n" + probe + rest
        text = text.replace(old, new, 1)
        patched += 1
    return text, [f"funcs_3.c: s3290 submit stall probe patched x{patched}"], True


def main():
    text, msgs, changed = apply_s3290_submit_gfx_stall_text(GEN.read_text())
    for m in msgs:
        print(m)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
