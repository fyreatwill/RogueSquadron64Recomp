"""s5639: env-gated (ROGUESQ_LOG_HUDBIT=1) entry log, first 3 calls per function, for every recompiled function that
statically calls playObjectiveVoiceLine1 (funcs_45..48) plus runInMissionFrame (funcs_42, positive control).
Idempotent; replayed from fixup_game_funcs_vendored.py per file."""
import re
TAG = "PATCH: s5639 voicecaller log"
def apply(text, with_control):
    out, n = [], 0
    parts = re.split(r'(?m)^(?=RECOMP_FUNC void )', text)
    for part in parts:
        m = re.match(r'RECOMP_FUNC void (\w+)\(', part)
        if m and TAG not in part[:600] and (("playObjectiveVoiceLine1(rdram" in part) or (with_control and m.group(1) == "runInMissionFrame")):
            nm = m.group(1)
            blk = ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
                   'if (s_e) { extern long time(long*); s_n++; if (s_n <= 3 || (s_n %% 1000) == 0) '
                   'fprintf(stderr, "[vcaller] %s n=%%d a0=0x%%X t=%%ld\\n", s_n, U32(ctx->r4), (long)time(0)); } } /* %s */\n' % (nm, TAG))
            j = part.find("{\n") + 2
            part = part[:j] + blk + part[j:]; n += 1
        out.append(part)
    return "".join(out), n
if __name__ == "__main__":
    import pathlib
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    for f in ("funcs_42.c", "funcs_45.c", "funcs_46.c", "funcs_47.c", "funcs_48.c"):
        p = base / f; t = p.read_text(); t2, n = apply(t, f == "funcs_42.c")
        if n: p.write_text(t2)
        print(f, n)
