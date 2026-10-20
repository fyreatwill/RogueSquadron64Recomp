"""s5637: env-gated (ROGUESQ_LOG_HUDBIT=1) entry log for playObjectiveVoiceLine1 (0x800C7CF8) and sayWhoaHim_v0x1FC (0x80108388):
id=a0, ra=r31, caller-chain hint sp, wall time. Cap 400 each. Idempotent; replayed from fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "s5637 voiceline log"
def blk(name):
    return ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
            'if (s_e) { extern long time(long*); s_n++; if (s_n <= 400) '
            'fprintf(stderr, "[voiceln] %s call#%%d a0=0x%%X ra=0x%%X sp=0x%%X t=%%ld\\n", s_n, U32(ctx->r4), U32(ctx->r31), U32(ctx->r29), (long)time(0)); } } /* PATCH: s5637 voiceline log */\n' % name)
def apply(text, fn, name):
    if TAG in text.split("RECOMP_FUNC void %s(" % fn)[1][:1500] if ("RECOMP_FUNC void %s(" % fn) in text else True:
        return text, 0
    i = text.find("RECOMP_FUNC void %s(" % fn)
    j = text.find("{\n", i) + 2
    return text[:j] + blk(name) + text[j:], 1
if __name__ == "__main__":
    for f, fn in (("funcs_36.c", "playObjectiveVoiceLine1"), ("funcs_48.c", "sayWhoaHim_v0x1FC")):
        p = base / f; t = p.read_text(); t2, n = apply(t, fn, fn)
        if n: p.write_text(t2)
        print(f, fn, n)
