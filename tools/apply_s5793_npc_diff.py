"""s5793: under ROGUESQ_LOG_HUDBIT, at updateDestructionDebrisNpc ENTRY log (msg a1, NPC words 0..24 diff vs the previous entry) for NPCs whose
descriptor +0x70 == 2 (counter-2 class). Names the message/word flip preceding destruction. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5793 npc diff"
ANC = "    ctx->r17 = MEM_W(ctx->r21, 0X4);\n"
B = ('    { static int s_e = -1, s_b = 0; static uint32_t s_n[8], s_w[8][24]; static int s_c = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
     'if (s_e && s_b < 400) { uint32_t n = U32(ctx->r17); uint32_t d = (n >> 24) == 0x80 ? (uint32_t)MEM_W(ctx->r17, 0X34) : 0; '
     'if (d >= 0x80300000u && d < 0x80330000u && (uint32_t)MEM_W(S32((int32_t)d), 0X70) == 2) { int k = -1; for (int i = 0; i < s_c; i++) if (s_n[i] == n) k = i; '
     'if (k < 0 && s_c < 8) { k = s_c++; s_n[k] = n; for (int q = 0; q < 24; q++) s_w[k][q] = 0xDEADBEEF; } '
     'if (k >= 0) { int ch = 0; for (int q = 0; q < 24; q++) if ((uint32_t)MEM_W(ctx->r17, q * 4) != s_w[k][q]) ch = 1; '
     'unsigned msg = (unsigned)(ctx->r5 & 0xFFFF); if (ch || msg == 5 || (msg != 3 && msg != 4 && msg != 11)) { s_b++; struct { long s; int us; } tv; extern int gettimeofday(void*, void*); gettimeofday(&tv, 0); '
     'fprintf(stderr, "[npcd] npc=%08x desc=%08x msg=%u t=%.0fms", n, d, msg, (double)(tv.s % 100000) * 1000.0 + tv.us / 1000.0); if (msg == 5 && ((uint32_t)ctx->r6 >> 24) == 0x80) { uint32_t df = (uint32_t)MEM_W(S32((int32_t)0x80137CE4u), 0); fprintf(stderr, " a0=%08x pl=%08x diff=%u hp=%d:", (unsigned)ctx->r4, (unsigned)ctx->r6, df, (df < 4) ? (int)MEM_W(S32((int32_t)(d + 0x6C + df * 4)), 0) : -99); for (int q = 0; q < 8; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(S32((int32_t)((uint32_t)ctx->r6 + q * 4)), 0)); fprintf(stderr, " |"); { static int s_bt[8]; if (s_bt[k] < 2) { s_bt[k]++; fprintf(stderr, "\\n"); extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); void* bt[16]; int nb = backtrace(bt, 16); backtrace_symbols_fd(bt, nb, 2); } } } '
     'for (int q = 0; q < 24; q++) { uint32_t w = (uint32_t)MEM_W(ctx->r17, q * 4); if (w != s_w[k][q]) fprintf(stderr, " [%d]%08x>%08x", q, s_w[k][q], w); s_w[k][q] = w; } fprintf(stderr, "\\n"); } } } } } /* ' + T + ' */\n')
def apply(text, name=None):
    n = 0
    i = text.find("RECOMP_FUNC void updateDestructionDebrisNpc(")
    if i >= 0 and T not in text:
        j = text.find(ANC, i)
        if j >= 0: k = j + len(ANC); text = text[:k] + B + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_16.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_16.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5793_npc_diff" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_16.c":\n'
               '        import apply_s5793_npc_diff as _a5793\n'
               '        text, _n5793 = _a5793.apply(text)\n'
               '        if _n5793:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5793 npc diff x{_n5793}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5792_npc_victim.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5793_npc_diff.py",\n', 1)
        fp.write_text(s); print("fixup patched")
