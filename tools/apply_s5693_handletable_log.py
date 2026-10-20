"""s5693: env-gated (ROGUESQ_LOG_HUDBIT=1) log of the objective-handle table at 0x8010C6E0 (48 x 0x10 bytes):
[hreg]  addBooleanCountHandle entry (a0=handler fn, a1..a3, sp+0x10) -- registrations, cap 300.
[hchk]  checkObjectiveHandles entry: call#, number of active (+0xE==1) entries; first 3 + every 1200th also
        dumps every active entry (handler,+4..+7,+8,+C,+D,+E).
[hfire] just before the jalr at 0x800FA0F0: entry idx (s2) and handler (v0) -- every dispatch, cap 400.
Question it answers: is sayWhoaHim_v0x1FC (0x80108388) ever registered / its entry ever armed / fired in the port.
Idempotent; replayed from fixup_game_funcs_vendored.py for funcs_42.c."""
import re
TAG = "PATCH: s5693 handletable log"
_EN = ('static int s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } ')
def _reg():
    return ('    { static int s_n = 0; ' + _EN + 'if (s_e) { s_n++; if (s_n <= 300) fprintf(stderr, '
            '"[hreg] n=%d h=0x%X a1=0x%X a2=0x%X a3=0x%X sp10=0x%X ra=0x%X\\n", s_n, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), '
            '(unsigned)MEM_W(0x10, ctx->r29), U32(ctx->r31)); } } /* ' + TAG + ' */\n')
def _chk():
    return ('    { static int s_n = 0; ' + _EN + 'if (s_e) { s_n++; int act = 0; for (int i = 0; i < 48; i++) act += (MEM_BU(0xE + i*16 - 0x3920, 0xFFFFFFFF80110000ull) == 1); '
            'if (s_n <= 3 || (s_n % 1200) == 0) { fprintf(stderr, "[hchk] n=%d active=%d\\n", s_n, act); '
            'for (int i = 0; i < 48; i++) if (MEM_BU(0xE + i*16 - 0x3920, 0xFFFFFFFF80110000ull) == 1) fprintf(stderr, '
            '"[hent] n=%d i=%d h=0x%X b4=%u b5=%u b6=%u b7=%u w8=0x%X bC=%u bD=%u\\n", s_n, i, '
            '(unsigned)MEM_W(i*16 - 0x3920, 0xFFFFFFFF80110000ull), (unsigned)MEM_BU(4 + i*16 - 0x3920, 0xFFFFFFFF80110000ull), '
            '(unsigned)MEM_BU(5 + i*16 - 0x3920, 0xFFFFFFFF80110000ull), (unsigned)MEM_BU(6 + i*16 - 0x3920, 0xFFFFFFFF80110000ull), '
            '(unsigned)MEM_BU(7 + i*16 - 0x3920, 0xFFFFFFFF80110000ull), (unsigned)MEM_W(8 + i*16 - 0x3920, 0xFFFFFFFF80110000ull), '
            '(unsigned)MEM_BU(0xC + i*16 - 0x3920, 0xFFFFFFFF80110000ull), (unsigned)MEM_BU(0xD + i*16 - 0x3920, 0xFFFFFFFF80110000ull)); } } } /* ' + TAG + ' */\n')
def _fire():
    return ('    { static int s_n = 0; ' + _EN + 'if (s_e) { s_n++; if (s_n <= 400) fprintf(stderr, "[hfire] n=%d i=%d h=0x%X\\n", s_n, (int)U32(ctx->r18), U32(ctx->r2)); } } /* ' + TAG + ' */\n')
def apply(text):
    n = 0
    for fn, blk in (("addBooleanCountHandle", _reg()), ("checkObjectiveHandles", _chk())):
        i = text.find("RECOMP_FUNC void %s(" % fn)
        if i < 0 or TAG in text[i:i + 900]: continue
        j = text.find("{\n", i) + 2
        text = text[:j] + blk + text[j:]; n += 1
    anchor = "    ctx->r2 = MEM_W(ctx->r17, 0X0);\n    // 0x800FA0F0: jalr"
    k = text.find(anchor)
    if k >= 0 and TAG not in text[k:k + 900]:
        k2 = k + len("    ctx->r2 = MEM_W(ctx->r17, 0X0);\n")
        text = text[:k2] + _fire() + text[k2:]; n += 1
    return text, n
if __name__ == "__main__":
    import pathlib
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_42.c")
    t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print(p.name, n)
