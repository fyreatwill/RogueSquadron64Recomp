"""s6595: witness the generated loads and TLUT return that feed the phase-7 HUD pointer."""
from pathlib import Path

MARK = "PATCH: s6595 hudptrread"
RET_MARK = "PATCH: s6595 hudptrret"
ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")

HELPER = r'''/* PATCH: s6595 hudptrread helper */
extern uint32_t rs64_phase_ord(void);
extern uint32_t rs64_vi_committed_origin(void);
void s6595_hudptr_read(uint8_t* rdram, recomp_context* ctx, uint32_t pc,
                              uint32_t source, uint32_t value, uint32_t deref,
                              uint32_t s0, const char* stage) {
    static int en = -1;
    static unsigned n;
    if (en < 0) { const char* e = getenv("ROGUESQ_HUDPTRWATCH"); en = (e && e[0] && e[0] != '0') ? 1 : 0; }
    if (!en || n >= 500) return;
    fprintf(stderr, "[hudptrr] n=%u stage=%s pc=%08X src=%08X val=%08X deref=%08X s0=%08X ra=%08X phase=%u vi_origin=%06X\n",
        ++n, stage, pc, source, value, deref, s0, (uint32_t)ctx->r31,
        rs64_phase_ord(), rs64_vi_committed_origin() & 0x00FFFFFFu);
    fflush(stderr);
    (void)rdram;
}

void s6595_hudptr_ret(uint8_t* rdram, recomp_context* ctx, uint32_t pc,
                            uint32_t value, uint32_t source, const char* stage) {
    static unsigned n;
    const char* e = getenv("ROGUESQ_HUDPTRWATCH");
    if (!e || !e[0] || e[0] == '0' || n >= 500) return;
    fprintf(stderr, "[hudptrr] n=%u stage=%s pc=%08X src=%08X val=%08X ra=%08X phase=%u vi_origin=%06X\n",
        ++n, stage, pc, source, value, (uint32_t)ctx->r31,
        rs64_phase_ord(), rs64_vi_committed_origin() & 0x00FFFFFFu);
    fflush(stderr);
    (void)rdram;
}
'''

def patch_handler() -> int:
    p = ROOT / "funcs_13.c"
    t = p.read_text()
    if "void s6595_hudptr_ret" in t:
        return 0
    anchor = "/* PATCH: s6593 hudptrwatch handler */\n"
    if anchor not in t:
        raise SystemExit("s6593 handler anchor missing")
    t = t.replace(anchor, HELPER + anchor, 1)
    p.write_text(t)
    return 1

def patch_worker() -> int:
    p = ROOT / "funcs_10.c"
    t = p.read_text()
    changed = 0
    decl = '#include "funcs.h"\n'
    if decl not in t:
        raise SystemExit("funcs.h include anchor missing")
    if "extern void s6595_hudptr_ret" not in t:
        t = t.replace(decl, decl + "extern void s6595_hudptr_read(uint8_t*, recomp_context*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, const char*);\nextern void s6595_hudptr_ret(uint8_t*, recomp_context*, uint32_t, uint32_t, uint32_t, const char*); /* " + RET_MARK + " */\n", 1)
        changed = 1
    old1 = "    // 0x80049644: lw          $v0, 0x14($s0)\n    ctx->r2 = MEM_W(ctx->r16, 0X14);\n"
    new1 = old1 + "    s6595_hudptr_read(rdram, ctx, 0x80049644u, U32(ADD32(ctx->r16, 0X14)), U32(ctx->r2), U32(ADD32(ctx->r2, 4)), U32(ctx->r16), \"material\"); /* " + MARK + " */\n"
    old2 = "    // 0x80049654: lw          $v1, 0x14($s0)\n    ctx->r3 = MEM_W(ctx->r16, 0X14);\n"
    new2 = old2 + "    s6595_hudptr_read(rdram, ctx, 0x80049654u, U32(ADD32(ctx->r16, 0X14)), U32(ctx->r3), U32(ADD32(ctx->r3, 6)), U32(ctx->r16), \"tlut\"); /* " + MARK + " */\n"
    if old1 not in t or old2 not in t:
        raise SystemExit("hud worker load anchors missing")
    if "s6595_hudptr_read(rdram, ctx, 0x80049644u" not in t:
        t = t.replace(old1, new1, 1)
    if "s6595_hudptr_read(rdram, ctx, 0x80049654u" not in t:
        t = t.replace(old2, new2, 1)
    old3 = "    ctx->r17 = ADD32(ctx->r2, 0);\n    after_2:\n"
    new3 = "    ctx->r17 = ADD32(ctx->r2, 0);\n    s6595_hudptr_ret(rdram, ctx, 0x80049660u, U32(ctx->r17), U32(ctx->r3), \"tlut_return\"); /* " + MARK + " */\n    after_2:\n"
    if "s6595_hudptr_ret(rdram, ctx, 0x80049660u" not in t and old3 not in t:
        raise SystemExit("hud worker TLUT return anchor missing")
    if "s6595_hudptr_ret(rdram, ctx, 0x80049660u" not in t:
        t = t.replace(old3, new3, 1)
        changed = 1
    p.write_text(t)
    return changed

print("s6595 patched", patch_handler() + patch_worker(), "files")
