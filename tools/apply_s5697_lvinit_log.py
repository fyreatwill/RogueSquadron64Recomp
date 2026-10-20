"""s5697: env-gated (ROGUESQ_LOG_HUDBIT=1) entry log for every lvN_initializeObjectTracking (+ initMission as the
positive control): [lvinit] fn, ra (the caller's return address = names the level-table indexer), gCurrentLevel
(0x80130B70), B40 (0x80130B40), a0..a3. Question: which code calls the per-level init, and which global feeds its index.
Idempotent; replayed from fixup_game_funcs_vendored.py for the funcs_4x files."""
import re
TAG = "PATCH: s5697 lvinit log"
def _blk(name):
    # s5698: host C backtrace (execinfo) at first 2 entries names the recomp parent frame (ra is never set by recomp jal)
    return ('    { static int s_n = 0; static int s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
            'if (s_e && ++s_n <= 40) fprintf(stderr, "[lvinit] %s n=%d ra=0x%X gCurLevel=%u b40=%u a0=0x%X a1=0x%X a2=0x%X a3=0x%X\\n", "' + name +
            '", s_n, U32(ctx->r31), (unsigned)MEM_W(0xB70, 0xFFFFFFFF80130000ull), (unsigned)MEM_BU(0xB40, 0xFFFFFFFF80130000ull), '
            'U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); if (s_e && s_n <= 2) { void* bt[24]; int nb = backtrace(bt, 24); fprintf(stderr, "[lvinit-bt] %s\\n", "' + name + '"); backtrace_symbols_fd(bt, nb, 2); } } /* ' + TAG + ' */\n')
def apply(text):
    n = 0
    if "#include <execinfo.h>" not in text:
        text = text.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <execinfo.h>\n', 1)
    if TAG in text and "[lvinit-bt]" not in text:  # upgrade older log blocks in place
        text = re.sub(r"(    \{ static int s_n = 0; static int s_e = -1;[^\n]*\n)", lambda m: "", text) if False else text
        text = re.sub(r"U32\(ctx->r7\)\); \} /\* " + re.escape(TAG), lambda m: "U32(ctx->r7)); if (s_e && s_n <= 2) { void* bt[24]; int nb = backtrace(bt, 24); fprintf(stderr, \"[lvinit-bt]\\n\"); backtrace_symbols_fd(bt, nb, 2); } } /* " + TAG, text)
        n += 1
    for m in list(re.finditer(r'RECOMP_FUNC void ((?:lv[0-9a-k]_initializeObjectTracking)|initMission)\(', text)):
        pass
    for name in sorted(set(re.findall(r'RECOMP_FUNC void ((?:lv[0-9a-k]_initializeObjectTracking)|initMission)\(', text))):
        i = text.find("RECOMP_FUNC void %s(" % name)
        if TAG in text[i:i + 900]: continue
        j = text.find("{\n", i) + 2
        text = text[:j] + _blk(name) + text[j:]; n += 1
    return text, n
if __name__ == "__main__":
    import pathlib
    for f in ("funcs_42.c", "funcs_43.c", "funcs_44.c", "funcs_45.c", "funcs_46.c", "funcs_47.c", "funcs_48.c", "funcs_49.c"):
        p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs") / f
        t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        print(f, n)
