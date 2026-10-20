"""s5667: env-gated (ROGUESQ_LOG_HUDBIT=1) entry/exit log for runVoiceLatticeFilter (0x8009D980).
The filter is PURE INTEGER fixed-point (mult/sra15, no FPU) so float-lowering (H8) is moot. Entry: input ptr t1(r9), out ptr t0(r8),
count t3(r11), coefficient pairs t9/t8/t7/t6 (r25/r24/r15/r14), state s7..s0 (r23..r16), a3 (r7), first 8 input s16.
Exit: out count, #rail samples (0x8000/0x7FF8 after the &0xFFF8), first 8 output s16, final state. Control: any call at all and
any non-rail output sample. First 40 calls + every 500th. Idempotent."""
import re
TAG = "PATCH: s5667 lattice log"
EN = '{ static int s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } if (s_e)'
ENTRY = ('    uint32_t s5667_o = U32(ctx->r8); int s5667_n = (int)ctx->r11 + 1; int s5667_log = 0; /* %s */\n'
         '    %s { static int s_c = 0; s_c++; s5667_log = (s_c <= 40 || (s_c %% 500) == 0); if (s5667_log) { '
         'fprintf(stderr, "[lat-in] c=%%d in=0x%%X out=0x%%X n=%%d coef t9=%%08X t8=%%08X t7=%%08X t6=%%08X st s7=%%d s6=%%d s5=%%d s4=%%d s3=%%d s2=%%d s1=%%d s0=%%d a3=%%d x[0..7]=", '
         's_c, U32(ctx->r9), s5667_o, s5667_n, U32(ctx->r25), U32(ctx->r24), U32(ctx->r15), U32(ctx->r14), (int)S32(ctx->r23), (int)S32(ctx->r22), '
         '(int)S32(ctx->r21), (int)S32(ctx->r20), (int)S32(ctx->r19), (int)S32(ctx->r18), (int)S32(ctx->r17), (int)S32(ctx->r16), (int)S32(ctx->r7)); '
         'for (int i = 0; i < 8; i++) fprintf(stderr, "%%d ", (int)(int16_t)MEM_HU(2 * i, ctx->r9)); fprintf(stderr, "\\n"); } } } /* %s */\n' % (TAG, EN, TAG))
EXIT = ('    if (s5667_log) { int rails = 0, nz = 0; for (int i = 0; i < s5667_n; i++) { int v = (int)(int16_t)MEM_HU(2 * i, (int32_t)s5667_o); '
        'if (v == -32768 || v == 32760) rails++; else if (v != 0) nz++; } fprintf(stderr, "[lat-out] n=%%d rails=%%d nonrail_nonzero=%%d y[0..7]=", s5667_n, rails, nz); '
        'for (int i = 0; i < 8; i++) fprintf(stderr, "%%d ", (int)(int16_t)MEM_HU(2 * i, (int32_t)s5667_o)); fprintf(stderr, "\\n"); } /* %s */\n' % TAG)
def apply(text):
    out, n = [], 0
    for part in re.split(r'(?m)^(?=RECOMP_FUNC void )', text):
        if part.startswith("RECOMP_FUNC void runVoiceLatticeFilter(") and TAG not in part[:6000]:
            j = part.find("{\n") + 2
            part = part[:j] + ENTRY + part[j:]
            part, k = re.subn(r'(?m)^(    return;\n)', lambda m: EXIT + m.group(1), part, count=1)
            n += 1 if k else 0
        out.append(part)
    return "".join(out), n
if __name__ == "__main__":
    import pathlib
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c"); t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print(p.name, n)
