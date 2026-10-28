"""s6595: witness the generated loads that produce the phase-7 HUD pointer."""
from pathlib import Path

MARK = "PATCH: s6595 hudptrread"
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
'''

def patch_handler() -> int:
    p = ROOT / "funcs_13.c"
    t = p.read_text()
    if MARK in t:
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
    if MARK in t:
        return 0
    decl = '#include "funcs.h"\n'
    if decl not in t:
        raise SystemExit("funcs.h include anchor missing")
    t = t.replace(decl, decl + "extern void s6595_hudptr_read(uint8_t*, recomp_context*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, const char*); /* " + MARK + " */\n", 1)
    old1 = "    // 0x80049644: lw          $v0, 0x14($s0)\n    ctx->r2 = MEM_W(ctx->r16, 0X14);\n"
    new1 = old1 + "    s6595_hudptr_read(rdram, ctx, 0x80049644u, U32(ADD32(ctx->r16, 0X14)), U32(ctx->r2), U32(ADD32(ctx->r2, 4)), U32(ctx->r16), \"material\"); /* " + MARK + " */\n"
    old2 = "    // 0x80049654: lw          $v1, 0x14($s0)\n    ctx->r3 = MEM_W(ctx->r16, 0X14);\n"
    new2 = old2 + "    s6595_hudptr_read(rdram, ctx, 0x80049654u, U32(ADD32(ctx->r16, 0X14)), U32(ctx->r3), U32(ADD32(ctx->r3, 6)), U32(ctx->r16), \"tlut\"); /* " + MARK + " */\n"
    if old1 not in t or old2 not in t:
        raise SystemExit("hud worker load anchors missing")
    t = t.replace(old1, new1, 1).replace(old2, new2, 1)
    p.write_text(t)
    return 1

print("s6595 patched", patch_handler() + patch_worker(), "files")
