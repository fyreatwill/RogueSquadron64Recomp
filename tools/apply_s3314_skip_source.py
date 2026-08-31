#!/usr/bin/env python3
"""Keep the s3314 cinematic skip-allow source census in generated funcs_27.c."""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c")
MARK = "PATCH: s3314 skip source"

HELPER = r'''/* PATCH: s3314 skip source */
static void rs64_s3314_skip_source(uint32_t pc, uint32_t v0, uint32_t a0,
                                   uint32_t value, uint32_t ra) {
    static int enabled = -1;
    static unsigned long n;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_CINE_INIT_JAL");
        const char* a = getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') || (a && a[0] && a[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    if (++n <= 32ul || (n % 100ul) == 0ul) {
        extern uint32_t rs64_phase_ord(void);
        extern uint32_t rs64_vi_committed_width(void);
        extern uint32_t rs64_vi_committed_origin(void);
        fprintf(stderr, "[s3314-skip-source] phase=%u width=%u origin=0x%06X pc=0x%08X v0=0x%08X a0=0x%08X value=0x%08X ra=0x%08X n=%lu\n",
                rs64_phase_ord(), rs64_vi_committed_width(),
                rs64_vi_committed_origin() & 0x00FFFFFFu, pc, v0, a0, value, ra, n);
        fflush(stderr);
    }
}

'''

def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: anchor count={count}")
    return text.replace(old, new, 1)

def main():
    text = GEN.read_text()
    if MARK in text:
        print("s3314 skip source already present")
        return
    decl = "RECOMP_FUNC void cinematicLoopBody(uint8_t* rdram, recomp_context* ctx) {\n"
    text = once(text, decl, HELPER + decl, "declaration")
    text = once(text,
        "    // 0x800A6208: andi        $v0, $v0, 0x9000\n"
        "    ctx->r2 = ctx->r2 & 0X9000;\n",
        "    // 0x800A6208: andi        $v0, $v0, 0x9000\n"
        "    ctx->r2 = ctx->r2 & 0X9000;\n"
        "    rs64_s3314_skip_source(0x800A6208u, U32(ctx->r2), U32(ctx->r4), U32(ctx->r2), U32(ctx->r31));\n",
        "6208")
    text = once(text,
        "    // 0x800A6238: bne         $v0, $zero, L_800A6250\n"
        "    if (ctx->r2 != 0) {\n",
        "    // 0x800A6238: bne         $v0, $zero, L_800A6250\n"
        "    rs64_s3314_skip_source(0x800A6238u, U32(ctx->r2), U32(ctx->r4), U32(ctx->r2), U32(ctx->r31));\n"
        "    if (ctx->r2 != 0) {\n",
        "6238")
    text = once(text,
        "    // 0x800A6248: beq         $v0, $zero, L_800A6254\n"
        "    if (ctx->r2 == 0) {\n",
        "    // 0x800A6248: beq         $v0, $zero, L_800A6254\n"
        "    rs64_s3314_skip_source(0x800A6248u, U32(ctx->r2), U32(ctx->r4), U32(ctx->r2), U32(ctx->r31));\n"
        "    if (ctx->r2 == 0) {\n",
        "6248")
    old = "    MEM_B(0XB1C, ctx->r3) = ctx->r2;\n"
    new = "    rs64_s3314_skip_source(0x800A9360u, U32(ctx->r2), U32(ctx->r4), U32(ctx->r2), U32(ctx->r31));\n" + old
    count = text.count(old)
    if count != 2:
        raise RuntimeError(f"9360: anchor count={count}")
    text = text.replace(old, new)
    GEN.write_text(text)
    print(f"patched {GEN}: s3314 source probes 6208/6238/6248/9360")

if __name__ == "__main__":
    main()
