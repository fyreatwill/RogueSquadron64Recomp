"""s5847: at requestMissionTransitionMode / setHudEnableBit4 / setHudEnableBit8 entry (funcs_42/funcs_35), log a0, mask 0x8010C9E0,
objective counters get(1),get(2),get(10) (0x8013805C+4n), vi and the first 3 backtraces. Under ROGUESQ_LOG_HUDBIT: [m47] lines."""
def _line(name):
    return ('    { /* PATCH: s5847 %s */ static int e_ = -1, n_ = 0; if (e_ < 0) { const char* v_ = getenv("ROGUESQ_LOG_HUDBIT"); e_ = (v_ && v_[0]) ? 1 : 0; } '
            'if (e_ && n_++ < 60) { extern volatile uint32_t rs64_vi_n_g; fprintf(stderr, "[m47] fn=%s n=%%d a0=%%u a1=%%u mask=%%08X c1=%%d c2=%%d c10=%%d ph=%%u fl=%%08X vi=%%u\\n", n_, U32(ctx->r4), U32(ctx->r5), '
            '(uint32_t)MEM_W((int32_t)0x8010C9E0, 0), (int)MEM_W((int32_t)0x8013805C + 4, 0), (int)MEM_W((int32_t)0x8013805C + 8, 0), (int)MEM_W((int32_t)0x8013805C + 40, 0), '
            '(uint32_t)MEM_W((int32_t)0x8010CA20, 0), (uint32_t)MEM_W((int32_t)0x8010CA1C, 0), rs64_vi_n_g); '
            'if (n_ <= 3) { extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); void* bt_[24]; int nb_ = backtrace(bt_, 24); backtrace_symbols_fd(bt_, nb_, 2); } } }\n') % (name, name)
def apply(text):
    n = 0
    for name in ("requestMissionTransitionMode", "setHudEnableBit4", "setHudEnableBit8"):
        tag = "PATCH: s5847 " + name
        sig = "RECOMP_FUNC void %s(" % name
        i = text.find(sig)
        if i < 0 or tag in text: continue
        j = text.find("    int c1cs = 0;\n", i); assert 0 < j - i < 400, name
        j += len("    int c1cs = 0;\n"); text = text[:j] + _line(name) + text[j:]; n += 1
    return text, n
if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        t = open(f).read(); t2, k = apply(t)
        if k: open(f, "w").write(t2)
        print(f, k)
